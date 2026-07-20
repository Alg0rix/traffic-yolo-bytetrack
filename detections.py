from typing import Dict, List
import numpy as np
import supervision as sv
from datetime import datetime


class DetectionsManager:
    def __init__(self) -> None:
        self.tracker_id_to_zone_id: Dict[int, int] = {}
        self.recorded_paths = {}
        self.counter_time = {}

    def update(
        self,
        detections: sv.Detections,
        detections_zones_in: List[sv.Detections],
        detections_zones_out: List[sv.Detections],
    ) -> sv.Detections:
        for zone_in_id, detections_zone_in in enumerate(detections_zones_in):
            for tracker_id in detections_zone_in.tracker_id:
                self.tracker_id_to_zone_id.setdefault(tracker_id, zone_in_id)

        for zone_out_id, detections_zone_out in enumerate(detections_zones_out):
            for tracker_id in detections_zone_out.tracker_id:
                if tracker_id in self.tracker_id_to_zone_id:
                    zone_in_id = self.tracker_id_to_zone_id[tracker_id]
                    self.recorded_paths.setdefault(zone_in_id, {})
                    self.recorded_paths[zone_out_id].setdefault(zone_in_id, set())
                    self.recorded_paths[zone_out_id][zone_in_id].add(tracker_id)

        if len(detections.tracker_id) > 0:
            detections.class_id = np.vectorize(
                lambda x: self.tracker_id_to_zone_id.get(x, -1)
            )(detections.tracker_id)

        detections = detections[detections.class_id != -1]
        return detections

    def counter_zone_update(
        self,
        detections: sv.Detections,
        detections_counter_zone: List[sv.Detections],
        real_fps: float,
        processed_fps: float,
    ) -> sv.Detections:
        fps_ratio = real_fps / processed_fps
        current_time = datetime.now()
        for tracker_id in detections_counter_zone.tracker_id:
            if tracker_id in self.tracker_id_to_zone_id:
                zone_in_id = self.tracker_id_to_zone_id[tracker_id]
                self.counter_time.setdefault(
                    zone_in_id,
                    {"trackers_id": {}, "updated_at": current_time, "average_time": 0},
                )
                self.counter_time[zone_in_id]["trackers_id"].setdefault(
                    tracker_id,
                    {
                        "start_time": current_time,
                        "elapsed_time": 0,
                        "updated_at": current_time,
                    },
                )
                elapsed_time_real_fps = (
                    current_time
                    - self.counter_time[zone_in_id]["trackers_id"][tracker_id][
                        "start_time"
                    ]
                ).total_seconds()
                elapsed_time = elapsed_time_real_fps / fps_ratio
                self.counter_time[zone_in_id]["trackers_id"][tracker_id][
                    "elapsed_time"
                ] = round(elapsed_time, 2)
                self.counter_time[zone_in_id]["trackers_id"][tracker_id][
                    "updated_at"
                ] = current_time
                self.counter_time[zone_in_id]["updated_at"] = current_time

        self.calculate_real_waiting_time(2)
        outdated_trackers = self.find_outdated_trackers(current_time, 15)
        self.remove_outdated_trackers(outdated_trackers)
        self.calculate_average_time()
        self.estimate_vehicle_speed()

    def calculate_average_time(self):
        for zone_id in self.counter_time:
            self.counter_time[zone_id]["average_time"] = (
                round(
                    np.mean(
                        [
                            self.counter_time[zone_id]["trackers_id"][tracker_id][
                                "elapsed_time"
                            ]
                            for tracker_id in self.counter_time[zone_id]["trackers_id"]
                        ]
                    ),
                    2,
                )
                if len(self.counter_time[zone_id]["trackers_id"]) > 0
                else 0
            )

    def find_outdated_trackers(self, current_time: datetime, timeout: int):
        outdated_trackers = []
        for zone_id in self.counter_time:
            if (
                current_time - self.counter_time[zone_id]["updated_at"]
            ).total_seconds() > timeout:
                outdated_trackers.extend(
                    [
                        tracker_id
                        for tracker_id in self.counter_time[zone_id]["trackers_id"]
                    ]
                )
        return outdated_trackers

    def remove_outdated_trackers(self, outdated_trackers: List[int]):
        for zone_id in self.counter_time:
            self.counter_time[zone_id]["trackers_id"] = {
                tracker_id: self.counter_time[zone_id]["trackers_id"][tracker_id]
                for tracker_id in self.counter_time[zone_id]["trackers_id"]
                if tracker_id not in outdated_trackers
            }

    def calculate_real_waiting_time(self, timeout: int = 1):
        # calculate real waiting time by find the highest elapsed time and ignore update_at
        current_time = datetime.now()

        for zone in self.counter_time:
            # sort by newest updated_at
            trackers = sorted(
                self.counter_time[zone]["trackers_id"].items(),
                key=lambda x: x[1]["updated_at"],
                reverse=True,
            )

            # remove outdated trackers

            trackers = [
                tracker
                for tracker in trackers
                if (current_time - tracker[1]["updated_at"]).total_seconds() < timeout
            ]

            # find highest elapsed time
            if len(trackers) > 0:
                highest_elapsed_time = max(
                    [tracker[1]["elapsed_time"] for tracker in trackers]
                )
                self.counter_time[zone]["real_waiting_time"] = highest_elapsed_time
            else:
                self.counter_time[zone]["real_waiting_time"] = 0

    def estimate_vehicle_speed(self):
        for zone_out_id in self.recorded_paths:
            for zone_in_id in self.recorded_paths[zone_out_id]:
                for tracker_id in self.recorded_paths[zone_out_id][zone_in_id]:
                    if tracker_id in self.counter_time.get(zone_in_id, {}).get(
                        "trackers_id", {}
                    ):
                        elapsed_time = self.counter_time[zone_in_id]["trackers_id"][
                            tracker_id
                        ]["elapsed_time"]
                        if elapsed_time > 0:
                            speed = round(
                                3.6 * 20 / elapsed_time,
                                2,
                            )
                            self.counter_time[zone_in_id]["trackers_id"][tracker_id][
                                "speed"
                            ] = speed
