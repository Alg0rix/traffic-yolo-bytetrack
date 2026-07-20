from vision import VideoProcessor


class VideoProcessorManager:
    def __init__(self):
        self.video = None
        self.config = None

    def init(
        self,
        source_weights_path,
        source_video_path,
        target_video_path,
        confidence_threshold,
        iou_threshold,
        zone_in_polygons,
        zone_out_polygons,
        counter_zone_polygons,
        config,
        is_rtsp=False,
    ):
        self.video = VideoProcessor(
            source_weights_path=source_weights_path,
            source_video_path=source_video_path,
            target_video_path=target_video_path,
            confidence_threshold=confidence_threshold,
            iou_threshold=iou_threshold,
            zone_in_polygons=zone_in_polygons,
            zone_out_polygons=zone_out_polygons,
            counter_zone=counter_zone_polygons,
            is_rtsp=is_rtsp,
        )
        self.config = config

    @property
    def summary(self):
        return self.video.summary()


video_processor_manager = VideoProcessorManager()
