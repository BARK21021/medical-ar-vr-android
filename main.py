    # -*- coding: utf-8 -*-
import gc
import hashlib
import os
import sys
import traceback
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.metrics import dp, sp
from kivy.properties import BooleanProperty, ListProperty, NumericProperty, ObjectProperty, StringProperty
from kivy.utils import platform
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

try:
    from PIL import Image as PILImage
except ImportError:
    PILImage = None

PIL_RESAMPLING = getattr(getattr(PILImage, "Resampling", PILImage), "LANCZOS", None) if PILImage else None


BG_COLOR = (0.10, 0.11, 0.18, 1)
CARD_COLOR = (0.09, 0.13, 0.24, 1)
CARD_ALT_COLOR = (0.07, 0.10, 0.19, 1)
ACCENT_COLOR = (0.91, 0.27, 0.38, 1)
TEXT_COLOR = (0.92, 0.93, 0.96, 1)
MUTED_COLOR = (0.62, 0.67, 0.76, 1)
SUCCESS_COLOR = (0.29, 0.78, 0.45, 1)
WARN_COLOR = (0.95, 0.45, 0.45, 1)

FONT_SCALE_PRESETS = {
    "font_scale_1.0": {"font": 1.0, "layout": 0.96, "media": 0.94},
    "font_scale_1.15": {"font": 1.15, "layout": 1.0, "media": 1.0},
    "font_scale_1.3": {"font": 1.3, "layout": 1.08, "media": 1.08},
}

IMAGE_MAX_EDGE = {
    "thumbnail": 1280,
    "content": 1600,
    "detail": 1920,
}


Builder.load_string(
    """
<PrimaryButton>:
    background_normal: ''
    background_down: ''
    background_color: 0, 0, 0, 0
    color: 0.95, 0.95, 0.98, 1
    font_size: self.ui_font_size
    size_hint_y: None
    height: self.ui_height
    canvas.before:
        Color:
            rgba: 0.91, 0.27, 0.38, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.corner_radius]

<SecondaryButton>:
    background_normal: ''
    background_down: ''
    background_color: 0, 0, 0, 0
    color: 0.92, 0.93, 0.96, 1
    font_size: self.ui_font_size
    size_hint_y: None
    height: self.ui_height
    canvas.before:
        Color:
            rgba: 0.08, 0.10, 0.18, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.corner_radius]
        Color:
            rgba: 0.18, 0.24, 0.38, 1
        Line:
            rounded_rectangle: (self.x, self.y, self.width, self.height, self.corner_radius)
            width: 1.1

<ChoiceButton>:
    background_normal: ''
    background_down: ''
    background_color: 0, 0, 0, 0
    color: 0.92, 0.93, 0.96, 1
    font_size: self.ui_font_size
    markup: True
    size_hint_y: None
    height: self.ui_height
    text_size: self.width - self.text_padding, None
    halign: 'left'
    valign: 'middle'
    canvas.before:
        Color:
            rgba: (0.91, 0.27, 0.38, 1) if self.state == 'down' else (0.08, 0.10, 0.18, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.corner_radius]
        Color:
            rgba: (0.91, 0.27, 0.38, 1) if self.state == 'down' else (0.18, 0.24, 0.38, 1)
        Line:
            rounded_rectangle: (self.x, self.y, self.width, self.height, self.corner_radius)
            width: 1.1

<DraggableChip>:
    color: 1, 1, 1, 1
    font_size: self.ui_font_size
    bold: True
    text_size: None, None
    size_hint: None, None
    canvas.before:
        Color:
            rgba: 0.91, 0.27, 0.38, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.corner_radius]
"""
)


def image_exists(path):
    return bool(path and os.path.exists(path))


def runtime_storage_dir():
    app = App.get_running_app()
    base_dir = getattr(app, "user_data_dir", "") if app else ""
    if not base_dir:
        base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".runtime")
    os.makedirs(base_dir, exist_ok=True)
    return base_dir


def runtime_cache_dir():
    cache_dir = os.path.join(runtime_storage_dir(), "image_cache")
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


def runtime_log_path():
    return os.path.join(runtime_storage_dir(), "pico_runtime.log")


