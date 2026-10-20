import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Mic,
  FileText,
  Clock,
  Send,
  FastForward,
  LogOut,
  Sparkles,
  AlertCircle,
  CheckCircle2,
  Volume2
} from 'lucide-react';
import { Button } from '../components/common/Button';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { AvatarInterviewer } from '../components/interview/AvatarInterviewer';
import { QuestionDisplay } from '../components/interview/QuestionDisplay';
import { AudioRecorder } from '../components/interview/AudioRecorder';
import { SpeechFeedback } from '../components/interview/SpeechFeedback';
import { interviewsApi } from '../api/interviews';
import type { InterviewSession, InterviewQuestion, AnswerResponse } from '../types';
import { useToast } from '../context/ToastContext';
import { Skeleton } from '../components/common/FeedbackStates';

export const InterviewRoomPage: React.FC = () => {
  const { interviewId } = useParams<{ interviewId: string }>();
  const navigate = useNavigate();
  const { addToast } = useToast();

  const [session, setSession] = useState<InterviewSession | null>(null);
  const [questions, setQuestions] = useState<InterviewQuestion[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);

  // Answering states
  const [answerMode, setAnswerMode] = useState<'text' | 'voice'>('text');
  const [answerText, setAnswerText] = useState('');
  const [audioDuration, setAudioDuration] = useState<number | undefined>(undefined);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [lastAnswerResponse, setLastAnswerResponse] = useState<AnswerResponse | null>(null);

  // Avatar state
  const [avatarStatus, setAvatarStatus] = useState<'idle' | 'speaking' | 'listening' | 'evaluating'>('idle');

  // Elapsed timer
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  // WebSocket reference
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!interviewId) return;
    loadInterviewRoom();

    // Start timer
    const interval = setInterval(() => {
      setElapsedSeconds((prev) => prev + 1);
    }, 1000);

    // Initialize WebSocket connection
    const wsUrl = `ws://localhost:8000/ws/interview/${interviewId}`;
    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.event === 'answer_evaluated') {
            // Next question event
          }
        } catch {
          // Ignore parse errors
        }
      };

      ws.onerror = () => {
        console.warn('WebSocket connection not reachable, continuing in resilient HTTP mode');
      };
    } catch {
      // Graceful fallback
    }

    return () => {
      clearInterval(interval);
      if (wsRef.current) wsRef.current.close();
    };
  }, [interviewId]);

  const loadInterviewRoom = async () => {
    if (!interviewId) return;
    try {
      const detail = await interviewsApi.getInterviewById(interviewId);
      setSession(detail);
      setCurrentIndex(detail.current_question_index);

      if (detail.status === 'created') {
        // Mark as started
        await interviewsApi.startInterview(interviewId);
      } else if (detail.status === 'completed') {
        // Already finished
        navigate(`/reports/${interviewId}`);
        return;
      }

      const qList = await interviewsApi.getQuestions(interviewId);
      setQuestions(qList);

      // Speaking simulation on load
      setAvatarStatus('speaking');
      setTimeout(() => {
        setAvatarStatus('idle');
      }, 2500);
    } catch (err) {
      addToast('Failed to load interview room.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleVoiceTranscription = (transcript: string, durationSecs: number) => {
    setAnswerText(transcript);
    setAudioDuration(durationSecs);
    setAnswerMode('text'); // Switch to text to allow reviewing before submit
  };

  const handleSubmitAnswer = async () => {
    if (!answerText.trim() || answerText.trim().length < 3) {
      addToast('Please provide a substantive answer before submitting.', 'warning');
      return;
    }

    const currentQ = questions[currentIndex];
    if (!currentQ || !interviewId) return;

    setIsSubmitting(true);
    setAvatarStatus('evaluating');

    try {
      const ansRes = await interviewsApi.submitAnswer(interviewId, {
        question_id: currentQ.id,
        answer_text: answerText.trim(),
        input_mode: answerMode,
        audio_duration_seconds: audioDuration,
      });

      setLastAnswerResponse(ansRes);
      addToast('Answer evaluated!', 'success');

      // Check if this was the last question
      const nextIdx = currentIndex + 1;
      if (nextIdx >= (session?.total_questions || questions.length)) {
        addToast('Interview completed! Generating executive report...', 'success');
        navigate(`/reports/${interviewId}`);
        return;
      }

      // Refresh question sequence to fetch any newly adapted questions!
      const updatedQList = await interviewsApi.getQuestions(interviewId);
      setQuestions(updatedQList);
      setCurrentIndex(nextIdx);

      // Reset input form for next question
      setAnswerText('');
      setAudioDuration(undefined);

      // Avatar speaks next question
      setAvatarStatus('speaking');
      setTimeout(() => {
        setAvatarStatus('idle');
      }, 2000);
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Failed to submit answer.';
      addToast(msg, 'error');
      setAvatarStatus('idle');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSkipQuestion = async () => {
    const nextIdx = currentIndex + 1;
    if (nextIdx >= (session?.total_questions || questions.length)) {
      handleEndInterview();
      return;
    }
    setCurrentIndex(nextIdx);
    setAnswerText('');
    addToast('Question skipped.', 'info');
  };

  const handleEndInterview = async () => {
    if (!interviewId) return;
    setIsSubmitting(true);
    try {
      await interviewsApi.completeInterview(interviewId);
      addToast('Interview concluded. Navigating to report...', 'success');
      navigate(`/reports/${interviewId}`);
    } catch (err) {
      addToast('Error ending interview session.', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const formatElapsed = (sec: number) => {
    const mins = Math.floor(sec / 60);
    const secs = sec % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-12 w-96 rounded-xl" />
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          <Skeleton className="lg:col-span-5 h-[450px] rounded-2xl" />
          <Skeleton className="lg:col-span-7 h-[450px] rounded-2xl" />
        </div>
      </div>
    );
  }

  const currentQ = questions[currentIndex] || {
    id: 'placeholder',
    question_index: currentIndex + 1,
    question_text: 'Describe an end-to-end technical project you developed and its core architectural trade-offs.',
    category: 'Technical',
    difficulty_level: 'Medium',
    is_follow_up: false,
  };

  const totalQ = session?.total_questions || questions.length || 5;
  const progressPct = Math.round(((currentIndex) / totalQ) * 100);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Room Header & Controls */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
            <h1 className="text-xl sm:text-2xl font-extrabold text-white tracking-tight">
              {session?.title || 'Live Interview Simulation'}
            </h1>
          </div>
          <p className="text-xs text-slate-400">
            {session?.role} • {session?.interview_type} • Difficulty: {session?.difficulty}
          </p>
        </div>

        <div className="flex items-center gap-4">
          {/* Timer Clock */}
          <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs font-mono font-bold text-slate-200">
            <Clock className="w-3.5 h-3.5 text-brand-400" />
            <span>{formatElapsed(elapsedSeconds)}</span>
          </div>

          {/* End Interview Button */}
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={handleEndInterview}
            leftIcon={<LogOut className="w-3.5 h-3.5 text-rose-400" />}
            className="border-slate-800 text-slate-300 hover:text-rose-400 hover:border-rose-500/40"
          >
            End Interview
          </Button>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="space-y-1.5">
        <div className="flex justify-between text-xs font-medium text-slate-400">
          <span>Interview Progress</span>
          <span className="font-bold text-white">Question {currentIndex + 1} of {totalQ} ({progressPct}%)</span>
        </div>
        <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden border border-slate-800">
          <div
            className="bg-gradient-to-r from-brand-600 to-indigo-500 h-full rounded-full transition-all duration-500"
            style={{ width: `${progressPct}%` }}
          />
        </div>
      </div>

      {/* Main Room Layout: Left (Avatar & Question) vs Right (Answer & Speech) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column (5 Cols) */}
        <div className="lg:col-span-5 space-y-6">
          <AvatarInterviewer
            status={avatarStatus}
            interviewerName="TalentIQ AI Evaluator"
            role="Staff Panel Lead"
          />

          <QuestionDisplay
            question={currentQ}
            currentIndex={currentIndex}
            totalQuestions={totalQ}
          />
        </div>

        {/* Right Column (7 Cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Answer Mode Toggle */}
          <div className="flex items-center justify-between p-1 bg-slate-900 border border-slate-800 rounded-xl">
            <button
              type="button"
              onClick={() => setAnswerMode('text')}
              className={`flex-1 py-2 text-xs font-bold rounded-lg flex items-center justify-center gap-2 transition-all ${
                answerMode === 'text'
                  ? 'bg-brand-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <FileText className="w-4 h-4" />
              <span>Text Mode</span>
            </button>
            <button
              type="button"
              onClick={() => setAnswerMode('voice')}
              className={`flex-1 py-2 text-xs font-bold rounded-lg flex items-center justify-center gap-2 transition-all ${
                answerMode === 'voice'
                  ? 'bg-brand-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Mic className="w-4 h-4" />
              <span>Voice Mode (Microphone)</span>
            </button>
          </div>

          {/* Voice Input Section */}
          {answerMode === 'voice' && (
            <AudioRecorder
              onTranscriptionComplete={handleVoiceTranscription}
              isTranscribing={isTranscribing}
              setIsTranscribing={setIsTranscribing}
            />
          )}

          {/* Text Input / Transcript Editor Card */}
          <Card className="p-6 bg-slate-900/90 border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
                Your Answer {answerMode === 'voice' && '(Transcribed Speech)'}
              </label>
              <span className="text-[11px] text-slate-400 font-mono">
                {answerText.trim() ? `${answerText.trim().split(/\s+/).length} words` : '0 words'}
              </span>
            </div>

            <textarea
              rows={8}
              value={answerText}
              onChange={(e) => setAnswerText(e.target.value)}
              disabled={isSubmitting}
              className="w-full bg-slate-950 text-slate-100 text-sm rounded-xl border border-slate-800 p-4 focus:outline-none focus:ring-2 focus:ring-brand-500 leading-relaxed disabled:opacity-50"
              placeholder={
                answerMode === 'voice'
                  ? 'Record your voice using the microphone tool above, or type directly here...'
                  : 'Structure your answer thoroughly. For technical questions, mention architecture, trade-offs, and metrics. For behavioral, use the STAR framework.'
              }
            />

            {/* Action Buttons */}
            <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={handleSkipQuestion}
                disabled={isSubmitting}
                leftIcon={<FastForward className="w-4 h-4 text-slate-400" />}
              >
                Skip Question
              </Button>

              <Button
                type="button"
                variant="primary"
                size="md"
                onClick={handleSubmitAnswer}
                isLoading={isSubmitting}
                disabled={!answerText.trim()}
                rightIcon={<Send className="w-4 h-4" />}
                className="px-6"
              >
                Submit Answer
              </Button>
            </div>
          </Card>

          {/* Speech Feedback Preview for previous question */}
          {lastAnswerResponse && (
            <SpeechFeedback lastAnswer={lastAnswerResponse} />
          )}
        </div>
      </div>
    </div>
  );
};
