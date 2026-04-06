# -*- coding: utf-8 -*-
import os

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp, sp
from kivy.properties import BooleanProperty, ListProperty, NumericProperty, ObjectProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.togglebutton import ToggleButton
from kivy.graphics import Color, Line, Rectangle, RoundedRectangle

from data_manager import VideoDataManager


BG_COLOR = (0.10, 0.11, 0.18, 1)
CARD_COLOR = (0.09, 0.13, 0.24, 1)
CARD_ALT_COLOR = (0.07, 0.10, 0.19, 1)
ACCENT_COLOR = (0.91, 0.27, 0.38, 1)
TEXT_COLOR = (0.92, 0.93, 0.96, 1)
MUTED_COLOR = (0.62, 0.67, 0.76, 1)
SUCCESS_COLOR = (0.29, 0.78, 0.45, 1)
WARN_COLOR = (0.95, 0.45, 0.45, 1)


Builder.load_string(
    """
<PrimaryButton>:
    background_normal: ''
    background_down: ''
    background_color: 0, 0, 0, 0
    color: 0.95, 0.95, 0.98, 1
    font_size: '15sp'
    size_hint_y: None
    height: '44dp'
    canvas.before:
        Color:
            rgba: 0.91, 0.27, 0.38, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [12]

<SecondaryButton>:
    background_normal: ''
    background_down: ''
    background_color: 0, 0, 0, 0
    color: 0.92, 0.93, 0.96, 1
    font_size: '15sp'
    size_hint_y: None
    height: '44dp'
    canvas.before:
        Color:
            rgba: 0.08, 0.10, 0.18, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [12]
        Color:
            rgba: 0.18, 0.24, 0.38, 1
        Line:
            rounded_rectangle: (self.x, self.y, self.width, self.height, 12)
            width: 1.1

<ChoiceButton>:
    background_normal: ''
    background_down: ''
    background_color: 0, 0, 0, 0
    color: 0.92, 0.93, 0.96, 1
    font_size: '15sp'
    markup: True
    size_hint_y: None
    height: max(self.texture_size[1] + dp(24), dp(52))
    text_size: self.width - dp(22), None
    halign: 'left'
    valign: 'middle'
    canvas.before:
        Color:
            rgba: (0.91, 0.27, 0.38, 1) if self.state == 'down' else (0.08, 0.10, 0.18, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [12]
        Color:
            rgba: (0.91, 0.27, 0.38, 1) if self.state == 'down' else (0.18, 0.24, 0.38, 1)
        Line:
            rounded_rectangle: (self.x, self.y, self.width, self.height, 12)
            width: 1.1

<DraggableChip>:
    color: 1, 1, 1, 1
    font_size: '14sp'
    bold: True
    text_size: None, None
    size_hint: None, None
    canvas.before:
        Color:
            rgba: 0.91, 0.27, 0.38, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [12]
"""
)


def image_exists(path):
    return bool(path and os.path.exists(path))


class PrimaryButton(Button):
    pass


class SecondaryButton(Button):
    pass


class ChoiceButton(ToggleButton):
    pass


class SurfaceBox(BoxLayout):
    surface_color = ListProperty(CARD_COLOR)
    border_color = ListProperty((0.18, 0.24, 0.38, 1))
    radius = NumericProperty(dp(18))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self._bg_color = Color(*self.surface_color)
            self._bg_rect = RoundedRectangle(radius=[self.radius])
            self._line_color = Color(*self.border_color)
            self._bg_line = Line(width=1.1)
        self.bind(pos=self._update_canvas, size=self._update_canvas, surface_color=self._update_colors, border_color=self._update_colors, radius=self._update_canvas)

    def _update_colors(self, *_):
        self._bg_color.rgba = self.surface_color
        self._line_color.rgba = self.border_color

    def _update_canvas(self, *_):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self._bg_rect.radius = [self.radius]
        self._bg_line.rounded_rectangle = (self.x, self.y, self.width, self.height, self.radius)


