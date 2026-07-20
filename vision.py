import time
from typing import Dict, List, Tuple
import cv2
import numpy as np

import supervision as sv
from detections import DetectionsManager
from ultralytics import YOLO
from threading import Thread, Lock

ZONE_IN_POLIGONS = [
    np.array([[472, 476], [934, 468], [930, 576], [301, 556]], dtype=np.int32),
    np.array([[978, 778], [1919, 765], [1916, 951], [985, 956]], dtype=np.int32),
]

ZONE_OUT_POLIGONS = [
    np.array([[-1, 746], [920, 765], [871, 966], [-1, 939]], dtype=np.int32),
    np.array([[978, 473], [976, 573], [1451, 507], [1324, 458]], dtype=np.int32),
]

COUNTER_ZONE = np.array(
    [[267, 373], [463, 317], [347, 193], [247, 213], [273, 381]], dtype=np.int32
)

COLORS = sv.ColorPalette.default()


def initiate_polygon_zones(
    polygons: List[np.ndarray],
    frame_resolution_wh: Tuple[int, int],
    triggering_position: sv.Position = sv.Position.CENTER,
) -> List[sv.PolygonZone]:
    return [
        sv.PolygonZone(
            polygon=polygon,
            frame_resolution_wh=frame_resolution_wh,
            triggering_position=triggering_position,
        )
        for polygon in polygons
    ]


class VideoCamera(object):
    def __init__(self, video_url, is_rtsp=False, reconnect_interval=5):
        self.video_url = video_url
        self.is_rtsp = is_rtsp
        self.reconnect_interval = reconnect_interval
        self.video = None
        self.fps = 0
        self.wt = 0
        self.stopped = False
        self.frame = None
        self.lock = Lock()
        self.connect()

        if self.is_rtsp:
            self.thread = Thread(target=self._rtsp_stream, daemon=True)
            self.thread.start()

    def __del__(self):
        self.stop()

    def connect(self):
        self.video = cv2.VideoCapture(self.video_url)
        if not self.video.isOpened():
            return False

        self.fps = self.video.get(cv2.CAP_PROP_FPS)
        self.wt = (
            1 / self.fps if self.fps > 0 else 0.033
        )  # Default to 30 FPS if unable to determine
        return True

    def stop(self):
        self.stopped = True
        if self.video:
            self.video.release()

    def _rtsp_stream(self):
        while not self.stopped:
            if not self.video or not self.video.isOpened():
                if not self.connect():
                    time.sleep(self.reconnect_interval)
                    continue

            success, image = self.video.read()
            if success:
                with self.lock:
                    self.frame = image
            else:
                self.video.release()
                time.sleep(self.reconnect_interval)

            time.sleep(self.wt)

    def get_frame(self):
        if self.is_rtsp:
            with self.lock:
                return self.frame
        else:
            if not self.video or not self.video.isOpened():
                if not self.connect():
                    return None

            success, image = self.video.read()
            if not success:
                self.video.release()
                if not self.connect():
                    return None
                success, image = self.video.read()

            return image if success else None


