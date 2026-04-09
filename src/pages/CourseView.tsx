import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/useStore';
import { Segment } from '../data/courses';
import SegmentCard from '../components/SegmentCard';
import PopupModal from '../components/PopupModal';
import { ArrowLeft, Clock } from 'lucide-react';

export default function CourseView() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { courses } = useAppStore();
  const [activeSegment, setActiveSegment] = useState<Segment | null>(null);

  const course = courses.find(c => c.id === id);

  if (!course) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4">课程未找到</h2>
          <button onClick={() => navigate('/')} className="text-brand-accent">返回首页</button>
        </div>
      </div>
    );
  }

  const questionCount = course.video_segments.filter(s => s.has_question).length;

  return (
    <div className="min-h-screen bg-brand-bg pb-12">
      <div className="sticky top-0 z-20 bg-brand-bg/80 backdrop-blur-xl border-b border-slate-800">
        <div className="max-w-3xl mx-auto px-4 h-16 flex items-center gap-4">
          <button 
            onClick={() => navigate('/')}
            className="p-2 -ml-2 rounded-full text-brand-muted hover:bg-slate-800/50 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-6 h-6" />
          </button>
          <h1 className="text-lg font-bold text-brand-text truncate flex-1">
            {course.title}
          </h1>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-5 pt-6 pb-8">
        <div className="bg-brand-card rounded-2xl overflow-hidden border border-slate-700/50 shadow-xl">
          <div className="aspect-video relative bg-slate-800">
            {course.thumbnail && (
              <img src={course.thumbnail} alt={course.title} className="w-full h-full object-cover" />
            )}
            <div className="absolute inset-0 bg-gradient-to-t from-brand-card to-transparent/10" />
          </div>
          <div className="p-6 -mt-8 relative z-10">
            <p className="text-brand-muted leading-relaxed text-sm sm:text-base">
              {course.description}
            </p>
            <div className="mt-4 flex items-center gap-2 text-brand-accent bg-brand-accent/10 w-fit px-3 py-1.5 rounded-lg text-sm font-medium">
              <Clock className="w-4 h-4" />
              <span>共 {course.video_segments.length} 个片段 · {questionCount} 道交互题</span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-5 flex flex-col gap-4 relative">
        <div className="absolute left-[38px] top-6 bottom-6 w-0.5 bg-slate-800 z-0 hidden sm:block"></div>
        
        {course.video_segments.map((segment, idx) => (
          <div key={segment.id} className="relative z-10">
            <SegmentCard 
              segment={segment} 
              index={idx} 
              onOpen={setActiveSegment} 
            />
          </div>
        ))}
      </div>

      {activeSegment && (
        <PopupModal 
          segment={activeSegment} 
          onClose={() => setActiveSegment(null)} 
        />
      )}
    </div>
  );
}