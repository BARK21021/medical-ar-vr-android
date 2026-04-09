import { Link } from 'react-router-dom';
import { Course } from '../data/courses';
import { ChevronRight, PlayCircle } from 'lucide-react';

export default function CourseCard({ course }: { course: Course }) {
  const questionCount = course.video_segments.filter(s => s.has_question).length;
  
  return (
    <Link 
      to={`/course/${course.id}`}
      className="flex gap-4 p-4 rounded-2xl bg-brand-card border border-slate-700/50 active:scale-[0.98] transition-transform hover:shadow-lg shadow-slate-900/20"
    >
      <div className="w-28 sm:w-36 shrink-0 aspect-[3/4] sm:aspect-video rounded-xl overflow-hidden bg-slate-800 flex items-center justify-center relative">
        {course.thumbnail ? (
          <img 
            src={course.thumbnail} 
            alt={course.title} 
            className="w-full h-full object-cover"
          />
        ) : (
          <PlayCircle className="text-slate-600 w-10 h-10" />
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
      </div>
      
      <div className="flex-1 flex flex-col justify-between py-1">
        <div>
          <h3 className="font-bold text-lg sm:text-xl text-brand-text line-clamp-2">
            {course.title}
          </h3>
          <p className="text-brand-muted text-sm sm:text-base mt-2 line-clamp-2 leading-relaxed">
            {course.description}
          </p>
        </div>
        
        <div className="mt-4 flex items-center justify-between">
          <span className="text-xs sm:text-sm font-medium text-brand-accent bg-brand-accent/10 px-2.5 py-1 rounded-md">
            共 {course.video_segments.length} 个片段 · {questionCount} 道交互题
          </span>
          <ChevronRight className="w-5 h-5 text-brand-muted" />
        </div>
      </div>
    </Link>
  );
}