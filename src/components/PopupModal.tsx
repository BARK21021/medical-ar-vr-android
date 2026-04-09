import { useState } from 'react';
import { Segment } from '../data/courses';
import { useAppStore } from '../store/useStore';
import { X, CheckCircle2, XCircle } from 'lucide-react';
import clsx from 'clsx';
import AnnotationStage from './AnnotationStage';

interface PopupModalProps {
  segment: Segment;
  onClose: () => void;
}

export default function PopupModal({ segment, onClose }: PopupModalProps) {
  const { incrementAnswered } = useAppStore();
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [isAnnotationComplete, setIsAnnotationComplete] = useState(false);
  
  const [step, setStep] = useState<'question' | 'feedback'>(segment.has_question ? 'question' : 'feedback');
  const [isCorrect, setIsCorrect] = useState(false);

  const handleSubmit = () => {
    if (segment.question_type === 'multiple_choice') {
      if (selectedOption === null) {
        alert("请先选择一个答案！");
        return;
      }
      const correct = selectedOption === segment.correct_answer;
      setIsCorrect(correct);
      incrementAnswered(correct, segment.id);
      setStep('feedback');
    } else if (segment.question_type === 'annotation') {
      if (!isAnnotationComplete) {
        alert("请将所有标签拖放到图像区域内！");
        return;
      }
      setIsCorrect(true);
      incrementAnswered(true, segment.id);
      setStep('feedback');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-brand-card w-full max-w-lg rounded-3xl shadow-2xl border border-slate-700/50 flex flex-col max-h-[90vh] overflow-hidden animate-in zoom-in-95 duration-200">
        
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800">
          <h2 className="text-lg font-bold text-brand-text truncate pr-4">
            {segment.has_question ? (step === 'feedback' ? '作答结果' : '交互题') : '知识片段'} 
            <span className="text-brand-muted font-normal ml-2">· {segment.time_display}</span>
          </h2>
          <button 
            onClick={onClose}
            className="p-2 -mr-2 text-brand-muted hover:text-white hover:bg-slate-800 rounded-full transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="overflow-y-auto flex-1 p-6 flex flex-col gap-6">
          {step === 'question' && segment.has_question && (
            <>
              <p className="text-lg text-brand-text leading-relaxed font-medium">
                {segment.question}
              </p>
              
              {segment.question_type === 'multiple_choice' && segment.image && (
                <div className="rounded-xl overflow-hidden bg-slate-900 border border-slate-800 aspect-video">
                  <img src={segment.image} alt="题目配图" className="w-full h-full object-contain" />
                </div>
              )}

              {segment.question_type === 'multiple_choice' && segment.options && (
                <div className="flex flex-col gap-3">
                  {segment.options.map((opt, idx) => (
                    <button
                      key={idx}
                      onClick={() => setSelectedOption(idx)}
                      className={clsx(
                        "w-full text-left px-5 py-4 rounded-xl border transition-all duration-200",
                        selectedOption === idx 
                          ? "border-brand-accent bg-brand-accent/10 text-brand-accent" 
                          : "border-slate-700 bg-slate-800/50 text-brand-text hover:border-slate-500 hover:bg-slate-700"
                      )}
                    >
                      <span className="font-bold mr-3">{String.fromCharCode(65 + idx)}.</span>
                      {opt.replace(/^[A-D]\.\s*/, '')}
                    </button>
                  ))}
                </div>
              )}

              {segment.question_type === 'annotation' && segment.annotations && (
                <AnnotationStage 
                  imagePath={segment.image || ''} 
                  annotations={segment.annotations} 
                  onComplete={setIsAnnotationComplete} 
                />
              )}
            </>
          )}

          {step === 'feedback' && (
            <div className="flex flex-col gap-6 animate-in slide-in-from-bottom-4 duration-300">
              {segment.has_question && (
                <div className={clsx(
                  "flex items-center gap-3 p-4 rounded-2xl border",
                  isCorrect ? "bg-brand-success/10 border-brand-success/20 text-brand-success" : "bg-brand-danger/10 border-brand-danger/20 text-brand-danger"
                )}>
                  {isCorrect ? <CheckCircle2 className="w-8 h-8" /> : <XCircle className="w-8 h-8" />}
                  <div>
                    <h3 className="font-bold text-lg">{isCorrect ? '回答正确' : '回答错误'}</h3>
                    {!isCorrect && segment.correct_answer !== undefined && segment.options && (
                      <p className="text-sm mt-1 opacity-90">
                        正确答案：{segment.options[segment.correct_answer]}
                      </p>
                    )}
                  </div>
                </div>
              )}

              <p className="text-base text-brand-text leading-relaxed">
                {segment.has_question ? segment.feedback : segment.description}
              </p>

              {(segment.answer_image || (!segment.has_question && segment.image)) && (
                <div className="rounded-xl overflow-hidden bg-slate-900 border border-slate-800 aspect-video">
                  <img 
                    src={segment.answer_image || segment.image} 
                    alt="解析配图" 
                    className="w-full h-full object-contain" 
                  />
                </div>
              )}
            </div>
          )}
        </div>

        <div className="p-4 border-t border-slate-800 bg-slate-900/50 flex justify-end gap-3">
          {step === 'question' ? (
            <>
              <button 
                onClick={onClose}
                className="px-6 py-3 rounded-xl font-semibold text-brand-text bg-slate-800 hover:bg-slate-700 transition-colors"
              >
                跳过
              </button>
              <button 
                onClick={handleSubmit}
                className="px-6 py-3 rounded-xl font-semibold text-white bg-brand-accent hover:bg-brand-accentHover transition-colors shadow-lg shadow-brand-accent/20"
              >
                提交答案
              </button>
            </>
          ) : (
            <button 
              onClick={onClose}
              className="px-6 py-3 rounded-xl font-semibold text-white bg-brand-accent hover:bg-brand-accentHover transition-colors shadow-lg shadow-brand-accent/20 w-full sm:w-auto"
            >
              完成
            </button>
          )}
        </div>
        
      </div>
    </div>
  );
}