def log_runtime_event(event, **payload):
    message = " ".join(f"{key}={payload[key]}" for key in sorted(payload))
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {event}"
    if message:
        line = f"{line} {message}"
    Logger.info(line)
    try:
        with open(runtime_log_path(), "a", encoding="utf-8") as handle:
            handle.write(line + "\n")
    except OSError:
        pass


def install_runtime_exception_hook():
    previous_hook = sys.excepthook

    def _handle_exception(exc_type, exc_value, exc_traceback):
        formatted = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        log_runtime_event("uncaught_exception", detail=formatted.replace("\n", "\\n"))
        previous_hook(exc_type, exc_value, exc_traceback)

    sys.excepthook = _handle_exception


def optimized_image_source(path, profile="content"):
    if not image_exists(path) or PILImage is None:
        return path if image_exists(path) else ""

    max_edge = IMAGE_MAX_EDGE.get(profile, IMAGE_MAX_EDGE["content"])

    try:
        source_mtime = int(os.path.getmtime(path))
        cache_key = hashlib.md5(f"{path}|{source_mtime}|{max_edge}".encode("utf-8")).hexdigest()
        cached_path = os.path.join(runtime_cache_dir(), f"{cache_key}.png")
        if os.path.exists(cached_path):
            return cached_path

        with PILImage.open(path) as image:
            if max(image.size) <= max_edge:
                return path
            optimized = image.copy()
            if PIL_RESAMPLING:
                optimized.thumbnail((max_edge, max_edge), PIL_RESAMPLING)
            else:
                optimized.thumbnail((max_edge, max_edge))
            optimized.save(cached_path, format="PNG", optimize=True)
        log_runtime_event("optimized_image", source=os.path.basename(path), profile=profile, cached=os.path.basename(cached_path))
        return cached_path
    except Exception as exc:
        log_runtime_event("optimize_image_failed", source=os.path.basename(path), error=str(exc))
        return path


def release_widget_images(widget):
    for child in list(getattr(widget, "children", [])):
        release_widget_images(child)

    if isinstance(widget, Image):
        widget.source = ""
        widget.texture = None
        widget.canvas.ask_update()


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def ui_scale_name():
    short_edge = min(max(Window.width, 1), max(Window.height, 1))
    long_edge = max(max(Window.width, 1), max(Window.height, 1))
    if short_edge <= 800 or long_edge <= 1280:
        return "font_scale_1.0"
    if short_edge <= 1200 or long_edge <= 2200:
        return "font_scale_1.15"
    return "font_scale_1.3"


def ui_scale_profile():
    return FONT_SCALE_PRESETS[ui_scale_name()]


def ui_dp(value, kind="layout"):
    profile = ui_scale_profile()
    factor = profile["media"] if kind == "media" else profile["layout"]
    return dp(value * factor)


def ui_sp(value):
    return sp(value * ui_scale_profile()["font"])


def wrapped_text_width(widget, padding=0):
    return max(widget.width - padding, 0)


def bind_wrapped_label(label, min_height=0, width_padding=0, line_height=1.15):
    label.line_height = line_height

    def _sync_width(inst, value):
        inst.text_size = (max(value - width_padding, 0), None)

    label.bind(width=_sync_width)
    if min_height:
        label.bind(texture_size=lambda inst, value: setattr(inst, "height", max(value[1], min_height)))
    _sync_width(label, label.width)


class PrimaryButton(Button):
    ui_font_size = NumericProperty(sp(15))
    ui_height = NumericProperty(dp(44))
    corner_radius = NumericProperty(dp(12))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ui_font_size = ui_sp(15)
        self.ui_height = ui_dp(46)
        self.corner_radius = ui_dp(12)
        self.font_size = self.ui_font_size
        self.height = self.ui_height


class SecondaryButton(Button):
    ui_font_size = NumericProperty(sp(15))
    ui_height = NumericProperty(dp(44))
    corner_radius = NumericProperty(dp(12))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ui_font_size = ui_sp(15)
        self.ui_height = ui_dp(46)
        self.corner_radius = ui_dp(12)
        self.font_size = self.ui_font_size
        self.height = self.ui_height


