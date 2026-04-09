# -*- coding: utf-8 -*-
import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.properties import NumericProperty, StringProperty, ListProperty, ObjectProperty
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.lang import Builder

Builder.load_string('''
<VideoButton>:
    canvas.before:
        Color:
            rgba: 0.086, 0.075, 0.243, 1
        Rectangle:
            pos: self.pos
            size: self.size
    background_normal: ''
    background_color: 0, 0, 0, 0
    markup: True
    font_size: '18sp'
    size_hint_y: None
    height: '80dp'
    
<QuestionPopup>:
    size_hint: 0.95, 0.9
    auto_dismiss: False
    canvas.before:
        Color:
            rgba: 0.102, 0.075, 0.243, 1
        Rectangle:
            pos: self.pos
            size: self.size
    title: ''
    separator_color: 0.914, 0.271, 0.376, 1
    title_color: 0.914, 0.271, 0.376, 1
    title_size: '20sp'
    
<ChoiceButton@ToggleButton>:
    canvas.before:
        Color:
            rgba: (0.086, 0.075, 0.243, 1) if self.state == 'normal' else (0.914, 0.271, 0.376, 1)
        Rectangle:
            pos: self.pos
            size: self.size
    background_normal: ''
    background_down: ''
    color: (0.918, 0.918, 0.918, 1) if self.state == 'normal' else (1, 1, 1, 1)
    font_size: '16sp'
    size_hint_y: None
    height: '50dp'
    markup: True
    
<DraggableLabel>:
    canvas.before:
        Color:
            rgba: 0.914, 0.271, 0.376, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [10]
    color: 1, 1, 1, 1
    font_size: '14sp'
    size_hint: None, None
    size: self.texture_size[0] + 20, self.texture_size[1] + 10
''')