class CourseCard(ButtonBehavior, SurfaceBox):
    course_data = ObjectProperty(None)
    on_open = ObjectProperty(None, allownone=True)

    def __init__(self, course_data, on_open=None, **kwargs):
        super().__init__(orientation="horizontal", spacing=dp(14), padding=dp(14), **kwargs)
        self.course_data = course_data
        self.on_open = on_open
        self.size_hint_y = None
        self.height = dp(138)
        self.surface_color = CARD_COLOR
        self._build_ui()

    def _build_ui(self):
        thumb = self.course_data.get("thumbnail", "")
        preview = Image(source=thumb if image_exists(thumb) else "", size_hint=(None, 1), width=dp(148), allow_stretch=True, keep_ratio=True)
        self.add_widget(preview)

        text_wrap = BoxLayout(orientation="vertical", spacing=dp(6))
        title = Label(
            text=f"[b]{self.course_data.get('title', '')}[/b]",
            markup=True,
            color=TEXT_COLOR,
            font_size=sp(18),
            size_hint_y=None,
            halign="left",
            valign="top",
        )
        title.bind(width=lambda inst, value: setattr(inst, "text_size", (value, None)))
        title.bind(texture_size=lambda inst, value: setattr(inst, "height", max(value[1], dp(28))))

        desc = Label(
            text=self.course_data.get("description", ""),
            color=MUTED_COLOR,
            font_size=sp(14),
            size_hint_y=None,
            halign="left",
            valign="top",
        )
        desc.bind(width=lambda inst, value: setattr(inst, "text_size", (value, None)))
        desc.bind(texture_size=lambda inst, value: setattr(inst, "height", max(value[1], dp(42))))

        segments = self.course_data.get("video_segments", [])
        question_count = sum(1 for item in segments if item.get("has_question"))
        stats = Label(
            text=f"共 {len(segments)} 个片段 · {question_count} 道交互题",
            color=ACCENT_COLOR,
            font_size=sp(13),
            size_hint_y=None,
            height=dp(22),
            halign="left",
            valign="middle",
        )
        stats.bind(width=lambda inst, value: setattr(inst, "text_size", (value, None)))

        open_hint = Label(
            text="点击进入课程",
            color=TEXT_COLOR,
            font_size=sp(13),
            size_hint_y=None,
            height=dp(22),
            halign="left",
            valign="middle",
        )
        open_hint.bind(width=lambda inst, value: setattr(inst, "text_size", (value, None)))

        text_wrap.add_widget(title)
        text_wrap.add_widget(desc)
        text_wrap.add_widget(stats)
        text_wrap.add_widget(open_hint)
        text_wrap.add_widget(Label(size_hint_y=1))
        self.add_widget(text_wrap)

    def on_release(self):
        if self.on_open:
            self.on_open(self.course_data)


class SegmentCard(SurfaceBox):
    def __init__(self, segment_data, index, on_open, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(10), padding=dp(14), **kwargs)
        self.size_hint_y = None
        self.height = dp(196)
        self.surface_color = CARD_ALT_COLOR

        top = BoxLayout(size_hint_y=None, height=dp(28))
        badge_text = "交互题" if segment_data.get("has_question") else "知识片段"
        badge_color = ACCENT_COLOR if segment_data.get("has_question") else SUCCESS_COLOR
        title = Label(
            text=f"[b]片段 {index + 1}[/b]  ·  {segment_data.get('time_display', '')}",
            markup=True,
            color=TEXT_COLOR,
            halign="left",
            valign="middle",
        )
        title.bind(width=lambda inst, value: setattr(inst, "text_size", (value, None)))
        badge = Label(
            text=badge_text,
            color=badge_color,
            font_size=sp(12),
            size_hint_x=None,
            width=dp(80),
            halign="right",
            valign="middle",
        )
        badge.bind(width=lambda inst, value: setattr(inst, "text_size", (value, None)))
        top.add_widget(title)
        top.add_widget(badge)
        self.add_widget(top)

        text = segment_data.get("question") or segment_data.get("description", "继续学习本片段内容。")
        summary = Label(
            text=text,
            color=MUTED_COLOR,
            font_size=sp(14),
            halign="left",
            valign="top",
            size_hint_y=None,
        )
        summary.bind(width=lambda inst, value: setattr(inst, "text_size", (value, None)))
        summary.bind(texture_size=lambda inst, value: setattr(inst, "height", max(value[1], dp(52))))
        self.add_widget(summary)

        image_path = segment_data.get("image", "")
        preview = Image(source=image_path if image_exists(image_path) else "", size_hint_y=1, allow_stretch=True, keep_ratio=True)
        self.add_widget(preview)

        button_cls = PrimaryButton if segment_data.get("has_question") else SecondaryButton
        action_text = "开始答题" if segment_data.get("has_question") else "查看内容"
        action_btn = button_cls(text=action_text)
        action_btn.bind(on_release=lambda *_: on_open(segment_data))
        self.add_widget(action_btn)


