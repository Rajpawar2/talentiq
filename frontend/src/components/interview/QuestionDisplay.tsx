import React from 'react';
import { Badge } from '../common/Badge';
import { Sparkles, HelpCircle, Flame } from 'lucide-react';
import type { InterviewQuestion } from '../../types';

interface QuestionDisplayProps {
  question: InterviewQuestion;
  currentIndex: number;
  totalQuestions: number;
}

export const QuestionDisplay: React.FC<QuestionDisplayProps> = ({
  question,
  currentIndex,
  totalQuestions,
}) => {
  const getDifficultyBadge = (diff: string) => {
    switch (diff.toLowerCase()) {
      case 'easy':
        return <Badge variant="emerald" size="sm">Easy</Badge>;
      case 'hard':
        return <Badge variant="rose" size="sm">Hard</Badge>;
      default:
        return <Badge variant="amber" size="sm">Medium</Badge>;
    }
  };

  return (
    <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800/80 shadow-xl space-y-4">
      {/* Header tags */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
            Question {currentIndex + 1} of {totalQuestions}
          </span>
          <Badge variant="brand" size="sm">{question.category}</Badge>
          {getDifficultyBadge(question.difficulty_level)}
        </div>

        {question.is_follow_up && (
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-indigo-500/15 border border-indigo-500/30 text-indigo-300 text-xs font-semibold animate-pulse">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Adaptive Follow-Up</span>
          </div>
        )}
      </div>

      {/* Main Question Text */}
      <div className="pt-2">
        <h2 className="text-xl sm:text-2xl font-bold text-white leading-relaxed tracking-tight">
          "{question.question_text}"
        </h2>
      </div>

      {/* Adaptive rationale preview if follow up */}
      {question.is_follow_up && question.follow_up_reason && (
        <div className="p-3.5 rounded-xl bg-slate-950/70 border border-indigo-500/20 text-xs text-indigo-200/90 flex items-start gap-2.5">
          <Flame className="w-4 h-4 text-indigo-400 flex-shrink-0 mt-0.5" />
          <div>
            <strong className="font-semibold text-indigo-300">Adaptive Reason: </strong>
            {question.follow_up_reason}
          </div>
        </div>
      )}
    </div>
  );
};