class VideoDataManager:
    def __init__(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.source_path = os.path.join(self.base_path, '源预制件')
        self.videos_data = self._init_videos_data()
        
    def _init_videos_data(self):
        return [
            {
                'id': 1,
                'title': '视频6 - 二尖瓣腱索断裂修复术',
                'description': '学习二尖瓣解剖结构及腱索调整技术',
                'thumbnail': os.path.join(self.source_path, '1.1.png'),
                'questions': [
                    {
                        'id': 1,
                        'video_file': os.path.join(self.source_path, '1-1.mp4'),
                        'time_display': "1'9''",
                        'type': 'annotation',
                        'question': '请在图中标记出二尖瓣A1,A2,A3,P1,P2,P3位置，并指出断裂腱索',
                        'image': os.path.join(self.source_path, '标题', '1.1.png'),
                        'annotation_items': [
                            {'name': 'A1', 'image': os.path.join(self.source_path, '标题', 'A1.png')},
                            {'name': 'A2', 'image': os.path.join(self.source_path, '标题', 'A2.png')},
                            {'name': 'A3', 'image': os.path.join(self.source_path, '标题', 'A3.png')},
                            {'name': 'P1', 'image': os.path.join(self.source_path, '标题', 'P1.png')},
                            {'name': 'P2', 'image': os.path.join(self.source_path, '标题', 'P2.png')},
                            {'name': 'P3', 'image': os.path.join(self.source_path, '标题', 'P3.png')},
                            {'name': '断裂腱索', 'image': os.path.join(self.source_path, '标题', 'duanlie.png')},
                        ],
                        'answer': 'annotation_complete',
                        'explanation': '二尖瓣分为前叶(A)和后叶(P)，各分为三个区段：A1/A2/A3和P1/P2/P3'
                    },
                    {
                        'id': 2,
                        'video_file': os.path.join(self.source_path, '1-2.mp4'),
                        'time_display': "6'40''",
                        'type': 'choice',
                        'question': '根据注水实验，你认为腱索应该如何调整：',
                        'image': os.path.join(self.source_path, '标题', '1.2.png'),
                        'options': [
                            'A. 不调整',
                            'B. 调整短一些',
                            'C. 调整长一些',
                            'D. 还需要进一步注水实验判断'
                        ],
                        'answer': 'B',
                        'explanation': '注水实验显示瓣叶对合不良，需要将腱索调整短一些以改善对合'
                    },
                    {
                        'id': 3,
                        'video_file': os.path.join(self.source_path, '1-3.mp4'),
                        'time_display': "8'15''",
                        'type': 'choice',
                        'question': '你认为瓣叶对合高度是否足够：',
                        'image': os.path.join(self.source_path, '标题', '1.3.png'),
                        'options': [
                            'A. 不够，太短了',
                            'B. 足够',
                            'C. 太长了',
                            'D. 还需要进一步判断'
                        ],
                        'answer': 'B',
                        'explanation': '瓣叶对合高度适中，符合正常标准'
                    }
                ]
            },
            {
                'id': 2,
                'title': '视频17 - 主动脉瓣病变诊断',
                'description': '学习主动脉瓣超声诊断技术',
                'thumbnail': os.path.join(self.source_path, '2.1.png'),
                'questions': [
                    {
                        'id': 1,
                        'video_file': os.path.join(self.source_path, '2-1.mp4'),
                        'time_display': "0'18''",
                        'type': 'choice',
                        'question': '根据所见超声结果，给出诊断：',
                        'image': os.path.join(self.source_path, '标题', '2.1.png'),
                        'options': [
                            'A. 主动脉瓣狭窄',
                            'B. 主动脉关闭不全，中心性反流',
                            'C. 主动脉瓣关闭不全，偏心性反流',
                            'D. 主动脉瓣叶穿孔'
                        ],
                        'answer': 'B',
                        'explanation': '超声显示主动脉瓣关闭不全伴有中心性反流束'
                    },
                    {
                        'id': 2,
                        'video_file': os.path.join(self.source_path, '2-2.mp4'),
                        'time_display': "2'15''",
                        'type': 'annotation',
                        'question': '请标记出主动脉瓣的三个瓣叶名称',
                        'image': os.path.join(self.source_path, '标题', '2.2.png'),
                        'annotation_items': [
                            {'name': '右冠瓣', 'image': os.path.join(self.source_path, '标题', '右.png')},
                            {'name': '左冠瓣', 'image': os.path.join(self.source_path, '标题', '左.png')},
                            {'name': '无冠瓣', 'image': os.path.join(self.source_path, '标题', '无.png')},
                        ],
                        'answer': 'annotation_complete',
                        'explanation': '主动脉瓣有三个瓣叶：右冠瓣、左冠瓣和无冠瓣'
                    }
                ]
            },
            {
                'id': 3,
                'title': '视频31 - 左心耳切除术',
                'description': '学习左心耳切除手术技术',
                'thumbnail': os.path.join(self.source_path, '3.1.png'),
                'questions': [
                    {
                        'id': 1,
                        'video_file': os.path.join(self.source_path, '3-1.mp4'),
                        'time_display': "0'12''",
                        'type': 'annotation',
                        'question': '请分别标注标记线和标记点位置',
                        'image': os.path.join(self.source_path, '标题', '3.1.png'),
                        'annotation_items': [
                            {'name': '标记线', 'image': os.path.join(self.source_path, '标题', 'red.png')},
                            {'name': '标记点', 'image': os.path.join(self.source_path, '标题', 'red.png')},
                        ],
                        'answer': 'annotation_complete',
                        'explanation': '标记线用于指示切除范围，标记点用于定位关键解剖结构'
                    },
                    {
                        'id': 2,
                        'video_file': os.path.join(self.source_path, '3-2.mp4'),
                        'time_display': "0'14''",
                        'type': 'choice',
                        'question': '目前做的操作是：',
                        'image': os.path.join(self.source_path, '标题', '3.2.png'),
                        'options': [
                            'A. 夹闭右心耳',
                            'B. 隔离肺静脉',
                            'C. 切断Marshall韧带',
                            'D. 切除左心耳'
                        ],
                        'answer': 'D',
                        'explanation': '该操作为切除左心耳，用于预防房颤患者血栓形成'
                    }
                ]
            }
        ]
        
    def get_all_videos(self):
        return self.videos_data
    
    def get_video_by_index(self, index):
        if 0 <= index < len(self.videos_data):
            return self.videos_data[index]
        return None


class DraggableLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.touch_offset = (0, 0)
        
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.touch_offset = (touch.x - self.x, touch.y - self.y)
            touch.grab(self)
            return True
        return super().on_touch_down(touch)
        
    def on_touch_move(self, touch):
        if touch.grab_current is self:
            self.x = touch.x - self.touch_offset[0]
            self.y = touch.y - self.touch_offset[1]
            return True
        return super().on_touch_move(touch)
        
    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            return True
        return super().on_touch_up(touch)


class VideoButton(Button):
    video_index = NumericProperty(0)
    video_title = StringProperty('')
    question_count = NumericProperty(0)


class AnnotationArea(BoxLayout):
    def __init__(self, image_path, annotation_items, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.image_path = image_path
        self.annotation_items = annotation_items
        self.draggable_labels = []
        self._init_ui()
        
    def _init_ui(self):
        self.image_widget = Image(source=self.image_path, size_hint=(1, 0.8))
        self.image_widget.allow_stretch = True
        self.image_widget.keep_ratio = True
        self.add_widget(self.image_widget)
        
        items_layout = BoxLayout(size_hint=(1, 0.2), spacing=5, padding=10)
        
        instruction = Label(
            text='拖拽标签到正确位置:',
            size_hint_x=0.3,
            color=(0.5, 0.5, 0.5, 1),
            font_size='14sp'
        )
        items_layout.add_widget(instruction)
        
        for item in self.annotation_items:
            label = DraggableLabel(text=item['name'])
            self.draggable_labels.append((item['name'], label))
            items_layout.add_widget(label)
            
        self.add_widget(items_layout)


class QuestionPopup(Popup):
    def __init__(self, question_data, on_submit, **kwargs):
        super().__init__(**kwargs)
        self.question_data = question_data
        self.on_submit = on_submit
        self.selected_answer = None
        self.annotation_area = None
        
        self.title = f"问题 - {question_data.get('time_display', '')}"
        self._init_content()
        
    def _init_content(self):
        content = BoxLayout(orientation='vertical', spacing=10, padding=15)
        
        question_label = Label(
            text=self.question_data.get('question', ''),
            size_hint_y=0.15,
            halign='left',
            valign='middle',
            text_size=(None, None),
            font_size='16sp',
            markup=True
        )
        question_label.bind(texture_size=question_label.setter('size'))
        content.add_widget(question_label)
        
        image_path = self.question_data.get('image', '')
        if image_path and os.path.exists(image_path):
            img = Image(
                source=image_path,
                size_hint_y=0.35,
                allow_stretch=True,
                keep_ratio=True
            )
            content.add_widget(img)
        
        question_type = self.question_data.get('type', 'choice')
        
        if question_type == 'choice':
            self._create_choice_options(content)
        elif question_type == 'annotation':
            self._create_annotation_area(content)
            
        self._create_buttons(content)
        self.content = content
        
    def _create_choice_options(self, content):
        options_layout = BoxLayout(orientation='vertical', spacing=8, size_hint_y=0.35)
        options = self.question_data.get('options', [])
        
        self.choice_buttons = []
        for option in options:
            btn = ToggleButton(
                text=option,
                group='choices',
                markup=True
            )
            btn.bind(on_press=self._on_choice_selected)
            options_layout.add_widget(btn)
            self.choice_buttons.append(btn)
            
        content.add_widget(options_layout)
        
    def _on_choice_selected(self, instance):
        self.selected_answer = instance.text[0] if instance.text else None
        
    def _create_annotation_area(self, content):
        annotation_items = self.question_data.get('annotation_items', [])
        image_path = self.question_data.get('image', '')
        
        self.annotation_area = AnnotationArea(image_path, annotation_items)
        content.add_widget(self.annotation_area)
        
    def _create_buttons(self, content):
        buttons_layout = BoxLayout(size_hint_y=0.15, spacing=10)
        
        skip_btn = Button(
            text='跳过',
            size_hint_x=0.4,
            background_color=(0.1, 0.1, 0.2, 1),
            font_size='16sp'
        )
        skip_btn.bind(on_press=lambda x: self.dismiss())
        
        submit_btn = Button(
            text='提交答案',
            size_hint_x=0.6,
            background_color=(0.914, 0.271, 0.376, 1),
            font_size='16sp'
        )
        submit_btn.bind(on_press=self._submit)
        
        buttons_layout.add_widget(skip_btn)
        buttons_layout.add_widget(submit_btn)
        content.add_widget(buttons_layout)
        
    def _submit(self, instance):
        question_type = self.question_data.get('type', 'choice')
        
        if question_type == 'choice':
            if not self.selected_answer:
                popup = Popup(
                    title='提示',
                    content=Label(text='请选择一个答案'),
                    size_hint=(0.6, 0.3)
                )
                popup.open()
                return
            answer = self.selected_answer
        else:
            answer = 'annotation_complete'
            
        self.dismiss()
        if self.on_submit:
            self.on_submit(answer, self.question_data)


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_manager = VideoDataManager()
        self._init_ui()
        
    def _init_ui(self):
        layout = BoxLayout(orientation='vertical', spacing=15, padding=20)
        
        layout.add_widget(self._create_header())
        layout.add_widget(self._create_video_list())
        layout.add_widget(self._create_footer())
        
        self.add_widget(layout)
        
    def _create_header(self):
        header = BoxLayout(orientation='vertical', size_hint_y=0.2, spacing=5)
        
        title = Label(
            text='[size=28][b]医学AR+VR学术教程系统[/b][/size]',
            markup=True,
            color=(0.914, 0.271, 0.376, 1)
        )
        header.add_widget(title)
        
        subtitle = Label(
            text='交互式医学手术视频学习平台',
            font_size='14sp',
            color=(0.5, 0.5, 0.5, 1)
        )
        header.add_widget(subtitle)
        
        return header
        
    def _create_video_list(self):
        scroll = ScrollView(size_hint=(1, 0.7))
        
        videos_layout = BoxLayout(orientation='vertical', spacing=15, size_hint_y=None)
        videos_layout.bind(minimum_height=videos_layout.setter('height'))
        
        videos = self.data_manager.get_all_videos()
        
        for i, video in enumerate(videos):
            btn = VideoButton(
                video_index=i,
                video_title=video['title'],
                question_count=len(video.get('questions', [])),
                text=f'[b]{video["title"]}[/b]\n共 {len(video.get("questions", []))} 道题目',
                markup=True
            )
            btn.bind(on_press=self._on_video_selected)
            videos_layout.add_widget(btn)
            
        scroll.add_widget(videos_layout)
        return scroll
        
    def _create_footer(self):
        footer = BoxLayout(size_hint_y=0.1, spacing=10)
        
        self.progress_label = Label(
            text='学习进度: 0/3 视频完成',
            font_size='14sp',
            color=(0.7, 0.7, 0.7, 1)
        )
        footer.add_widget(self.progress_label)
        
        return footer
        
    def _on_video_selected(self, instance):
        video_screen = self.manager.get_screen('video')
        video_screen.load_video(instance.video_index)
        self.manager.current = 'video'


class VideoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_manager = VideoDataManager()
        self.current_video = None
        self.questions_asked = set()
        self.completed_videos = set()
        
        self._init_ui()
        
    def _init_ui(self):
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=15)
        self.add_widget(self.layout)
        
    def on_enter(self):
        pass
        
    def load_video(self, video_index):
        self.current_video = self.data_manager.get_video_by_index(video_index)
        self.questions_asked = set()
        
        self.layout.clear_widgets()
        
        if self.current_video:
            self._build_ui()
            
    def _build_ui(self):
        self.layout.clear_widgets()
        
        header = BoxLayout(size_hint_y=0.1, spacing=10)
        
        back_btn = Button(
            text='← 返回',
            size_hint_x=0.3,
            background_color=(0.1, 0.1, 0.2, 1),
            font_size='16sp'
        )
        back_btn.bind(on_press=self._go_back)
        header.add_widget(back_btn)
        
        title = Label(
            text=self.current_video['title'],
            font_size='16sp',
            color=(0.914, 0.271, 0.376, 1),
            size_hint_x=0.7
        )
        header.add_widget(title)
        
        self.layout.add_widget(header)
        
        video_info = BoxLayout(orientation='vertical', size_hint_y=0.8, spacing=10)
        
        questions = self.current_video.get('questions', [])
        info_text = f"本视频包含 {len(questions)} 道交互问题\n每个问题对应独立视频片段\n\n点击下方按钮开始学习："
        
        info_label = Label(
            text=info_text,
            font_size='18sp',
            halign='center',
            color=(0.8, 0.8, 0.8, 1)
        )
        video_info.add_widget(info_label)
        
        thumbnail_path = self.current_video.get('thumbnail', '')
        if thumbnail_path and os.path.exists(thumbnail_path):
            thumb = Image(
                source=thumbnail_path,
                size_hint_y=0.6,
                allow_stretch=True,
                keep_ratio=True
            )
            video_info.add_widget(thumb)
            
        self.layout.add_widget(video_info)
        
        buttons_layout = BoxLayout(size_hint_y=0.1, spacing=10)
        
        for i, question in enumerate(questions):
            btn = Button(
                text=f"问题{i+1}\n{question.get('time_display', '')}",
                font_size='14sp',
                background_color=(0.086, 0.075, 0.243, 1)
            )
            btn.bind(on_press=lambda x, q=question: self._show_question(q))
            buttons_layout.add_widget(btn)
            
        self.layout.add_widget(buttons_layout)
        
    def _show_question(self, question):
        popup = QuestionPopup(question, self._on_answer_submitted)
        popup.open()
        
    def _on_answer_submitted(self, answer, question_data):
        correct_answer = question_data.get('answer', '')
        is_correct = (answer == correct_answer or answer == 'annotation_complete')
        
        if is_correct:
            result_popup = Popup(
                title='✅ 回答正确！',
                content=Label(
                    text='恭喜你，回答正确！\n\n继续学习更多内容。',
                    font_size='16sp'
                ),
                size_hint=(0.8, 0.4)
            )
        else:
            explanation = question_data.get('explanation', '')
            result_popup = Popup(
                title='❌ 回答错误',
                content=Label(
                    text=f'正确答案: {correct_answer}\n\n{explanation}',
                    font_size='16sp'
                ),
                size_hint=(0.8, 0.5)
            )
            
        result_popup.open()
        
    def _go_back(self, instance):
        self.manager.current = 'main'


class MedicalTutorialApp(App):
    def build(self):
        Window.clearcolor = (0.102, 0.102, 0.18, 1)
        
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(VideoScreen(name='video'))
        
        return sm
        
    def get_application_name(self):
        return '医学AR+VR教程'


if __name__ == '__main__':
    MedicalTutorialApp().run()
