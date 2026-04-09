export type Segment = {
  id: string;
  time: number;
  time_display: string;
  description?: string;
  image?: string;
  video_file?: string;
  has_question?: boolean;
  question_type?: 'multiple_choice' | 'annotation';
  question?: string;
  options?: string[];
  correct_answer?: number;
  feedback?: string;
  answer_image?: string;
  annotations?: { name: string; image?: string }[];
};

export type Course = {
  id: string;
  title: string;
  description: string;
  thumbnail: string;
  video_segments: Segment[];
};

export const coursesData: Course[] = [
  {
    id: "course-1",
    title: "视频6 - 二尖瓣腱索断裂修复术",
    description: "学习二尖瓣解剖结构及腱索调整技术",
    thumbnail: "/assets/源预制件/1.1.png",
    video_segments: [
      {
        id: "seg-1-1",
        time: 69,
        time_display: "1'9''",
        has_question: true,
        question_type: "annotation",
        question: "请在图中标记出二尖瓣A1,A2,A3,P1,P2,P3位置，并指出断裂腱索",
        image: "/assets/源预制件/1.1.png",
        video_file: "/assets/源预制件/1-1.mp4",
        annotations: [
          { name: "A1", image: "/assets/源预制件/标题/A1.png" },
          { name: "A2", image: "/assets/源预制件/标题/A2.png" },
          { name: "A3", image: "/assets/源预制件/标题/A3.png" },
          { name: "P1", image: "/assets/源预制件/标题/P1.png" },
          { name: "P2", image: "/assets/源预制件/标题/P2.png" },
          { name: "P3", image: "/assets/源预制件/标题/P3.png" },
          { name: "断裂腱索", image: "/assets/源预制件/标题/duanlie.png" },
        ],
        feedback: "二尖瓣分为前叶(A)和后叶(P)，各分为三个区段：A1/A2/A3和P1/P2/P3",
        answer_image: "/assets/源预制件/1.1answer.png",
      },
      {
        id: "seg-1-2",
        time: 400,
        time_display: "6'40''",
        has_question: true,
        question_type: "multiple_choice",
        question: "根据注水实验，你认为腱索应该如何调整：",
        image: "/assets/源预制件/标题/1.2.png",
        video_file: "/assets/源预制件/1-2.mp4",
        options: [
          "A. 不调整",
          "B. 调整短一些",
          "C. 调整长一些",
          "D. 还需要进一步注水实验判断"
        ],
        correct_answer: 1, // 'B'
        feedback: "注水实验显示瓣叶对合不良，需要将腱索调整短一些以改善对合",
      },
      {
        id: "seg-1-3",
        time: 495,
        time_display: "8'15''",
        has_question: true,
        question_type: "multiple_choice",
        question: "你认为瓣叶对合高度是否足够：",
        image: "/assets/源预制件/标题/1.3.png",
        video_file: "/assets/源预制件/1-3.mp4",
        options: [
          "A. 不够，太短了",
          "B. 足够",
          "C. 太长了",
          "D. 还需要进一步判断"
        ],
        correct_answer: 1, // 'B'
        feedback: "瓣叶对合高度适中，符合正常标准",
      },
      {
        id: "seg-1-4",
        time: 630,
        time_display: "10'30''",
        has_question: false,
        description: "手术总结与术后观察",
        video_file: "/assets/源预制件/1-4.mp4",
      }
    ]
  },
  {
    id: "course-2",
    title: "视频17 - 主动脉瓣病变诊断",
    description: "学习主动脉瓣超声诊断技术",
    thumbnail: "/assets/源预制件/2.1.png",
    video_segments: [
      {
        id: "seg-2-1",
        time: 18,
        time_display: "0'18''",
        has_question: true,
        question_type: "multiple_choice",
        question: "根据所见超声结果，给出诊断：",
        image: "/assets/源预制件/标题/2.1.png",
        video_file: "/assets/源预制件/2-1.mp4",
        options: [
          "A. 主动脉瓣狭窄",
          "B. 主动脉关闭不全，中心性反流",
          "C. 主动脉瓣关闭不全，偏心性反流",
          "D. 主动脉瓣叶穿孔"
        ],
        correct_answer: 1, // 'B'
        feedback: "超声显示主动脉瓣关闭不全伴有中心性反流束",
      },
      {
        id: "seg-2-2",
        time: 135,
        time_display: "2'15''",
        has_question: true,
        question_type: "annotation",
        question: "请标记出主动脉瓣的三个瓣叶名称",
        image: "/assets/源预制件/标题/2.2.png",
        video_file: "/assets/源预制件/2-2.mp4",
        annotations: [
          { name: "右冠瓣", image: "/assets/源预制件/标题/右.png" },
          { name: "左冠瓣", image: "/assets/源预制件/标题/左.png" },
          { name: "无冠瓣", image: "/assets/源预制件/标题/无.png" },
        ],
        feedback: "主动脉瓣有三个瓣叶：右冠瓣、左冠瓣和无冠瓣",
      },
      {
        id: "seg-2-3",
        time: 320,
        time_display: "5'20''",
        has_question: false,
        description: "手术方案讨论与总结",
        video_file: "/assets/源预制件/2-3.mp4",
      }
    ]
  },
  {
    id: "course-3",
    title: "视频31 - 左心耳切除术",
    description: "学习左心耳切除手术技术",
    thumbnail: "/assets/源预制件/3.1.png",
    video_segments: [
      {
        id: "seg-3-1",
        time: 12,
        time_display: "0'12''",
        has_question: true,
        question_type: "annotation",
        question: "请分别标注标记线和标记点位置",
        image: "/assets/源预制件/标题/3.1.png",
        video_file: "/assets/源预制件/3-1.mp4",
        annotations: [
          { name: "标记线", image: "/assets/源预制件/标题/red.png" },
          { name: "标记点", image: "/assets/源预制件/标题/red.png" },
        ],
        feedback: "标记线用于指示切除范围，标记点用于定位关键解剖结构",
      },
      {
        id: "seg-3-2",
        time: 14,
        time_display: "0'14''",
        has_question: true,
        question_type: "multiple_choice",
        question: "目前做的操作是：",
        image: "/assets/源预制件/标题/3.2.png",
        video_file: "/assets/源预制件/3-2.mp4",
        options: [
          "A. 夹闭右心耳",
          "B. 隔离肺静脉",
          "C. 切断Marshall韧带",
          "D. 切除左心耳"
        ],
        correct_answer: 3, // 'D'
        feedback: "该操作为切除左心耳，用于预防房颤患者血栓形成",
      },
      {
        id: "seg-3-3",
        time: 165,
        time_display: "2'45''",
        has_question: false,
        description: "术后处理与注意事项",
        video_file: "/assets/源预制件/3-3.mp4",
      }
    ]
  }
];