class ChoiceButton(ToggleButton):
    ui_font_size = NumericProperty(sp(15))
    ui_height = NumericProperty(dp(52))
    corner_radius = NumericProperty(dp(12))
    text_padding = NumericProperty(dp(22))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ui_font_size = ui_sp(15)
        self.ui_height = ui_dp(52)
        self.corner_radius = ui_dp(12)
        self.text_padding = ui_dp(22)
        self.font_size = self.ui_font_size
        self.bind(width=self._sync_text_wrap, texture_size=self._sync_height)
        self._sync_text_wrap(self, self.width)
        self._sync_height(self, self.texture_size)

    def _sync_text_wrap(self, *_):
        self.text_size = (wrapped_text_width(self, self.text_padding), None)

    def _sync_height(self, *_):
        self.height = max(self.texture_size[1] + ui_dp(24), self.ui_height)


class SurfaceBox(BoxLayout):
    surface_color = ListProperty(CARD_COLOR)
    border_color = ListProperty((0.18, 0.24, 0.38, 1))
    radius = NumericProperty(dp(18))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.radius = ui_dp(18)
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
        self._outer_padding = ui_dp(14)
        self._gap = ui_dp(14)
        super().__init__(orientation="horizontal", spacing=self._gap, padding=self._outer_padding, **kwargs)
        self.course_data = course_data
        self.on_open = on_open
        self.size_hint_y = None
        self.height = ui_dp(156)
        self.surface_color = CARD_COLOR
        self._build_ui()
        self.bind(size=self._refresh_layout)

    def _build_ui(self):
        thumb = self.course_data.get("thumbnail", "")
        self.preview = Image(
            source=optimized_image_source(thumb, "thumbnail") if image_exists(thumb) else "",
            size_hint=(None, None),
            allow_stretch=True,
            keep_ratio=True,
        )
        self.add_widget(self.preview)

        self.text_wrap = BoxLayout(orientation="vertical", spacing=ui_dp(6))
        self.title = Label(
            text=f"[b]{self.course_data.get('title', '')}[/b]",
            markup=True,
            color=TEXT_COLOR,
            font_size=ui_sp(18),
            size_hint_y=None,
            halign="left",
            valign="top",
        )
        bind_wrapped_label(self.title, min_height=ui_dp(28), line_height=1.12)

        self.desc = Label(
            text=self.course_data.get("description", ""),
            color=MUTED_COLOR,
            font_size=ui_sp(14),
            size_hint_y=None,
            halign="left",
            valign="top",
        )
        bind_wrapped_label(self.desc, min_height=ui_dp(42), line_height=1.18)

        segments = self.course_data.get("video_segments", [])
        question_count = sum(1 for item in segments if item.get("has_question"))
        self.stats = Label(
            text=f"共 {len(segments)} 个片段 · {question_count} 道交互题",
            color=ACCENT_COLOR,
            font_size=ui_sp(13),
            size_hint_y=None,
            height=ui_dp(22),
            halign="left",
            valign="middle",
        )
        bind_wrapped_label(self.stats, min_height=ui_dp(22), line_height=1.1)

        self.open_hint = Label(
            text="点击进入课程",
            color=TEXT_COLOR,
            font_size=ui_sp(13),
            size_hint_y=None,
            height=ui_dp(22),
            halign="left",
            valign="middle",
        )
        bind_wrapped_label(self.open_hint, min_height=ui_dp(22), line_height=1.1)

        self.text_wrap.add_widget(self.title)
        self.text_wrap.add_widget(self.desc)
        self.text_wrap.add_widget(self.stats)
        self.text_wrap.add_widget(self.open_hint)
        self.text_wrap.add_widget(Label(size_hint_y=1))
        self.add_widget(self.text_wrap)

        for widget in (self.title, self.desc, self.stats, self.open_hint):
            widget.bind(texture_size=self._refresh_layout)
        self._refresh_layout()

    def _refresh_layout(self, *_):
        inner_width = max(self.width - self._outer_padding * 2 - self._gap, ui_dp(280))
        preview_width = clamp(inner_width * 0.32, ui_dp(118, "media"), ui_dp(172, "media"))
        preview_height = clamp(preview_width * 0.72, ui_dp(98, "media"), ui_dp(136, "media"))
        self.preview.size = (preview_width, preview_height)

        text_width = max(inner_width - preview_width, ui_dp(132))
        for label in (self.title, self.desc, self.stats, self.open_hint):
            label.text_size = (text_width, None)

        content_height = (
            self._outer_padding * 2
            + self.title.height
            + self.desc.height
            + self.stats.height
            + self.open_hint.height
            + self.text_wrap.spacing * 3
        )
        media_height = preview_height + self._outer_padding * 2
        self.height = max(content_height, media_height)

    def on_release(self):
        if self.on_open:
            self.on_open(self.course_data)