class MessagePopup(Popup):
    def __init__(self, title, message, image_path="", **kwargs):
        super().__init__(title=title, size_hint=(0.94, 0.88), auto_dismiss=False, separator_color=ACCENT_COLOR, **kwargs)
        content = BoxLayout(orientation="vertical", spacing=dp(12), padding=dp(16))

        scroll = ScrollView(do_scroll_x=False)
        body = BoxLayout(orientation="vertical", spacing=dp(12), size_hint_y=None)
        body.bind(minimum_height=body.setter("height"))

        message_label = Label(
            text=message,
            color=TEXT_COLOR,
            font_size=sp(16),
            halign="left",
            valign="top",
            size_hint_y=None,
        )
        message_label.bind(width=lambda inst, value: setattr(inst, "text_size", (value, None)))
        message_label.bind(texture_size=lambda inst, value: setattr(inst, "height", max(value[1], dp(40))))
        body.add_widget(message_label)

        if image_exists(image_path):
            img = Image(source=image_path, size_hint_y=None, height=dp(280), allow_stretch=True, keep_ratio=True)
            body.add_widget(img)

        scroll.add_widget(body)
        content.add_widget(scroll)

        close_btn = PrimaryButton(text="关闭")
        close_btn.bind(on_release=lambda *_: self.dismiss())
        content.add_widget(close_btn)
        self.content = content


class DraggableChip(Label):
    drag_offset = ListProperty([0, 0])
    placed = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.bind(texture_size=self._refresh_size)

    def _refresh_size(self, *_):
        self.size = (self.texture_size[0] + dp(24), self.texture_size[1] + dp(14))

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.drag_offset = [touch.x - self.x, touch.y - self.y]
            if self.parent:
                self.parent.remove_widget(self)
                self.parent.add_widget(self)
            touch.grab(self)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self and self.parent:
            raw_x = touch.x - self.drag_offset[0]
            raw_y = touch.y - self.drag_offset[1]
            bounded_x, bounded_y = self.parent.bound_chip_position(self, raw_x, raw_y)
            self.pos = (bounded_x, bounded_y)
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            self.placed = True
            return True
        return super().on_touch_up(touch)