class VideoProcessor:
    def __init__(
        self,
        source_weights_path: str,
        source_video_path: str,
        target_video_path: str = None,
        confidence_threshold: float = 0.3,
        iou_threshold: float = 0.7,
        zone_in_polygons: List[np.ndarray] = ZONE_IN_POLIGONS,
        zone_out_polygons: List[np.ndarray] = ZONE_OUT_POLIGONS,
        counter_zone: np.ndarray = COUNTER_ZONE,
        is_rtsp=False,
    ) -> None:
        self.source_weights_path = source_weights_path
        self.source_video_path = source_video_path
        self.target_video_path = target_video_path
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.is_rtsp = is_rtsp
        self.video_info = sv.VideoInfo.from_video_path(self.source_video_path)
        self.zone_in = initiate_polygon_zones(
            polygons=zone_in_polygons,
            frame_resolution_wh=self.video_info.resolution_wh,
            triggering_position=sv.Position.CENTER,
        )

        self.zone_out = initiate_polygon_zones(
            polygons=zone_out_polygons,
            frame_resolution_wh=self.video_info.resolution_wh,
            triggering_position=sv.Position.CENTER,
        )

        self.counter_zone = initiate_polygon_zones(
            polygons=[counter_zone],
            frame_resolution_wh=self.video_info.resolution_wh,
            triggering_position=sv.Position.CENTER,
        )[0]

        self.model = YOLO(
            model=self.source_weights_path,
        )
        self.detections_manager = DetectionsManager()

        self.tracker = sv.ByteTrack()
        self.box_annotator = sv.BoxAnnotator(color=COLORS)
        self.trace_annotator = sv.TraceAnnotator(
            color=COLORS, trace_length=100, thickness=2
        )
        self.current_frame = None
        self.fps = self.video_info.fps
        self.real_fps = self.fps
        self.wt = 1 / self.fps
        self.frame_count = 0
        self.cam = VideoCamera(self.source_video_path)
        self.vehicle_count = {}

    def process_video(self):
        if not self.is_rtsp:
            frame_generator = sv.get_video_frames_generator(
                source_path=self.source_video_path,
            )

        prev_frame_time = 0
        new_frame_time = 0
        if self.is_rtsp:
            while True:
                frame = self.cam.get_frame()
                if frame is None:
                    continue
                processed_frame = self.process_frame(frame)
                new_frame_time = time.time()
                self.real_fps = 1 / (new_frame_time - prev_frame_time)
                prev_frame_time = new_frame_time
                self.current_frame = frame
                self.frame_count += 1
                yield processed_frame
        else:
            for frame in frame_generator:
                processed_frame = self.process_frame(frame)
                new_frame_time = time.time()
                self.real_fps = 1 / (new_frame_time - prev_frame_time)
                prev_frame_time = new_frame_time
                self.current_frame = frame
                self.frame_count += 1
                yield processed_frame

    def annotate_frame(
        self, frame: np.ndarray, detections: sv.Detections
    ) -> np.ndarray:
        annotated_frame = frame.copy()

        for i, (zone_in, zone_out) in enumerate(zip(self.zone_in, self.zone_out)):
            annotated_frame = sv.draw_polygon(
                scene=annotated_frame,
                polygon=zone_in.polygon,
                color=COLORS.colors[i],
            )
            annotated_frame = sv.draw_polygon(
                scene=annotated_frame,
                polygon=zone_out.polygon,
                color=COLORS.colors[i],
            )

        labels = [f"#{tracker_id}" for tracker_id in detections.tracker_id]
        for zone in self.detections_manager.counter_time:
            for tracker_id in self.detections_manager.counter_time[zone]["trackers_id"]:
                try:
                    tracker_idx = labels.index(f"#{tracker_id}")
                except ValueError:
                    continue
                labels[tracker_idx] = (
                    f"#{tracker_id} - {self.detections_manager.counter_time[zone]['trackers_id'][tracker_id]['elapsed_time']} - {self.detections_manager.counter_time[zone]['trackers_id'][tracker_id].get('speed', 0)}"
                )

        annotated_frame = self.box_annotator.annotate(
            annotated_frame, detections, labels=labels
        )

        annotated_frame = self.trace_annotator.annotate(annotated_frame, detections)

        for zone_out_id, zone_out in enumerate(self.zone_out):
            zone_center = sv.get_polygon_center(zone_out.polygon)
            if zone_out_id in self.detections_manager.recorded_paths:
                paths = self.detections_manager.recorded_paths[zone_out_id]
                for i, zone_in_id in enumerate(paths):
                    count = len(paths[zone_in_id])
                    text_anchor = sv.Point(x=zone_center.x, y=zone_center.y + 50 * i)
                    annotated_frame = sv.draw_text(
                        scene=annotated_frame,
                        text=f"Zone {zone_out_id} -> {zone_in_id}: {count}",
                        text_anchor=text_anchor,
                        background_color=COLORS.colors[zone_in_id],
                    )
                    self.vehicle_count[zone_out_id] = count

        # draw average time in out zone
        for zone_id in self.detections_manager.counter_time:
            zone_center = sv.get_polygon_center(self.zone_out[zone_id].polygon)
            average_time = self.detections_manager.counter_time[zone_id]["average_time"]
            text_anchor = sv.Point(x=zone_center.x, y=zone_center.y - 50)
            annotated_frame = sv.draw_text(
                scene=annotated_frame,
                text=f"Average time in zone {zone_id}: {average_time}",
                text_anchor=text_anchor,
                background_color=COLORS.colors[zone_id],
            )
        # draw counter zone
        if self.counter_zone is not None:
            annotated_frame = sv.draw_polygon(
                scene=annotated_frame,
                polygon=self.counter_zone.polygon,
                color=COLORS.colors[-1],
            )

        # draw real wait time in center of counter zone
        for i, zone_in_id in enumerate(self.detections_manager.counter_time):
            zone_center = sv.get_polygon_center(self.counter_zone.polygon)
            elapsed_time = self.detections_manager.counter_time[zone_in_id][
                "real_waiting_time"
            ]

            text_anchor = sv.Point(x=zone_center.x, y=zone_center.y + 50 * i)
            annotated_frame = sv.draw_text(
                scene=annotated_frame,
                text=f"Zone {zone_in_id}: {elapsed_time}",
                text_anchor=text_anchor,
                background_color=COLORS.colors[zone_in_id],
            )

        # display real fps
        text_anchor = sv.Point(x=100, y=50)
        annotated_frame = sv.draw_text(
            scene=annotated_frame,
            text=f"Real FPS: {int(self.real_fps)} / {self.fps}",
            text_anchor=text_anchor,
            background_color=COLORS.colors[-1],
        )

        return annotated_frame

    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        result = self.model(
            frame, verbose=False, conf=self.confidence_threshold, iou=self.iou_threshold
        )[0]
        detections = sv.Detections.from_ultralytics(result)
        detections = self.tracker.update_with_detections(detections)

        detections_zones_in = []
        detections_zones_out = []

        for zone_in, zone_out in zip(self.zone_in, self.zone_out):
            detections_zone_in = detections[zone_in.trigger(detections)]
            detections_zones_in.append(detections_zone_in)
            detections_zone_out = detections[zone_out.trigger(detections)]
            detections_zones_out.append(detections_zone_out)

        detections_counter = detections[self.counter_zone.trigger(detections)]
        detections = self.detections_manager.update(
            detections=detections,
            detections_zones_in=detections_zones_in,
            detections_zones_out=detections_zones_out,
        )

        self.detections_manager.counter_zone_update(
            detections=detections,
            detections_counter_zone=detections_counter,
            real_fps=self.fps,
            processed_fps=self.real_fps,
        )

        annotated_frame = self.annotate_frame(frame, detections)
        return annotated_frame

    def get_traffic_conclusion(self, travel_time):
        if travel_time < 5:
            return "Lancar"
        elif travel_time < 10:
            return "Pelan"
        else:
            return "Macet"

    def get_traffic_conclusion_level(self, travel_time):
        if travel_time < 5:
            return 0
        elif travel_time < 10:
            return 1
        else:
            return 2

    def summary(self) -> Dict:
        traffic_conclusion = self.detections_manager.counter_time.get(
            0,
            {
                "real_waiting_time": 0,
                "average_time": 0,
            },
        )
        return {
            "real_fps": self.real_fps,
            "fps": self.fps,
            "frame_count": self.frame_count,
            "traffic_conclusion": self.get_traffic_conclusion(
                traffic_conclusion["real_waiting_time"]
            ),
            "average_time": traffic_conclusion["average_time"],
            "real_waiting_time": traffic_conclusion["real_waiting_time"],
            "vehicle_count": self.vehicle_count,
            "traffic_conclusion_level": self.get_traffic_conclusion_level(
                traffic_conclusion["real_waiting_time"]
            ),
        }