class SegmentCard(SurfaceBox):
    def __init__(self, segment_data, index, on_open, **kwargs):
        self._outer_padding = ui_dp(14)
        self._gap = ui_dp(10)
        super().__init__(orientation="vertical", spacing=self._gap, padding=self._outer_padding, **kwargs)
        self.size_hint_y = None
        self.height = ui_dp(214)
        self.surface_color = CARD_ALT_COLOR

        self.top = BoxLayout(size_hint_y=None, height=ui_dp(30))
        badge_text = "交互题" if segment_data.get("has_question") else "知识片段"
        badge_color = ACCENT_COLOR if segment_data.get("has_question") else SUCCESS_COLOR
        self.segment_title = Label(
            text=f"[b]片段 {index + 1}[/b]  ·  {segment_data.get('time_display', '')}",
            markup=True,
            color=TEXT_COLOR,
            font_size=ui_sp(16),
            size_hint_y=None,
            halign="left",
            valign="middle",
        )
        bind_wrapped_label(self.segment_title, min_height=ui_dp(24), line_height=1.12)
        self.badge = Label(
            text=badge_text,
            color=badge_color,
            font_size=ui_sp(12),
            size_hint_x=None,
            width=ui_dp(84),
            halign="right",
            valign="middle",
        )
        self.badge.bind(width=lambda inst, value: setattr(inst, "text_size", (value, None)))
        self.top.add_widget(self.segment_title)
        self.top.add_widget(self.badge)
        self.add_widget(self.top)

        text = segment_data.get("question") or segment_data.get("description", "继续学习本片段内容。")
        self.summary = Label(
            text=text,
            color=MUTED_COLOR,
            font_size=ui_sp(14),
            halign="left",
            valign="top",
            size_hint_y=None,
        )
        bind_wrapped_label(self.summary, min_height=ui_dp(52), line_height=1.18)
        self.add_widget(self.summary)

        image_path = segment_data.get("image", "")
        self.preview = Image(
            source=optimized_image_source(image_path, "content") if image_exists(image_path) else "",
            size_hint_y=None,
            allow_stretch=True,
            keep_ratio=True,
        )
        self.add_widget(self.preview)

        button_cls = PrimaryButton if segment_data.get("has_question") else SecondaryButton
        action_text = "开始答题" if segment_data.get("has_question") else "查看内容"
        self.action_btn = button_cls(text=action_text)
        self.action_btn.bind(on_release=lambda *_: on_open(segment_data))
        self.add_widget(self.action_btn)
        self.bind(size=self._refresh_layout)
        self.segment_title.bind(texture_size=self._refresh_layout)
        self.summary.bind(texture_size=self._refresh_layout)
        self._refresh_layout()

    def _refresh_layout(self, *_):
        content_width = max(self.width - self._outer_padding * 2, ui_dp(220))
        self.badge.width = clamp(content_width * 0.22, ui_dp(74), ui_dp(92))
        self.segment_title.text_size = (max(content_width - self.badge.width - self._gap, ui_dp(110)), None)
        self.top.height = max(self.segment_title.height, self.badge.texture_size[1], ui_dp(28))
        self.summary.text_size = (content_width, None)
        preview_height = clamp(content_width * 0.34, ui_dp(84, "media"), ui_dp(146, "media"))
        self.preview.height = preview_height
        self.height = max(
            self._outer_padding * 2 + self.top.height + self.summary.height + preview_height + self.action_btn.height + self.spacing * 3,
            ui_dp(188),
        )


class ManagedPopup(Popup):
    def dismiss(self, *args, **kwargs):
        self._release_media()
        return super().dismiss(*args, **kwargs)

    def _release_media(self):
        if self.content:
            release_widget_images(self.content)
        gc.collect()


