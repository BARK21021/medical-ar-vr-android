import os
import cv2
import numpy as np
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QSlider, QFrame, QMessageBox, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QFont, QPixmap, QImage


class VideoThread(QThread):
    frame_ready = pyqtSignal(np.ndarray)
    finished = pyqtSignal()

    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path
        self.running = False
        self.paused = False
        self.cap = None
        self.current_frame = 0
        self.total_frames = 0
        self.fps = 30

    def run(self):
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            self.finished.emit()
            return

        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
        self.running = True

        while self.running:
            if self.paused:
                self.msleep(50)
                continue

            ret, frame = self.cap.read()
            if not ret:
                self.finished.emit()
                break

            self.current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            self.frame_ready.emit(frame)
            self.msleep(int(1000 / self.fps))

        self.cap.release()

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def stop(self):
        self.running = False
        self.wait()

    def seek(self, frame_number):
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            self.current_frame = frame_number


class VideoPlayerWidget(QWidget):
    question_triggered = pyqtSignal(dict)
    video_completed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.video_data = None
        self.questions_asked = set()
        self.is_playing = False
        self.current_frame = 0
        self.total_frames = 0
        self.fps = 30
        self.current_segment_index = 0
        self.video_thread = None
        self.original_pixmap = None

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.video_display = QLabel()
        self.video_display.setAlignment(Qt.AlignCenter)
        self.video_display.setMinimumHeight(300)
        self.video_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_display.setStyleSheet("""
            QLabel {
                background-color: #0a0a1a;
                border: 3px solid #0f3460;
                border-radius: 12px;
            }
        """)
        self.video_display.setText("📀 视频播放区域\n\n请选择视频片段开始学习")
        self.video_display.setFont(QFont("Microsoft YaHei", 16))

        layout.addWidget(self.video_display, 1)

        self._create_controls(layout)
        self._create_info_panel(layout)
        layout.setStretch(0, 6)
        layout.setStretch(1, 0)
        layout.setStretch(2, 0)

    def _create_controls(self, layout):
        controls_frame = QFrame()
        controls_frame.setStyleSheet("""
            QFrame {
                background-color: #16213e;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        controls_layout = QVBoxLayout(controls_frame)
        controls_layout.setSpacing(8)

        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setRange(0, 1000)
        self.progress_slider.setValue(0)
        self.progress_slider.sliderPressed.connect(self._on_slider_pressed)
        self.progress_slider.sliderReleased.connect(self._on_slider_released)
        self.progress_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 10px;
                background: #0f3460;
                border-radius: 5px;
            }
            QSlider::handle:horizontal {
                background: #e94560;
                width: 20px;
                margin: -5px 0;
                border-radius: 10px;
            }
            QSlider::sub-page:horizontal {
                background: #e94560;
                border-radius: 5px;
            }
        """)
        self.slider_is_pressed = False
        controls_layout.addWidget(self.progress_slider)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.play_btn = QPushButton("▶ 播放")
        self.play_btn.setFont(QFont("Microsoft YaHei", 12))
        self.play_btn.clicked.connect(self._toggle_play)
        self.play_btn.setMinimumWidth(100)

        self.stop_btn = QPushButton("⏹ 停止")
        self.stop_btn.setFont(QFont("Microsoft YaHei", 12))
        self.stop_btn.clicked.connect(self.stop_video)
        self.stop_btn.setMinimumWidth(100)

        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setFont(QFont("Microsoft YaHei", 12))
        self.time_label.setStyleSheet("color: #eaeaea;")

        buttons_layout.addWidget(self.play_btn)
        buttons_layout.addWidget(self.stop_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.time_label)

        controls_layout.addLayout(buttons_layout)
        layout.addWidget(controls_frame)

    def _create_info_panel(self, layout):
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #0f3460;
                border-radius: 10px;
                padding: 12px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(8)

        self.title_label = QLabel("📽 请选择视频片段")
        self.title_label.setFont(QFont("Microsoft YaHei", 13, QFont.Bold))
        self.title_label.setStyleSheet("color: #e94560;")

        self.question_info_label = QLabel("")
        self.question_info_label.setFont(QFont("Microsoft YaHei", 11))
        self.question_info_label.setStyleSheet("color: #eaeaea;")

        info_layout.addWidget(self.title_label)
        info_layout.addWidget(self.question_info_label)

        segments_label = QLabel("🎬 选择视频片段：")
        segments_label.setFont(QFont("Microsoft YaHei", 11))
        segments_label.setStyleSheet("color: #888888;")
        info_layout.addWidget(segments_label)

        self.segments_btn_layout = QHBoxLayout()
        self.segments_btn_layout.setSpacing(8)
        info_layout.addLayout(self.segments_btn_layout)

        layout.addWidget(info_frame)

    def load_video(self, video_data):
        self.video_data = video_data
        self.questions_asked.clear()
        self.current_segment_index = 0
        self.original_pixmap = None
        self.video_display.setPixmap(QPixmap())
        self.video_display.setText("📀 请选择视频片段\n\n开始学习")
        self._update_segments_buttons()
        self._update_title()

    def _update_title(self):
        if self.video_data:
            self.title_label.setText(f"📽 {self.video_data.get('title', '未知视频')}")

    def _update_segments_buttons(self):
        while self.segments_btn_layout.count():
            item = self.segments_btn_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.video_data:
            return

        segments = self.video_data.get('video_segments', [])
        for i in range(len(segments)):
            btn = QPushButton(f"片段{i+1}")
            btn.setFont(QFont("Microsoft YaHei", 11))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #16213e;
                    border: 2px solid #0f3460;
                    border-radius: 6px;
                    padding: 8px 16px;
                    color: #eaeaea;
                }
                QPushButton:hover {
                    background-color: #0f3460;
                    border-color: #e94560;
                }
                QPushButton:checked {
                    background-color: #e94560;
                    border-color: #e94560;
                }
            """)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, idx=i: self._play_segment(idx))
            self.segments_btn_layout.addWidget(btn)

        if segments:
            self.segments_btn_layout.itemAt(0).widget().setChecked(True)

    def _play_segment(self, segment_index):
        self.stop_video()
        self.current_segment_index = segment_index
        self.questions_asked.discard(segment_index)

        segments = self.video_data.get('video_segments', [])
        if segment_index >= len(segments):
            return

        segment = segments[segment_index]
        video_path = segment.get('video_file', '')

        if video_path and os.path.exists(video_path):
            self._start_video_thread(video_path)
            has_q = segment.get('has_question', False)
            desc = segment.get('description', '') if not has_q else ''
            status = "✅ 有交互问题" if has_q else f"ℹ️ 无问题 - {desc}"
            self.question_info_label.setText(
                f"片段 {segment_index + 1}/{len(segments)} | {segment.get('time_display', '')}\n"
                f"正在播放... | {status}"
            )

    def _start_video_thread(self, video_path):
        if self.video_thread:
            self.video_thread.stop()

        self.video_thread = VideoThread(video_path)
        self.video_thread.frame_ready.connect(self._on_frame_ready)
        self.video_thread.finished.connect(self._on_video_finished)
        self.video_thread.start()
        self.is_playing = True
        self.play_btn.setText("⏸ 暂停")

    def _display_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        q_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

        self.original_pixmap = QPixmap.fromImage(q_image)
        self.video_display.setText("")
        self._update_video_display()

    def _update_video_display(self):
        if not self.original_pixmap or self.original_pixmap.isNull():
            return
        scaled_pixmap = self.original_pixmap.scaled(
            self.video_display.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.video_display.setPixmap(scaled_pixmap)

    @pyqtSlot(np.ndarray)
    def _on_frame_ready(self, frame):
        self.current_frame = self.video_thread.current_frame if self.video_thread else 0
        self._display_frame(frame)
        if not self.slider_is_pressed and self.video_thread:
            progress = int((self.current_frame / self.video_thread.total_frames) * 1000) if self.video_thread.total_frames > 0 else 0
            self.progress_slider.setValue(progress)
        self._update_time_display()

    def _on_video_finished(self):
        self.is_playing = False
        self.play_btn.setText("▶ 播放")

        segments = self.video_data.get('video_segments', [])
        if self.current_segment_index < len(segments):
            segment = segments[self.current_segment_index]
            if segment.get('has_question', False) and self.current_segment_index not in self.questions_asked:
                self.questions_asked.add(self.current_segment_index)
                self.question_triggered.emit(segment)
        
    def _toggle_play(self):
        if self.is_playing:
            self.pause_video()
        else:
            self.resume_video()

    def pause_video(self):
        if self.video_thread:
            self.video_thread.pause()
        self.is_playing = False
        self.play_btn.setText("▶ 播放")

    def resume_video(self):
        if self.video_thread:
            self.video_thread.resume()
        self.is_playing = True
        self.play_btn.setText("⏸ 暂停")

    def stop_video(self):
        if self.video_thread:
            self.video_thread.stop()
            self.video_thread = None
        self.is_playing = False
        self.play_btn.setText("▶ 播放")
        self.current_frame = 0
        self.original_pixmap = None
        self.progress_slider.setValue(0)
        if self.video_data:
            self.video_display.setPixmap(QPixmap())
            self.video_display.setText("📀 请选择视频片段\n\n开始学习")

    def _on_slider_pressed(self):
        self.slider_is_pressed = True
        if self.video_thread:
            self.video_thread.pause()

    def _on_slider_released(self):
        self.slider_is_pressed = False
        if self.video_thread and self.video_thread.total_frames > 0:
            value = self.progress_slider.value()
            frame_number = int((value / 1000) * self.video_thread.total_frames)
            self.video_thread.seek(frame_number)
            if self.is_playing:
                self.video_thread.resume()

    def _update_time_display(self):
        if self.video_thread:
            current_seconds = int(self.current_frame / self.video_thread.fps) if self.video_thread.fps > 0 else 0
            total_seconds = int(self.video_thread.total_frames / self.video_thread.fps) if self.video_thread.fps > 0 else 0
        else:
            current_seconds = 0
            total_seconds = 0
        current_mins = current_seconds // 60
        current_secs = current_seconds % 60
        total_mins = total_seconds // 60
        total_secs = total_seconds % 60
        self.time_label.setText(f"⏱{current_mins:02d}:{current_secs:02d} / {total_mins:02d}:{total_secs:02d}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_video_display()
