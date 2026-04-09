import { useAppStore } from '../store/useStore';
import CourseCard from '../components/CourseCard';
import { Activity } from 'lucide-react';

export default function HomeView() {
  const { answered, correct, total, courses } = useAppStore();

  return (
    <div className="min-h-screen pb-12">
      {/* Header */}
      <div className="bg-brand-card border-b border-slate-800 px-5 pt-12 pb-8 sticky top-0 z-10">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            医学 AR+VR 教程 Android 版
          </h1>
          <p className="text-brand-muted mt-2 text-sm sm:text-base">
            移动端图像交互学习与答题入口
          </p>
          
          {/* Progress */}
          <div className="mt-6 flex items-center gap-3 bg-brand-bg rounded-xl p-4 border border-slate-700/50">
            <div className="bg-brand-accent/20 p-2.5 rounded-lg text-brand-accent">
              <Activity className="w-6 h-6" />
            </div>
            <div>
              <p className="text-brand-text font-medium text-sm">
                已完成 {answered} / {total} 道交互题
              </p>
              <p className="text-brand-success text-xs mt-1 font-medium">
                答对 {correct} 道题目
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Course List */}
      <div className="max-w-3xl mx-auto px-5 mt-6 flex flex-col gap-4">
        {courses.map(course => (
          <CourseCard key={course.id} course={course} />
        ))}
      </div>
    </div>
  );
}
