import os
os.system("pip install --upgrade pip")

import streamlit as st
import cv2
import numpy as np
import threading

# Change to a video file like "sample_video.mp4" if no webcam is available
VIDEO_SOURCE = 0  # or "sample_video.mp4"

class CameraThread(threading.Thread):
    def __init__(self, name='CameraThread'):
        super().__init__(name=name, daemon=True)
        self.stop_event = False
        self._frame = np.zeros((480, 640, 3), dtype=np.uint8)
        self.lock = threading.Lock()
        self.webcam = None  # Initialize here, but open later

    def run(self):
        self.webcam = cv2.VideoCapture(VIDEO_SOURCE)  # ✅ Open camera/video inside the thread
        while not self.stop_event:
            ret, img = self.webcam.read()
            if not ret:
                self.webcam.release()
                self.webcam = cv2.VideoCapture(VIDEO_SOURCE)
                continue
            with self.lock:
                self._frame = img.copy()

    def stop(self):
        self.stop_event = True
        if self.webcam:
            self.webcam.release()

    def read(self):
        with self.lock:
            return self._frame.copy()

@st.cache_resource
def get_or_create_camera_thread():
    # Stop any previously running thread (for hot-reloading)
    for th in threading.enumerate():
        if th.name == 'CameraThread':
            th.stop()
            th.join()
    cam_thread = CameraThread('CameraThread')
    cam_thread.start()
    return cam_thread

# Streamlit app
st.title("Security Camera Feed")

camera = get_or_create_camera_thread()
frame_placeholder = st.empty()

while True:
    frame = camera.read()
    frame_placeholder.image(frame, channels="BGR")