class MessagePopup(ManagedPopup):
    def __init__(self, title, message, image_path="", **kwargs):
        super().__init__(title=title, size_hint=(0.94, 0.88), auto_dismiss=False, separator_color=ACCENT_COLOR, **kwargs)
        content = BoxLayout(orientation="vertical", spacing=ui_dp(12), padding=ui_dp(16))

        scroll = ScrollView(do_scroll_x=False)
        body = BoxLayout(orientation="vertical", spacing=ui_dp(12), size_hint_y=None)
        body.bind(minimum_height=body.setter("height"))

        message_label = Label(
            text=message,
            color=TEXT_COLOR,
            font_size=ui_sp(16),
            halign="left",
            valign="top",
            size_hint_y=None,
        )
        bind_wrapped_label(message_label, min_height=ui_dp(40), line_height=1.18)
        body.add_widget(message_label)

        if image_exists(image_path):
            img = Image(
                source=optimized_image_source(image_path, "content"),
                size_hint_y=None,
                height=clamp(Window.height * 0.34, ui_dp(220, "media"), ui_dp(320, "media")),
                allow_stretch=True,
                keep_ratio=True,
            )
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
    ui_font_size = NumericProperty(sp(14))
    corner_radius = NumericProperty(dp(12))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.ui_font_size = ui_sp(14)
        self.corner_radius = ui_dp(12)
        self.font_size = self.ui_font_size
        self.bind(texture_size=self._refresh_size)

    def _refresh_size(self, *_):
        self.size = (self.texture_size[0] + ui_dp(24), self.texture_size[1] + ui_dp(14))

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
        self.height = clamp(Window.height * 0.52, ui_dp(340), ui_dp(520))
        self.image_path = image_path
        self.annotation_items = annotation_items
        self.image_area = [0, 0, 0, 0]
        self.tray_area = [0, 0, 0, 0]
        self.chips = []

        with self.canvas.before:
            self._root_bg = Color(*CARD_ALT_COLOR)
            self._root_rect = RoundedRectangle(radius=[ui_dp(18)])
            self._root_line_color = Color(0.18, 0.24, 0.38, 1)
            self._root_line = Line(width=1.1)
            self._image_bg = Color(0.04, 0.06, 0.11, 1)
            self._image_rect = RoundedRectangle(radius=[ui_dp(16)])
            self._tray_bg = Color(0.08, 0.10, 0.18, 1)
            self._tray_rect = RoundedRectangle(radius=[ui_dp(16)])

        self.hint_label = Label(
            text="拖拽标签到图像区域内，拖动时会自动保持在最上层。",
            color=TEXT_COLOR,
            font_size=ui_sp(13),
            size_hint=(None, None),
            halign="left",
            valign="middle",
        )
        self.hint_label.line_height = 1.12
        self.add_widget(self.hint_label)

        self.image_widget = Image(
            source=optimized_image_source(image_path, "detail") if image_exists(image_path) else "",
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(None, None),
        )
        self.add_widget(self.image_widget)

        for item in self.annotation_items:
            chip = DraggableChip(text=item.get("name", ""))
            self.chips.append(chip)
            self.add_widget(chip)

        self.bind(pos=self._refresh_layout, size=self._refresh_layout)
        Clock.schedule_once(self._refresh_layout, 0)

    def bound_chip_position(self, chip, raw_x, raw_y):
        min_x = self.x + ui_dp(12)
        min_y = self.y + ui_dp(12)
        max_x = self.right - chip.width - ui_dp(12)
        max_y = self.top - chip.height - ui_dp(12)
        return min(max(raw_x, min_x), max_x), min(max(raw_y, min_y), max_y)

    def _refresh_layout(self, *_):
        pad = ui_dp(12)
        gap = ui_dp(12)
        content_x = self.x + pad
        content_y = self.y + pad
        content_w = max(self.width - pad * 2, ui_dp(200))
        content_h = max(self.height - pad * 2, ui_dp(260))
        self.hint_label.text_size = (content_w, None)
        hint_h = max(self.hint_label.texture_size[1], ui_dp(30))
        tray_h = self._measure_tray_height(content_w)

        image_y = content_y + tray_h + gap
        image_h = max(content_h - tray_h - gap - hint_h, ui_dp(180))
        self.image_area = [content_x, image_y, content_w, image_h]
        self.tray_area = [content_x, content_y, content_w, tray_h]

        self._root_rect.pos = self.pos
        self._root_rect.size = self.size
        self._root_rect.radius = [ui_dp(18)]
        self._root_line.rounded_rectangle = (self.x, self.y, self.width, self.height, ui_dp(18))

        self._image_rect.pos = (content_x, image_y)
        self._image_rect.size = (content_w, image_h)
        self._image_rect.radius = [ui_dp(16)]

        self._tray_rect.pos = (content_x, content_y)
        self._tray_rect.size = (content_w, tray_h)
        self._tray_rect.radius = [ui_dp(16)]

        self.hint_label.size = (content_w, hint_h)
        self.hint_label.pos = (content_x, image_y + image_h - hint_h)

        self.image_widget.pos = (content_x, image_y)
        self.image_widget.size = (content_w, image_h)

        self._layout_chips()

    def _measure_tray_height(self, width):
        available_width = max(width - ui_dp(20), ui_dp(120))
        x = 0
        rows = 1
        row_height = ui_dp(44)
        for chip in self.chips:
            chip.texture_update()
            chip_width = max(chip.texture_size[0] + ui_dp(24), ui_dp(96))
            chip_height = max(chip.texture_size[1] + ui_dp(14), ui_dp(42))
            if x and x + chip_width > available_width:
                rows += 1
                x = 0
            x += chip_width + ui_dp(10)
            row_height = max(row_height, chip_height)
        return max(ui_dp(110), rows * row_height + max(rows - 1, 0) * ui_dp(10) + ui_dp(26))

    def _layout_chips(self):
        if not self.chips:
            return
        left, bottom, width, _ = self.tray_area
        x = left + ui_dp(10)
        y = bottom + ui_dp(18)
        row_height = 0
        right = left + width - ui_dp(10)

        for chip in self.chips:
            chip.texture_update()
            if x + chip.width > right:
                x = left + ui_dp(10)
                y += row_height + ui_dp(10)
                row_height = 0

            if not chip.placed:
                chip.pos = self.bound_chip_position(chip, x, y)
            else:
                chip.pos = self.bound_chip_position(chip, chip.x, chip.y)

            row_height = max(row_height, chip.height)
            x += chip.width + ui_dp(10)

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


