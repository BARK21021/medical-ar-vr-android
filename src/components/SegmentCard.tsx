import { Segment } from '../data/courses';
import { PlayCircle, HelpCircle, ChevronRight } from 'lucide-react';
import clsx from 'clsx';

interface SegmentCardProps {
  segment: Segment;
  index: number;
  onOpen: (segment: Segment) => void;
}

export default function SegmentCard({ segment, index, onOpen }: SegmentCardProps) {
  const isQuestion = segment.has_question;

  return (
    <div 
      className="bg-brand-cardAlt border border-slate-700/50 rounded-2xl overflow-hidden cursor-pointer active:scale-[0.98] transition-transform"
      onClick={() => onOpen(segment)}
    >
      <div className="px-4 py-3 flex items-center justify-between border-b border-slate-800 bg-slate-800/20">
        <div className="flex items-center gap-3">
          <div className={clsx(
            "w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm",
            isQuestion ? "bg-brand-accent/20 text-brand-accent" : "bg-brand-success/20 text-brand-success"
          )}>
            {index + 1}
          </div>
          <span className="font-semibold text-brand-text">
            片段 {index + 1} · <span className="text-brand-muted font-normal">{segment.time_display}</span>
          </span>
        </div>
        <span className={clsx(
          "text-xs font-bold px-2 py-1 rounded-md",
          isQuestion ? "bg-brand-accent text-white" : "bg-brand-success/20 text-brand-success"
        )}>
          {isQuestion ? "交互题" : "知识片段"}
        </span>
      </div>

      <div className="p-4 flex gap-4">
        <div className="w-24 sm:w-32 aspect-square rounded-xl overflow-hidden bg-brand-bg shrink-0 relative border border-slate-700/30">
          {segment.image ? (
            <img 
              src={segment.image} 
              alt="片段配图" 
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="absolute inset-0 flex items-center justify-center text-slate-600">
              {isQuestion ? <HelpCircle className="w-8 h-8" /> : <PlayCircle className="w-8 h-8" />}
            </div>
          )}
        </div>
        
        <div className="flex-1 flex flex-col justify-between">
          <p className="text-sm sm:text-base text-brand-muted line-clamp-3 leading-relaxed">
            {segment.question || segment.description || "继续学习本片段内容。"}
          </p>
          <div className="flex justify-end mt-3">
            <button 
              className={clsx(
                "px-4 py-2 rounded-xl text-sm font-semibold flex items-center gap-1.5 transition-colors",
                isQuestion 
                  ? "bg-brand-accent text-white hover:bg-brand-accentHover" 
                  : "bg-slate-700 text-brand-text hover:bg-slate-600"
              )}
            >
              {isQuestion ? "开始答题" : "查看内容"}
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}