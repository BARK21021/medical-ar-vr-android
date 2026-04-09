import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QRadioButton, QButtonGroup, QFrame,
                             QScrollArea, QWidget, QMessageBox, QSpacerItem,
                             QSizePolicy)
from PyQt5.QtCore import Qt, QPoint, QRect, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QPainter, QPen, QColor, QBrush


class DraggableLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.drag_position = None
        self.user_positioned = False
        self.setStyleSheet("""
            QLabel {
                background-color: #e94560;
                color: white;
                padding: 8px 15px;
                border-radius: 8px;
                font-weight: bold;
            }
        """)
        self.setCursor(Qt.OpenHandCursor)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            self.raise_()
            
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position:
            parent_widget = self.parentWidget()
            if parent_widget:
                new_pos = parent_widget.mapFromGlobal(event.globalPos()) - self.drag_position
                if hasattr(parent_widget, "bound_label_position"):
                    new_pos = parent_widget.bound_label_position(self, new_pos)
                self.move(new_pos)
                self.raise_()
            
    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)
        if event.button() == Qt.LeftButton:
            self.user_positioned = True


class AnnotationCanvas(QFrame):
    def __init__(self, base_image_path, annotation_items, parent=None):
        super().__init__(parent)
        self.base_image_path = base_image_path
        self.annotation_items = annotation_items
        self.annotation_labels = []
        self.background_pixmap = QPixmap(self.base_image_path) if os.path.exists(self.base_image_path) else QPixmap()
        self.image_rect = QRect()
        self.tray_rect = QRect()

        self.setMinimumSize(640, 500)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet("""
            QFrame {
                background-color: #10182f;
                border: 2px solid #0f3460;
                border-radius: 12px;
            }
        """)

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #0a0a1a;
                border: 2px solid #0f3460;
                border-radius: 10px;
            }
        """)

        self.hint_label = QLabel("拖拽下方标签到图像对应位置，拖动时标签会始终显示在最上层。", self)
        self.hint_label.setFont(QFont("Microsoft YaHei", 10))
        self.hint_label.setStyleSheet("color: #eaeaea; background: transparent; border: none;")

        for item in self.annotation_items:
            label = DraggableLabel(item['name'], self)
            label.setFont(QFont("Microsoft YaHei", 10))
            label.adjustSize()
            self.annotation_labels.append((item['name'], label))

        self._refresh_layout()

    def bound_label_position(self, label, position):
        max_x = max(18, self.width() - label.width() - 18)
        max_y = max(18, self.height() - label.height() - 18)
        x = min(max(position.x(), 18), max_x)
        y = min(max(position.y(), 18), max_y)
        return QPoint(x, y)

    def get_annotations(self):
        positions = {}
        for name, label in self.annotation_labels:
            center = label.geometry().center()
            if self.image_rect.contains(center) and self.image_rect.width() > 0 and self.image_rect.height() > 0:
                rel_x = round((center.x() - self.image_rect.left()) / self.image_rect.width(), 4)
                rel_y = round((center.y() - self.image_rect.top()) / self.image_rect.height(), 4)
                positions[name] = {
                    'canvas_pos': (label.x(), label.y()),
                    'relative_pos': (rel_x, rel_y),
                    'in_image': True
                }
            else:
                positions[name] = {
                    'canvas_pos': (label.x(), label.y()),
                    'relative_pos': None,
                    'in_image': False
                }
        return positions

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._refresh_layout()

    def _refresh_layout(self):
        content_rect = self.rect().adjusted(18, 18, -18, -18)
        tray_height = 108
        gap = 14

        self.tray_rect = QRect(
            content_rect.left(),
            content_rect.bottom() - tray_height + 1,
            content_rect.width(),
            tray_height
        )

        image_area = QRect(
            content_rect.left(),
            content_rect.top() + 26,
            content_rect.width(),
            max(200, content_rect.height() - tray_height - gap - 26)
        )

        self.hint_label.setGeometry(content_rect.left(), content_rect.top(), content_rect.width(), 24)

        if not self.background_pixmap.isNull():
            scaled = self.background_pixmap.scaled(
                image_area.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            image_x = image_area.left() + (image_area.width() - scaled.width()) // 2
            image_y = image_area.top() + (image_area.height() - scaled.height()) // 2
            self.image_rect = QRect(image_x, image_y, scaled.width(), scaled.height())
            self.image_label.setGeometry(self.image_rect)
            self.image_label.setPixmap(scaled)
            self.image_label.setText("")
        else:
            self.image_rect = image_area
            self.image_label.setGeometry(self.image_rect)
            self.image_label.setPixmap(QPixmap())
            self.image_label.setText("📷 图像未找到")
            self.image_label.setFont(QFont("Microsoft YaHei", 14))

        self._layout_labels()
        self.image_label.lower()
        self.hint_label.raise_()

    def _layout_labels(self):
        x = self.tray_rect.left() + 8
        y = self.tray_rect.top() + 18
        row_height = 0
        max_right = self.tray_rect.right() - 8

        for _, label in self.annotation_labels:
            label.adjustSize()
            if x + label.width() > max_right:
                x = self.tray_rect.left() + 8
                y += row_height + 12
                row_height = 0

            target_pos = QPoint(x, y)
            if not label.user_positioned:
                label.move(self.bound_label_position(label, target_pos))
            else:
                label.move(self.bound_label_position(label, label.pos()))

            row_height = max(row_height, label.height())
            x += label.width() + 12
            label.raise_()


class AnnotationWidget(QWidget):
    def __init__(self, base_image_path, annotation_items, parent=None):
        super().__init__(parent)
        self.base_image_path = base_image_path
        self.annotation_items = annotation_items
        self.annotations = {}
        self.annotation_labels = []
        
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        instruction = QLabel("🎯 拖拽标签到图像上正确位置：")
        instruction.setFont(QFont("Microsoft YaHei", 11))
        instruction.setStyleSheet("color: #eaeaea;")
        layout.addWidget(instruction)

        self.canvas = AnnotationCanvas(self.base_image_path, self.annotation_items, self)
        self.annotation_labels = self.canvas.annotation_labels
        layout.addWidget(self.canvas)
        
    def get_annotations(self):
        return self.canvas.get_annotations()


class QuestionDialog(QDialog):
    def __init__(self, question_data, parent=None):
        super().__init__(parent)
        self.question_data = question_data
        self.user_answer = None
        self.annotation_widget = None
        
        self.setWindowTitle("📝 问题")
        self.setMinimumSize(820, 660)
        self.setStyleSheet(self._get_stylesheet())
        
        self._init_ui()
        
    def _get_stylesheet(self):
        return """
            QDialog {
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
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0f3460;
                border-color: #e94560;
            }
            QPushButton:pressed {
                background-color: #e94560;
            }
            QRadioButton {
                color: #eaeaea;
                font-size: 14px;
                spacing: 10px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
            QRadioButton::indicator:unchecked {
                border: 2px solid #0f3460;
                border-radius: 9px;
                background-color: #16213e;
            }
            QRadioButton::indicator:checked {
                border: 2px solid #e94560;
                border-radius: 9px;
                background-color: #e94560;
            }
            QFrame {
                background-color: #16213e;
                border-radius: 10px;
            }
        """
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        time_display = self.question_data.get('time_display', '')
        title_label = QLabel(f"⏱ 时间点: {time_display}")
        title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        title_label.setStyleSheet("color: #e94560;")
        layout.addWidget(title_label)
        
        question_text = self.question_data.get('question', '')
        question_label = QLabel(f"❓ {question_text}")
        question_label.setFont(QFont("Microsoft YaHei", 12))
        question_label.setWordWrap(True)
        layout.addWidget(question_label)
        
        image_path = self.question_data.get('image', '')
        if image_path and os.path.exists(image_path):
            image_frame = QFrame()
            image_layout = QVBoxLayout(image_frame)
            
            image_label = QLabel()
            pixmap = QPixmap(image_path)
            image_label.setPixmap(pixmap.scaled(
                450, 280, Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
            image_label.setAlignment(Qt.AlignCenter)
            image_layout.addWidget(image_label)
            layout.addWidget(image_frame)
        
        question_type = self.question_data.get('type', 'choice')
        
        if question_type == 'choice':
            self._create_choice_options(layout)
        elif question_type == 'annotation':
            self._create_annotation_area(layout)
            
        self._create_buttons(layout)
        
    def _create_choice_options(self, layout):
        options_frame = QFrame()
        options_frame.setStyleSheet("padding: 12px;")
        options_layout = QVBoxLayout(options_frame)
        options_layout.setSpacing(8)
        
        self.button_group = QButtonGroup()
        options = self.question_data.get('options', [])
        
        for i, option in enumerate(options):
            radio_btn = QRadioButton(option)
            radio_btn.setFont(QFont("Microsoft YaHei", 11))
            self.button_group.addButton(radio_btn, i)
            options_layout.addWidget(radio_btn)
            
        layout.addWidget(options_frame)
        
    def _create_annotation_area(self, layout):
        annotation_items = self.question_data.get('annotation_items', [])
        image_path = self.question_data.get('image', '')
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: 2px solid #0f3460;
                border-radius: 10px;
                background-color: #16213e;
            }
        """)
        
        self.annotation_widget = AnnotationWidget(image_path, annotation_items)
        scroll.setWidget(self.annotation_widget)
        scroll.setMinimumHeight(460)
        
        layout.addWidget(scroll)
        
    def _create_buttons(self, layout):
        layout.addStretch()
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        submit_btn = QPushButton("✓ 提交答案")
        submit_btn.setFont(QFont("Microsoft YaHei", 12))
        submit_btn.setMinimumWidth(140)
        submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #e94560;
            }
        """)
        submit_btn.clicked.connect(self._submit_answer)
        
        skip_btn = QPushButton("跳过")
        skip_btn.setFont(QFont("Microsoft YaHei", 12))
        skip_btn.setMinimumWidth(100)
        skip_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(skip_btn)
        buttons_layout.addWidget(submit_btn)
        
        layout.addLayout(buttons_layout)
        
    def _submit_answer(self):
        question_type = self.question_data.get('type', 'choice')
        
        if question_type == 'choice':
            checked_id = self.button_group.checkedId()
            if checked_id == -1:
                QMessageBox.warning(self, "⚠ 提示", "请选择一个答案")
                return
            options = self.question_data.get('options', [])
            if 0 <= checked_id < len(options):
                self.user_answer = options[checked_id][0]
        elif question_type == 'annotation':
            annotations = self.annotation_widget.get_annotations() if self.annotation_widget else {}
            if annotations and not all(item.get('in_image') for item in annotations.values()):
                QMessageBox.warning(self, "⚠ 提示", "请先将所有标签拖拽到图像区域内再提交")
                return
            self.user_answer = 'annotation_complete'
            
        self.accept()
        
    def get_answer(self):
        return self.user_answer
