import os
import json

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
                'video_segments': [
                    {
                        'video_file': os.path.join(self.source_path, '1-1.mp4'),
                        'has_question': True,
                        'time_display': "1'9''",
                        'type': 'annotation',
                        'question': '请在图中标记出二尖瓣A1,A2,A3,P1,P2,P3位置，并指出断裂腱索',
                        'image': os.path.join(self.source_path, '1.1.png'),
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
                        'explanation': '二尖瓣分为前叶(A)和后叶(P)，各分为三个区段：A1/A2/A3和P1/P2/P3',
                        'answer_image': os.path.join(self.source_path, '1.1answer.png')
                    },
                    {
                        'video_file': os.path.join(self.source_path, '1-2.mp4'),
                        'has_question': True,
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
                        'video_file': os.path.join(self.source_path, '1-3.mp4'),
                        'has_question': True,
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
                    },
                    {
                        'video_file': os.path.join(self.source_path, '1-4.mp4'),
                        'has_question': False,
                        'time_display': "10'30''",
                        'description': '手术总结与术后观察'
                    }
                ]
            },
            {
                'id': 2,
                'title': '视频17 - 主动脉瓣病变诊断',
                'description': '学习主动脉瓣超声诊断技术',
                'thumbnail': os.path.join(self.source_path, '2.1.png'),
                'video_segments': [
                    {
                        'video_file': os.path.join(self.source_path, '2-1.mp4'),
                        'has_question': True,
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
                        'video_file': os.path.join(self.source_path, '2-2.mp4'),
                        'has_question': True,
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
                    },
                    {
                        'video_file': os.path.join(self.source_path, '2-3.mp4'),
                        'has_question': False,
                        'time_display': "5'20''",
                        'description': '手术方案讨论与总结'
                    }
                ]
            },
            {
                'id': 3,
                'title': '视频31 - 左心耳切除术',
                'description': '学习左心耳切除手术技术',
                'thumbnail': os.path.join(self.source_path, '3.1.png'),
                'video_segments': [
                    {
                        'video_file': os.path.join(self.source_path, '3-1.mp4'),
                        'has_question': True,
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
                        'video_file': os.path.join(self.source_path, '3-2.mp4'),
                        'has_question': True,
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
                    },
                    {
                        'video_file': os.path.join(self.source_path, '3-3.mp4'),
                        'has_question': False,
                        'time_display': "2'45''",
                        'description': '术后处理与注意事项'
                    }
                ]
            }
        ]
        
    def get_all_videos(self):
        return self.videos_data
    
    def get_video(self, video_id):
        if isinstance(video_id, int):
            for video in self.videos_data:
                if video['id'] == video_id + 1:
                    return video
        return None
    
    def get_video_by_index(self, index):
        if 0 <= index < len(self.videos_data):
            return self.videos_data[index]
        return None