class QuestionPopup(ManagedPopup):
    def __init__(self, question_data, on_submit, **kwargs):
        super().__init__(title=f"交互题 · {question_data.get('time_display', '')}", size_hint=(0.97, 0.95), auto_dismiss=False, separator_color=ACCENT_COLOR, **kwargs)
        self.question_data = question_data
        self.on_submit = on_submit
        self.selected_answer = None
        self.choice_buttons = []
        self.annotation_stage = None
        self._build_content()

    def _build_content(self):
        wrap = BoxLayout(orientation="vertical", spacing=ui_dp(12), padding=ui_dp(16))

        scroll = ScrollView(do_scroll_x=False)
        body = BoxLayout(orientation="vertical", spacing=ui_dp(12), size_hint_y=None)
        body.bind(minimum_height=body.setter("height"))

        title = Label(
            text=self.question_data.get("question", ""),
            color=TEXT_COLOR,
            font_size=ui_sp(18),
            halign="left",
            valign="top",
            size_hint_y=None,
        )
        bind_wrapped_label(title, min_height=ui_dp(36), line_height=1.14)
        body.add_widget(title)

        image_path = self.question_data.get("image", "")
        if image_exists(image_path):
            preview = Image(
                source=optimized_image_source(image_path, "content"),
                size_hint_y=None,
                height=clamp(Window.height * 0.32, ui_dp(180, "media"), ui_dp(280, "media")),
                allow_stretch=True,
                keep_ratio=True,
            )
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

        buttons = BoxLayout(size_hint_y=None, height=ui_dp(46), spacing=ui_dp(10))
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
        self.root_box = BoxLayout(orientation="vertical", spacing=ui_dp(14), padding=ui_dp(16))

        self.header = SurfaceBox(orientation="vertical", spacing=ui_dp(6), padding=ui_dp(16), size_hint_y=None)
        self.header.surface_color = CARD_COLOR
        self.home_title = Label(
            text="[b]医学 AR+VR 教程 Android 版[/b]",
            markup=True,
            color=TEXT_COLOR,
            font_size=ui_sp(24),
            size_hint_y=None,
            halign="left",
            valign="top",
        )
        bind_wrapped_label(self.home_title, min_height=ui_dp(34), line_height=1.08)
        self.home_subtitle = Label(
            text="移动端图像交互学习与答题入口",
            color=MUTED_COLOR,
            font_size=ui_sp(14),
            size_hint_y=None,
            halign="left",
            valign="top",
        )
        bind_wrapped_label(self.home_subtitle, min_height=ui_dp(24), line_height=1.12)
        self.progress_label = Label(
            text="",
            color=ACCENT_COLOR,
            font_size=ui_sp(14),
            size_hint_y=None,
            halign="left",
            valign="top",
        )
        bind_wrapped_label(self.progress_label, min_height=ui_dp(24), line_height=1.12)
        self.header.add_widget(self.home_title)
        self.header.add_widget(self.home_subtitle)
        self.header.add_widget(self.progress_label)
        self.root_box.add_widget(self.header)

        scroll = ScrollView(do_scroll_x=False)
        self.list_wrap = BoxLayout(orientation="vertical", spacing=ui_dp(12), size_hint_y=None)
        self.list_wrap.bind(minimum_height=self.list_wrap.setter("height"))

        for course in self.data_manager.get_all_videos():
            self.list_wrap.add_widget(CourseCard(course, on_open=self._open_course))

        scroll.add_widget(self.list_wrap)
        self.root_box.add_widget(scroll)
        self.add_widget(self.root_box)

        self.header.bind(size=self._refresh_header_layout)
        self.home_title.bind(texture_size=self._refresh_header_layout)
        self.home_subtitle.bind(texture_size=self._refresh_header_layout)
        self.progress_label.bind(texture_size=self._refresh_header_layout)
        self._refresh_header_layout()

    def _refresh_header_layout(self, *_):
        width = max(self.header.width - self.header.padding[0] * 2, ui_dp(200))
        for label in (self.home_title, self.home_subtitle, self.progress_label):
            label.text_size = (width, None)
        self.header.height = (
            self.header.padding[1] * 2
            + self.home_title.height
            + self.home_subtitle.height
            + self.progress_label.height
            + self.header.spacing * 2
        )

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.refresh_progress()

    def refresh_progress(self):
        stats = App.get_running_app().stats
        self.progress_label.text = f"已完成 {stats['answered']} / {stats['total']} 道交互题，答对 {stats['correct']} 道。"
        self._refresh_header_layout()

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
        self.root_box = BoxLayout(orientation="vertical", spacing=ui_dp(12), padding=ui_dp(16))

        self.top_bar = BoxLayout(size_hint_y=None, height=ui_dp(46), spacing=ui_dp(10))
        back_btn = SecondaryButton(text="← 返回课程")
        back_btn.size_hint_x = None
        back_btn.width = ui_dp(136)
        back_btn.bind(on_release=self._go_back)
        self.course_title = Label(
            text="",
            color=TEXT_COLOR,
            font_size=ui_sp(18),
            size_hint_y=None,
            halign="left",
            valign="middle",
        )
        bind_wrapped_label(self.course_title, min_height=ui_dp(28), line_height=1.1)
        self.top_bar.add_widget(back_btn)
        self.top_bar.add_widget(self.course_title)
        self.root_box.add_widget(self.top_bar)
        self.back_btn = back_btn

        self.hero = SurfaceBox(orientation="horizontal", spacing=ui_dp(12), padding=ui_dp(14), size_hint_y=None)
        self.hero.surface_color = CARD_COLOR
        self.hero_image = Image(size_hint=(None, None), allow_stretch=True, keep_ratio=True)
        self.hero.add_widget(self.hero_image)
        self.hero_text_wrap = BoxLayout(orientation="vertical", spacing=ui_dp(8))
        self.hero_desc = Label(
            text="",
            color=TEXT_COLOR,
            font_size=ui_sp(16),
            size_hint_y=None,
            halign="left",
            valign="top",
        )
        bind_wrapped_label(self.hero_desc, min_height=ui_dp(42), line_height=1.16)
        self.hero_meta = Label(
            text="",
            color=ACCENT_COLOR,
            font_size=ui_sp(13),
            size_hint_y=None,
            halign="left",
            valign="middle",
        )
        bind_wrapped_label(self.hero_meta, min_height=ui_dp(22), line_height=1.1)
        self.hero_text_wrap.add_widget(self.hero_desc)
        self.hero_text_wrap.add_widget(self.hero_meta)
        self.hero_text_wrap.add_widget(Label(size_hint_y=1))
        self.hero.add_widget(self.hero_text_wrap)
        self.root_box.add_widget(self.hero)

        self.scroll = ScrollView(do_scroll_x=False)
        self.segment_list = BoxLayout(orientation="vertical", spacing=ui_dp(12), size_hint_y=None)
        self.segment_list.bind(minimum_height=self.segment_list.setter("height"))
        self.scroll.add_widget(self.segment_list)
        self.root_box.add_widget(self.scroll)
        self.add_widget(self.root_box)

        self.top_bar.bind(size=self._refresh_course_layout)
        self.course_title.bind(texture_size=self._refresh_course_layout)
        self.hero.bind(size=self._refresh_course_layout)
        self.hero_desc.bind(texture_size=self._refresh_course_layout)
        self.hero_meta.bind(texture_size=self._refresh_course_layout)
        self._refresh_course_layout()

    def _refresh_course_layout(self, *_):
        top_width = max(self.top_bar.width - self.back_btn.width - self.top_bar.spacing, ui_dp(120))
        self.course_title.text_size = (top_width, None)
        self.top_bar.height = max(self.back_btn.height, self.course_title.height)

        inner_width = max(self.hero.width - self.hero.padding[0] * 2 - self.hero.spacing, ui_dp(240))
        image_width = clamp(inner_width * 0.36, ui_dp(148, "media"), ui_dp(240, "media"))
        image_height = clamp(image_width * 0.66, ui_dp(104, "media"), ui_dp(168, "media"))
        self.hero_image.size = (image_width, image_height)

        text_width = max(inner_width - image_width, ui_dp(120))
        self.hero_desc.text_size = (text_width, None)
        self.hero_meta.text_size = (text_width, None)

        text_height = self.hero_desc.height + self.hero_meta.height + self.hero_text_wrap.spacing
        self.hero.height = max(
            image_height + self.hero.padding[1] * 2,
            text_height + self.hero.padding[1] * 2,
            ui_dp(156),
        )

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
        Clock.schedule_once(self._refresh_course_layout, 0)

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
            MessagePopup("❌ 倒误", message, image_path=question_data.get("answer_image", "")).open()

        home = self.manager.get_screen("home")
        home.refresh_progress()

    def _go_back(self, *_):
        release_widget_images(self.segment_list)
        self.segment_list.clear_widgets()
        self.hero_image.source = ""
        self.current_course = None
        gc.collect()
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "home"


