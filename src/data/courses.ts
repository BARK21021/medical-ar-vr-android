export type Segment = {
  id: string;
  time: number;
  time_display: string;
  description?: string;
  image?: string;
  has_question?: boolean;
  question_type?: 'multiple_choice' | 'annotation';
  question?: string;
  options?: string[];
  correct_answer?: number;
  feedback?: string;
  answer_image?: string;
  annotations?: { name: string }[];
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
    title: "注射胰岛素",
    description: "学习糖尿病患者注射胰岛素的规范流程与常见注意事项。",
    thumbnail: "/assets/source/标题/1.1.png",
    video_segments: [
      {
        id: "seg-1-1",
        time: 0,
        time_display: "0:00",
        description: "患者准备注射前的用物核对。",
        image: "/assets/source/1.1 (1).png",
      },
      {
        id: "seg-1-2",
        time: 14,
        time_display: "0:14",
        has_question: true,
        question_type: "multiple_choice",
        question: "注射胰岛素前，首先需要确认什么？",
        options: ["针头是否已经丢弃", "患者身份与药物剂量", "病房空调温度", "手机是否静音"],
        correct_answer: 1,
        feedback: "任何注射操作前都应核对患者身份、药物名称与剂量，避免给药错误。",
        answer_image: "/assets/source/1.2 (2).png",
        image: "/assets/source/1.2 (1).png",
      },
      {
        id: "seg-1-3",
        time: 32,
        time_display: "0:32",
        description: "完成皮肤消毒，保持注射部位清洁。",
        image: "/assets/source/1.3 (1).png",
      },
      {
        id: "seg-1-4",
        time: 45,
        time_display: "0:45",
        has_question: true,
        question_type: "annotation",
        question: "请将“腹部脐周 5 厘米外区域”和“上臂外侧”拖拽到推荐注射部位。",
        annotations: [
          { name: "腹部脐周 5 厘米外区域" },
          { name: "上臂外侧" },
        ],
        feedback: "腹部脐周外侧、上臂外侧、大腿前外侧都是常用注射区域，需要轮换注射点。",
        answer_image: "/assets/source/1.4 (2).png",
        image: "/assets/source/1.4 (1).png",
      },
    ],
  },
  {
    id: "course-2",
    title: "血糖仪测血糖",
    description: "掌握便携式血糖仪测量流程与结果判读。",
    thumbnail: "/assets/source/标题/2.1.png",
    video_segments: [
      {
        id: "seg-2-1",
        time: 0,
        time_display: "0:00",
        description: "准备试纸、采血针与血糖仪。",
        image: "/assets/source/2.1 (1).png",
      },
      {
        id: "seg-2-2",
        time: 18,
        time_display: "0:18",
        has_question: true,
        question_type: "multiple_choice",
        question: "血糖测试前不应忽略哪一步？",
        options: ["清洁并擦干手指", "播放背景音乐", "调暗病房灯光", "先记录患者体重"],
        correct_answer: 0,
        feedback: "清洁并擦干采血部位可以避免污染样本与影响测试结果。",
        answer_image: "/assets/source/2.2 (2).png",
        image: "/assets/source/2.2 (1).png",
      },
      {
        id: "seg-2-3",
        time: 35,
        time_display: "0:35",
        description: "将血滴滴加至试纸指定区域，等待仪器读数。",
        image: "/assets/source/2.3 (1).png",
      },
      {
        id: "seg-2-4",
        time: 50,
        time_display: "0:50",
        has_question: true,
        question_type: "annotation",
        question: "将“试纸插入口”和“结果显示区”拖拽到血糖仪对应部位。",
        annotations: [
          { name: "试纸插入口" },
          { name: "结果显示区" },
        ],
        feedback: "熟悉血糖仪关键部件有助于快速完成监测并减少误操作。",
        answer_image: "/assets/source/2.4 (2).png",
        image: "/assets/source/2.4 (1).png",
      },
    ],
  },
  {
    id: "course-3",
    title: "咳痰训练",
    description: "通过动作示范学习有效咳嗽与排痰训练步骤。",
    thumbnail: "/assets/source/标题/3.1.png",
    video_segments: [
      {
        id: "seg-3-1",
        time: 0,
        time_display: "0:00",
        description: "调整坐位并进行腹式呼吸准备。",
        image: "/assets/source/3.1 (1).png",
      },
      {
        id: "seg-3-2",
        time: 20,
        time_display: "0:20",
        has_question: true,
        question_type: "multiple_choice",
        question: "有效咳嗽前应先进行哪项准备？",
        options: ["快速连续浅呼吸", "深吸气后短暂停顿", "立刻用力咳嗽", "完全屏住呼吸 10 秒"],
        correct_answer: 1,
        feedback: "深吸气并短暂停顿可以帮助肺泡扩张，为后续有效咳嗽创造条件。",
        answer_image: "/assets/source/3.2 (2).png",
        image: "/assets/source/3.2 (1).png",
      },
      {
        id: "seg-3-3",
        time: 40,
        time_display: "0:40",
        description: "双手保护手术切口或胸腹部后进行排痰。",
        image: "/assets/source/3.3 (1).png",
      },
      {
        id: "seg-3-4",
        time: 58,
        time_display: "0:58",
        has_question: true,
        question_type: "annotation",
        question: "将“腹式呼吸手位”和“前倾坐位”拖拽到示意图中。",
        annotations: [
          { name: "腹式呼吸手位" },
          { name: "前倾坐位" },
        ],
        feedback: "正确体位和手位能增强咳痰训练效果，并提升患者舒适度。",
        answer_image: "/assets/source/3.4 (2).png",
        image: "/assets/source/3.4 (1).png",
      },
    ],
  },
];
