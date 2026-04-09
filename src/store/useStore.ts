import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { coursesData, Course } from '../data/courses';

interface AppState {
  answered: number;
  correct: number;
  total: number;
  completedSegments: string[];
  incrementAnswered: (isCorrect: boolean, segmentId: string) => void;
  resetProgress: () => void;
  courses: Course[];
}

const totalQuestions = coursesData.reduce((acc, course) => {
  return acc + course.video_segments.filter(seg => seg.has_question).length;
}, 0);

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      answered: 0,
      correct: 0,
      total: totalQuestions,
      completedSegments: [],
      courses: coursesData,
      incrementAnswered: (isCorrect, segmentId) => set((state) => {
        // Prevent answering the same question multiple times
        if (state.completedSegments.includes(segmentId)) return state;
        return {
          answered: state.answered + 1,
          correct: state.correct + (isCorrect ? 1 : 0),
          completedSegments: [...state.completedSegments, segmentId],
        };
      }),
      resetProgress: () => set({ answered: 0, correct: 0, completedSegments: [] }),
    }),
    {
      name: 'medical-tutorial-progress',
    }
  )
);