class AnnotationStage(FloatLayout):
    def __init__(self, image_path, annotation_items, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(430)
        self.image_path = image_path
        self.annotation_items = annotation_items
        self.image_area = [0, 0, 0, 0]
        self.tray_area = [0, 0, 0, 0]
        self.chips = []

        with self.canvas.before:
            self._root_bg = Color(*CARD_ALT_COLOR)
            self._root_rect = RoundedRectangle(radius=[dp(18)])
            self._root_line_color = Color(0.18, 0.24, 0.38, 1)
            self._root_line = Line(width=1.1)
            self._image_bg = Color(0.04, 0.06, 0.11, 1)
            self._image_rect = RoundedRectangle(radius=[dp(16)])
            self._tray_bg = Color(0.08, 0.10, 0.18, 1)
            self._tray_rect = RoundedRectangle(radius=[dp(16)])

        self.hint_label = Label(
            text="拖拽标签到图像区域内，拖动时会自动保持在最上层。",
            color=TEXT_COLOR,
            font_size=sp(13),
            size_hint=(None, None),
            halign="left",
            valign="middle",
        )
        self.add_widget(self.hint_label)

        self.image_widget = Image(source=image_path if image_exists(image_path) else "", allow_stretch=True, keep_ratio=True, size_hint=(None, None))
        self.add_widget(self.image_widget)

        for item in self.annotation_items:
            chip = DraggableChip(text=item.get("name", ""))
            self.chips.append(chip)
            self.add_widget(chip)

        self.bind(pos=self._refresh_layout, size=self._refresh_layout)
        Clock.schedule_once(self._refresh_layout, 0)

    def bound_chip_position(self, chip, raw_x, raw_y):
        min_x = self.x + dp(12)
        min_y = self.y + dp(12)
        max_x = self.right - chip.width - dp(12)
        max_y = self.top - chip.height - dp(12)
        return min(max(raw_x, min_x), max_x), min(max(raw_y, min_y), max_y)

    def _refresh_layout(self, *_):
        pad = dp(12)
        gap = dp(12)
        hint_h = dp(28)
        tray_h = dp(110)
        content_x = self.x + pad
        content_y = self.y + pad
        content_w = max(self.width - pad * 2, dp(200))
        content_h = max(self.height - pad * 2, dp(260))

        image_y = content_y + tray_h + gap
        image_h = max(content_h - tray_h - gap - hint_h, dp(180))
        self.image_area = [content_x, image_y, content_w, image_h]
        self.tray_area = [content_x, content_y, content_w, tray_h]

        self._root_rect.pos = self.pos
        self._root_rect.size = self.size
        self._root_rect.radius = [dp(18)]
        self._root_line.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(18))

        self._image_rect.pos = (content_x, image_y)
        self._image_rect.size = (content_w, image_h)
        self._image_rect.radius = [dp(16)]

        self._tray_rect.pos = (content_x, content_y)
        self._tray_rect.size = (content_w, tray_h)
        self._tray_rect.radius = [dp(16)]

        self.hint_label.text_size = (content_w, hint_h)
        self.hint_label.size = (content_w, hint_h)
        self.hint_label.pos = (content_x, image_y + image_h - hint_h)

        self.image_widget.pos = (content_x, image_y)
        self.image_widget.size = (content_w, image_h)

        self._layout_chips()

    def _layout_chips(self):
        if not self.chips:
            return
        left, bottom, width, _ = self.tray_area
        x = left + dp(10)
        y = bottom + dp(18)
        row_height = 0
        right = left + width - dp(10)

        for chip in self.chips:
            chip.texture_update()
            if x + chip.width > right:
                x = left + dp(10)
                y += row_height + dp(10)
                row_height = 0

            if not chip.placed:
                chip.pos = self.bound_chip_position(chip, x, y)
            else:
                chip.pos = self.bound_chip_position(chip, chip.x, chip.y)

            row_height = max(row_height, chip.height)
            x += chip.width + dp(10)

    def get_annotations(self):
        left, bottom, width, height = self.image_area
        result = {}
        for chip in self.chips:
            center_x = chip.center_x
            center_y = chip.center_y
            in_image = left <= center_x <= left + width and bottom <= center_y <= bottom + height
            relative_pos = None
            if in_image and width > 0 and height > 0:
                relative_pos = (
                    round((center_x - left) / width, 4),
                    round((center_y - bottom) / height, 4),
                )
            result[chip.text] = {
                "canvas_pos": (round(chip.x, 2), round(chip.y, 2)),
                "relative_pos": relative_pos,
                "in_image": in_image,
            }
        return result


