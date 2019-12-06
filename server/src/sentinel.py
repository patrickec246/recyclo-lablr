import json
import logging
import threading

from settings import stats

from utils import *
from frame_processor import *

class TaskTimer(threading.Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

class ServerSentinel(object):
    def __init__(self):
        self.label_threshold = 5
        self.max_unlabeled_imgs = 30
        self.max_frames_per_pass = 10

        self.video_cleanup_rate = 20
        self.frame_cleanup_rate = 10
        self.process_video_rate = 5
        self.update_stats_rate = 5

    def run(self):
        self.video_cleanup_task = TaskTimer(self.video_cleanup_rate, self.video_cleanup_sentinel)
        self.video_cleanup_task.daemon = True
        self.frame_cleanup_task = TaskTimer(self.frame_cleanup_rate, self.frame_cleanup_sentinel)
        self.frame_cleanup_task.daemon = True
        self.process_video_task = TaskTimer(self.process_video_rate, self.process_video_sentinel)
        self.process_video_task.daemon = True
        self.update_stats_task = TaskTimer(self.update_stats_rate, self.update_stats)
        self.update_stats_task.daemon = True

        self.video_cleanup_task.start()
        self.frame_cleanup_task.start()
        self.process_video_task.start()
        self.update_stats_task.start()

    def stop(self):
        if self.video_cleanup_task:
            self.video_cleanup_task.cancel()
        if self.frame_cleanup_task:
            self.frame_cleanup_task.cancel()
        if self.process_video_task:
            self.process_video_task.cancel()
        if self.update_stats_task:
            self.update_stats_task.cancel()

    def video_cleanup_sentinel(self):
        cleanup_completed_videos()

    def frame_cleanup_sentinel(self):
        complete_saturated_frames(self.label_threshold)

    def process_video_sentinel(self):
        if available_frames() < self.max_unlabeled_imgs:
            log('Generating more frames to fill space')
            process_video(pick_random_video())

    def update_stats(self):
        save_labeled_stats(stats.frames_labeled, stats.total_labels)
