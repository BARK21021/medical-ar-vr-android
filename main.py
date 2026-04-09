import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QStackedWidget,
                             QFrame, QMessageBox, QProgressBar, QScrollArea)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap, QPainter, QPen, QColor
import json

from video_player import VideoPlayerWidget
from question_dialog import QuestionDialog
from data_manager import VideoDataManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("医学AR+VR学术教程系统")
        self.setMinimumSize(1000, 750)
        self.resize(1300, 850)
        self.setStyleSheet(self._get_stylesheet())
        
        self.data_manager = VideoDataManager()
        self.current_video_index = -1
        self.completed_videos = set()
        self.video_progress = {}
        
        self._init_ui()
        
    def _get_stylesheet(self):
        return """
            QMainWindow {
                background-color: #1a1a2e;
            }
            QLabel {
                color: #eaeaea;
            }
            QPushButton {
                background-color: #16213e;
                color: #eaeaea;
                border: 2px solid #0f3460;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #0f3460;
                border-color: #e94560;
            }
            QPushButton:pressed {
                background-color: #e94560;
            }
            QPushButton:disabled {
                background-color: #2d2d44;
                color: #666666;
                border-color: #333344;
            }
            QFrame {
                background-color: #16213e;
                border-radius: 12px;
            }
            QProgressBar {
                border: 2px solid #0f3460;
                border-radius: 5px;
                text-align: center;
                color: #eaeaea;
            }
            QProgressBar::chunk {
                background-color: #e94560;
                border-radius: 3px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """
        
    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(25, 20, 25, 20)
        self.main_layout.setSpacing(15)
        
        self._create_header()
        self._create_content_stack()
        self._create_footer()
        
    def _create_header(self):
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        header_layout.setSpacing(5)
        
        title_label = QLabel("🏥 医学AR+VR学术教程系统")
        title_label.setFont(QFont("Microsoft YaHei", 26, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #e94560;")
        
        subtitle_label = QLabel("交互式医学手术视频学习平台")
        subtitle_label.setFont(QFont("Microsoft YaHei", 13))
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #888888;")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        self.main_layout.addWidget(header_frame)
        
    def _create_content_stack(self):
        self.content_stack = QStackedWidget()
        
        self._create_video_selection_page()
        self._create_video_player_page()
        
        self.main_layout.addWidget(self.content_stack, 1)
        
    def _create_video_selection_page(self):
        selection_page = QWidget()
        layout = QVBoxLayout(selection_page)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)
        
        instruction_label = QLabel("📚 请选择要学习的视频教程：")
        instruction_label.setFont(QFont("Microsoft YaHei", 15))
        instruction_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(instruction_label)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        scroll_content = QWidget()
        videos_layout = QVBoxLayout(scroll_content)
        videos_layout.setSpacing(12)
        videos_layout.setContentsMargins(5, 5, 5, 5)
        
        self.video_buttons = []
        videos = self.data_manager.get_all_videos()
        
        for i, video in enumerate(videos):
            video_frame = QFrame()
            video_frame.setStyleSheet("""
                QFrame {
                    background-color: #16213e;
                    border-radius: 10px;
                    border: 1px solid #0f3460;
                }
                QFrame:hover {
                    border: 2px solid #e94560;
                }
            """)
            video_layout = QHBoxLayout(video_frame)
            video_layout.setContentsMargins(15, 10, 15, 10)
            
            thumbnail_label = QLabel()
            thumbnail_path = video.get('thumbnail', '')
            if thumbnail_path and os.path.exists(thumbnail_path):
                pixmap = QPixmap(thumbnail_path)
                thumbnail_label.setPixmap(pixmap.scaled(80, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                thumbnail_label.setText("📹")
                thumbnail_label.setFont(QFont("Microsoft YaHei", 24))
                thumbnail_label.setStyleSheet("color: #e94560;")
            thumbnail_label.setFixedSize(90, 70)
            video_layout.addWidget(thumbnail_label)
            
            info_layout = QVBoxLayout()
            
            title_btn = QPushButton(f"  {video['title']}")
            title_btn.setFont(QFont("Microsoft YaHei", 13, QFont.Bold))
            title_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    text-align: left;
                    color: #eaeaea;
                }
                QPushButton:hover {
                    color: #e94560;
                }
            """)
            title_btn.clicked.connect(lambda checked, idx=i: self._start_video(idx))
            
            segments = video.get('video_segments', [])
            question_count = sum(1 for s in segments if s.get('has_question', False))
            info_text = f"📝 {question_count} 道问题 | 🎬 {len(segments)} 个片段"
            info_label = QLabel(info_text)
            info_label.setFont(QFont("Microsoft YaHei", 11))
            info_label.setStyleSheet("color: #888888;")
            
            info_layout.addWidget(title_btn)
            info_layout.addWidget(info_label)
            
            video_layout.addLayout(info_layout, 1)
            
            play_icon = QLabel("▶")
            play_icon.setFont(QFont("Microsoft YaHei", 18))
            play_icon.setStyleSheet("color: #e94560;")
            play_icon.setFixedWidth(30)
            video_layout.addWidget(play_icon)
            
            videos_layout.addWidget(video_frame)
            self.video_buttons.append(title_btn)
            
        videos_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        self.content_stack.addWidget(selection_page)
        
    def _create_video_player_page(self):
        self.player_page = QWidget()
        player_layout = QVBoxLayout(self.player_page)
        player_layout.setContentsMargins(0, 0, 0, 0)
        player_layout.setSpacing(0)

        player_scroll = QScrollArea()
        player_scroll.setWidgetResizable(True)
        player_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        player_content = QWidget()
        content_layout = QVBoxLayout(player_content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)

        top_bar = QFrame()
        top_bar.setStyleSheet("background-color: #16213e; border-radius: 8px;")
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(15, 8, 15, 8)
        
        back_btn = QPushButton("← 返回列表")
        back_btn.setFont(QFont("Microsoft YaHei", 11))
        back_btn.setMaximumWidth(120)
        back_btn.clicked.connect(self._return_to_selection)
        top_bar_layout.addWidget(back_btn)
        
        self.player_title = QLabel("")
        self.player_title.setFont(QFont("Microsoft YaHei", 13, QFont.Bold))
        self.player_title.setStyleSheet("color: #e94560;")
        top_bar_layout.addWidget(self.player_title, 1)

        content_layout.addWidget(top_bar)

        self.video_player = VideoPlayerWidget()
        self.video_player.question_triggered.connect(self._show_question)
        self.video_player.video_completed.connect(self._on_video_completed)

        content_layout.addWidget(self.video_player, 1)
        player_scroll.setWidget(player_content)
        player_layout.addWidget(player_scroll)

        self.content_stack.addWidget(self.player_page)
        
    def _create_footer(self):
        footer_frame = QFrame()
        footer_frame.setStyleSheet("background-color: #0f3460;")
        footer_layout = QHBoxLayout(footer_frame)
        footer_layout.setContentsMargins(20, 10, 20, 10)
        
        self.progress_label = QLabel("📊 学习进度: 0/3 视频完成")
        self.progress_label.setFont(QFont("Microsoft YaHei", 11))
        self.progress_label.setStyleSheet("color: #eaeaea;")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(20)
        self.progress_bar.setMaximumWidth(300)
        
        footer_layout.addWidget(self.progress_label)
        footer_layout.addStretch()
        footer_layout.addWidget(self.progress_bar)
        
        self.main_layout.addWidget(footer_frame)
        
    def _start_video(self, video_index):
        self.current_video_index = video_index
        video_data = self.data_manager.get_video(video_index)
        
        if video_data:
            self.player_title.setText(video_data['title'])
            self.video_player.load_video(video_data)
            self.content_stack.setCurrentIndex(1)
            
    def _show_question(self, question_data):
        self.video_player.pause_video()
        
        dialog = QuestionDialog(question_data, self)
        result = dialog.exec_()
        
        if result == QuestionDialog.Accepted:
            answer = dialog.get_answer()
            is_correct = self._check_answer(question_data, answer)
            self._show_result_feedback(is_correct, question_data)
            
            if self.current_video_index not in self.video_progress:
                self.video_progress[self.current_video_index] = {'answered': 0, 'correct': 0}
            self.video_progress[self.current_video_index]['answered'] += 1
            if is_correct:
                self.video_progress[self.current_video_index]['correct'] += 1
                
        self.video_player.resume_video()
        
    def _check_answer(self, question_data, user_answer):
        correct_answer = question_data.get('answer', '')
        if isinstance(correct_answer, list):
            return user_answer in correct_answer
        return user_answer == correct_answer
        
    def _show_result_feedback(self, is_correct, question_data):
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QScrollArea, QWidget
        
        # Create custom dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("✅ 回答正确！" if is_correct else "❌ 回答错误")
        dialog.setMinimumSize(600, 500)
        dialog.setStyleSheet(self._get_stylesheet())
        
        layout = QVBoxLayout(dialog)
        
        # Result message
        if is_correct:
            result_label = QLabel("🎉 恭喜你，回答正确！\n\n继续观看视频学习更多内容。")
            result_label.setStyleSheet("color: #4ade80; font-size: 16px;")
        else:
            correct_answer = question_data.get('answer', '')
            explanation = question_data.get('explanation', '')
            result_label = QLabel(f"正确答案: {correct_answer}\n\n{explanation}")
            result_label.setStyleSheet("color: #f87171; font-size: 14px;")
        
        result_label.setFont(QFont("Microsoft YaHei", 12))
        result_label.setWordWrap(True)
        layout.addWidget(result_label)
        
        # Show answer image if exists
        answer_image_path = question_data.get('answer_image', '')
        if answer_image_path and os.path.exists(answer_image_path):
            image_label = QLabel()
            pixmap = QPixmap(answer_image_path)
            image_label.setPixmap(pixmap.scaled(
                550, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
            image_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(image_label)
        
        # Close button
        close_btn = QPushButton("关闭")
        close_btn.setFont(QFont("Microsoft YaHei", 12))
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec_()
            
    def _on_video_completed(self):
        self.completed_videos.add(self.current_video_index)
        self._update_progress()
        
        accuracy = self._get_current_video_accuracy()
        QMessageBox.information(
            self, 
            "🎉 视频学习完成", 
            f"恭喜完成本视频的所有问题！\n\n正确率: {accuracy}%"
        )
        
    def _get_current_video_accuracy(self):
        if self.current_video_index not in self.video_progress:
            return 0
        progress = self.video_progress[self.current_video_index]
        if progress['answered'] == 0:
            return 0
        return int((progress['correct'] / progress['answered']) * 100)
        
    def _update_progress(self):
        total_videos = len(self.data_manager.get_all_videos())
        completed = len(self.completed_videos)
        
        self.progress_label.setText(f"📊 学习进度: {completed}/{total_videos} 视频完成")
        self.progress_bar.setValue(int((completed / total_videos) * 100))
        
    def _return_to_selection(self):
        self.video_player.stop_video()
        self.content_stack.setCurrentIndex(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())