class QuestionPopup(Popup):
    def __init__(self, question_data, on_submit, **kwargs):
        super().__init__(title=f"交互题 · {question_data.get('time_display', '')}", size_hint=(0.97, 0.95), auto_dismiss=False, separator_color=ACCENT_COLOR, **kwargs)
        self.question_data = question_data
        self.on_submit = on_submit
        self.selected_answer = None
        self.choice_buttons = []
        self.annotation_stage = None
        self._build_content()

    def _build_content(self):
        wrap = BoxLayout(orientation="vertical", spacing=dp(12), padding=dp(16))

        scroll = ScrollView(do_scroll_x=False)
        body = BoxLayout(orientation="vertical", spacing=dp(12), size_hint_y=None)
        body.bind(minimum_height=body.setter("height"))

        title = Label(
            text=self.question_data.get("question", ""),
            color=TEXT_COLOR,
            font_size=sp(18),
            halign="left",
            valign="top",
            size_hint_y=None,
        )
        title.bind(width=lambda inst, value: setattr(inst, "text_size", (value, None)))
        title.bind(texture_size=lambda inst, value: setattr(inst, "height", max(value[1], dp(36))))
        body.add_widget(title)

        image_path = self.question_data.get("image", "")
        if image_exists(image_path):
            preview = Image(source=image_path, size_hint_y=None, height=dp(240), allow_stretch=True, keep_ratio=True)
            body.add_widget(preview)

        if self.question_data.get("type") == "choice":
            self._build_choice_area(body)
        else:
            self.annotation_stage = AnnotationStage(
                self.question_data.get("image", ""),
                self.question_data.get("annotation_items", []),
            )
            body.add_widget(self.annotation_stage)

        scroll.add_widget(body)
        wrap.add_widget(scroll)

        buttons = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
        cancel_btn = SecondaryButton(text="跳过")
        cancel_btn.bind(on_release=lambda *_: self.dismiss())
        submit_btn = PrimaryButton(text="提交答案")
        submit_btn.bind(on_release=self._submit)
        buttons.add_widget(cancel_btn)
        buttons.add_widget(submit_btn)
        wrap.add_widget(buttons)
        self.content = wrap

    def _build_choice_area(self, parent):
        group_name = f"choice_{id(self)}"
        for option in self.question_data.get("options", []):
            btn = ChoiceButton(text=option, group=group_name)
            btn.bind(on_release=self._set_choice)
            self.choice_buttons.append(btn)
            parent.add_widget(btn)

    def _set_choice(self, instance):
        self.selected_answer = instance.text[0] if instance.text else None

    def _submit(self, *_):
        if self.question_data.get("type") == "choice":
            if not self.selected_answer:
                MessagePopup("提示", "请先选择一个答案。").open()
                return
            answer = self.selected_answer
        else:
            annotations = self.annotation_stage.get_annotations() if self.annotation_stage else {}
            if annotations and not all(item["in_image"] for item in annotations.values()):
                MessagePopup("提示", "请先将所有标签拖拽到图像区域内。").open()
                return
            answer = "annotation_complete"
        self.dismiss()
        if self.on_submit:
            self.on_submit(answer, self.question_data)


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_manager = VideoDataManager()
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", spacing=dp(14), padding=dp(16))

        header = SurfaceBox(orientation="vertical", spacing=dp(6), padding=dp(16), size_hint_y=None, height=dp(122))
        header.surface_color = CARD_COLOR
        title = Label(text="[b]医学 AR+VR 教程 Android 版[/b]", markup=True, color=TEXT_COLOR, font_size=sp(24))
        subtitle = Label(text="移动端图像交互学习与答题入口", color=MUTED_COLOR, font_size=sp(14))
        self.progress_label = Label(text="", color=ACCENT_COLOR, font_size=sp(14))
        header.add_widget(title)
        header.add_widget(subtitle)
        header.add_widget(self.progress_label)
        root.add_widget(header)

        scroll = ScrollView(do_scroll_x=False)
        list_wrap = BoxLayout(orientation="vertical", spacing=dp(12), size_hint_y=None)
        list_wrap.bind(minimum_height=list_wrap.setter("height"))

        for course in self.data_manager.get_all_videos():
            list_wrap.add_widget(CourseCard(course, on_open=self._open_course))

        scroll.add_widget(list_wrap)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.refresh_progress()

    def refresh_progress(self):
        stats = App.get_running_app().stats
        self.progress_label.text = f"已完成 {stats['answered']} / {stats['total']} 道交互题，答对 {stats['correct']} 道。"

    def _open_course(self, course_data):
        course_screen = self.manager.get_screen("course")
        course_screen.load_course(course_data)
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "course"