class MedicalTutorialAndroidApp(App):
    def build(self):
        install_runtime_exception_hook()
        Window.clearcolor = BG_COLOR
        Window.softinput_mode = "below_target"
        self.data_manager = VideoDataManager()
        self._log_startup_state()
        total = 0
        for course in self.data_manager.get_all_videos():
            total += sum(1 for item in course.get("video_segments", []) if item.get("has_question"))
        self.stats = {"answered": 0, "correct": 0, "total": total}

        manager = ScreenManager()
        manager.add_widget(HomeScreen(name="home"))
        manager.add_widget(CourseScreen(name="course"))
        self.root_manager = manager
        return manager

    def get_application_name(self):
        return "医学AR+VR教程"

    def _log_startup_state(self):
        missing_assets = self.data_manager.get_missing_assets()
        large_assets = self.data_manager.get_large_assets()
        log_runtime_event(
            "startup",
            platform=platform,
            window=f"{Window.width}x{Window.height}",
            missing_assets=len(missing_assets),
            large_assets=len(large_assets),
        )
        for path in missing_assets:
            log_runtime_event("missing_asset", path=path)
        for path, size_mb in large_assets:
            log_runtime_event("large_asset", path=path, size_mb=size_mb)

    def on_pause(self):
        log_runtime_event("on_pause", current_screen=getattr(self.root, "current", "unknown"))
        gc.collect()
        return True

    def on_resume(self):
        log_runtime_event("on_resume", current_screen=getattr(self.root, "current", "unknown"))
        Clock.schedule_once(self._refresh_after_resume, 0)

    def on_stop(self):
        log_runtime_event("on_stop")
        gc.collect()

    def _refresh_after_resume(self, *_):
        Window.canvas.ask_update()
        if not getattr(self, "root_manager", None):
            return
        try:
            home = self.root_manager.get_screen("home")
            home.refresh_progress()
            course = self.root_manager.get_screen("course")
            course._refresh_course_layout()
        except Exception as exc:
            log_runtime_event("resume_refresh_failed", error=str(exc))


if __name__ == "__main__":
    MedicalTutorialAndroidApp().run()