class CourseScreen(Screen):
    current_course = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build_ui()

    def _build_ui(self):
        self.root_box = BoxLayout(orientation="vertical", spacing=dp(12), padding=dp(16))

        self.top_bar = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
        back_btn = SecondaryButton(text="← 返回课程")
        back_btn.bind(on_release=self._go_back)
        self.course_title = Label(text="", color=TEXT_COLOR, font_size=sp(18), halign="left", valign="middle")
        self.course_title.bind(width=lambda inst, value: setattr(inst, "text_size", (value, None)))
        self.top_bar.add_widget(back_btn)
        self.top_bar.add_widget(self.course_title)
        self.root_box.add_widget(self.top_bar)

        self.hero = SurfaceBox(orientation="horizontal", spacing=dp(12), padding=dp(14), size_hint_y=None, height=dp(180))
        self.hero.surface_color = CARD_COLOR
        self.hero_image = Image(size_hint=(None, 1), width=dp(220), allow_stretch=True, keep_ratio=True)
        self.hero.add_widget(self.hero_image)
        hero_text_wrap = BoxLayout(orientation="vertical", spacing=dp(8))
        self.hero_desc = Label(text="", color=TEXT_COLOR, font_size=sp(16), halign="left", valign="top")
        self.hero_desc.bind(width=lambda inst, value: setattr(inst, "text_size", (value, None)))
        self.hero_meta = Label(text="", color=ACCENT_COLOR, font_size=sp(13), halign="left", valign="middle")
        self.hero_meta.bind(width=lambda inst, value: setattr(inst, "text_size", (value, None)))
        hero_text_wrap.add_widget(self.hero_desc)
        hero_text_wrap.add_widget(self.hero_meta)
        hero_text_wrap.add_widget(Label(size_hint_y=1))
        self.hero.add_widget(hero_text_wrap)
        self.root_box.add_widget(self.hero)

        self.scroll = ScrollView(do_scroll_x=False)
        self.segment_list = BoxLayout(orientation="vertical", spacing=dp(12), size_hint_y=None)
        self.segment_list.bind(minimum_height=self.segment_list.setter("height"))
        self.scroll.add_widget(self.segment_list)
        self.root_box.add_widget(self.scroll)
        self.add_widget(self.root_box)

    def load_course(self, course_data):
        self.current_course = course_data
        self.course_title.text = course_data.get("title", "")
        self.hero_image.source = course_data.get("thumbnail", "") if image_exists(course_data.get("thumbnail", "")) else ""
        self.hero_desc.text = course_data.get("description", "")
        segments = course_data.get("video_segments", [])
        question_count = sum(1 for item in segments if item.get("has_question"))
        self.hero_meta.text = f"共 {len(segments)} 个片段 · {question_count} 道交互题"
        self.segment_list.clear_widgets()
        for index, segment in enumerate(segments):
            self.segment_list.add_widget(SegmentCard(segment, index, self._open_segment))

    def _open_segment(self, segment_data):
        if segment_data.get("has_question"):
            QuestionPopup(segment_data, self._on_answer_submitted).open()
            return
        message = f"⏱ 时间点：{segment_data.get('time_display', '')}\n\n{segment_data.get('description', '继续学习该片段内容。')}"
        MessagePopup("知识片段", message, image_path=segment_data.get("image", "")).open()

    def _on_answer_submitted(self, answer, question_data):
        correct_answer = question_data.get("answer", "")
        if isinstance(correct_answer, list):
            is_correct = answer in correct_answer
        else:
            is_correct = answer == correct_answer

        app = App.get_running_app()
        app.stats["answered"] += 1
        if is_correct:
            app.stats["correct"] += 1

        if is_correct:
            message = "回答正确，继续学习下一片段。"
            image_path = question_data.get("answer_image", "")
            MessagePopup("✅ 回答正确", message, image_path=image_path).open()
        else:
            explanation = question_data.get("explanation", "")
            message = f"正确答案：{correct_answer}\n\n{explanation}"
            MessagePopup("❌ 回答错误", message, image_path=question_data.get("answer_image", "")).open()

        home = self.manager.get_screen("home")
        home.refresh_progress()

    def _go_back(self, *_):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "home"


class MedicalTutorialAndroidApp(App):
    def build(self):
        Window.clearcolor = BG_COLOR
        self.data_manager = VideoDataManager()
        total = 0
        for course in self.data_manager.get_all_videos():
            total += sum(1 for item in course.get("video_segments", []) if item.get("has_question"))
        self.stats = {"answered": 0, "correct": 0, "total": total}

        manager = ScreenManager()
        manager.add_widget(HomeScreen(name="home"))
        manager.add_widget(CourseScreen(name="course"))
        return manager

    def get_application_name(self):
        return "医学AR+VR教程"


if __name__ == "__main__":
    MedicalTutorialAndroidApp().run()
