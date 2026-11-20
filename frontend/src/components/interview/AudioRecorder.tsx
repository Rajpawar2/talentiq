import React, { useState, useRef, useEffect } from 'react';
import { Mic, Square, Loader2, AlertCircle, Volume2, RotateCcw } from 'lucide-react';
import { Button } from '../common/Button';
import { interviewsApi } from '../../api/interviews';
import { useToast } from '../../context/ToastContext';

interface AudioRecorderProps {
  onTranscriptionComplete: (transcript: string, durationSeconds: number) => void;
  isTranscribing: boolean;
  setIsTranscribing: (v: boolean) => void;
}

export const AudioRecorder: React.FC<AudioRecorderProps> = ({
  onTranscriptionComplete,
  isTranscribing,
  setIsTranscribing,
}) => {
  const { addToast } = useToast();
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [permissionError, setPermissionError] = useState<string | null>(null);
  const [liveTranscript, setLiveTranscript] = useState<string>('');

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerIntervalRef = useRef<any>(null);
  const recordingTimeRef = useRef<number>(0);
  const speechRecognitionRef = useRef<any>(null);
  const accumulatedSpeechRef = useRef<string>('');

  useEffect(() => {
    return () => {
      if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
        mediaRecorderRef.current.stop();
      }
      if (speechRecognitionRef.current) {
        try {
          speechRecognitionRef.current.stop();
        } catch {
          // ignore
        }
      }
    };
  }, []);

  const formatTime = (secs: number) => {
    const mins = Math.floor(secs / 60);
    const remaining = secs % 60;
    return `${mins.toString().padStart(2, '0')}:${remaining.toString().padStart(2, '0')}`;
  };

  const getSupportedMimeType = (): string => {
    const types = [
      'audio/webm;codecs=opus',
      'audio/webm',
      'audio/mp4',
      'audio/ogg;codecs=opus',
      'audio/wav',
    ];
    for (const t of types) {
      if (typeof MediaRecorder !== 'undefined' && MediaRecorder.isTypeSupported && MediaRecorder.isTypeSupported(t)) {
        return t;
      }
    }
    return '';
  };

  const startRecording = async () => {
    setPermissionError(null);
    audioChunksRef.current = [];
    accumulatedSpeechRef.current = '';
    setLiveTranscript('');
    recordingTimeRef.current = 0;
    setRecordingTime(0);

    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Your browser does not support audio recording. Please use Text Mode.');
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mimeType = getSupportedMimeType();
      const options = mimeType ? { mimeType } : undefined;
      const mediaRecorder = options ? new MediaRecorder(stream, options) : new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const finalDuration = Math.max(recordingTimeRef.current, 1);
        const effectiveMime = mimeType || 'audio/webm';
        const audioBlob = new Blob(audioChunksRef.current, { type: effectiveMime });

        // Release microphone tracks
        stream.getTracks().forEach((track) => track.stop());

        // Process audio upload & transcription
        await processAudioUpload(audioBlob, finalDuration, accumulatedSpeechRef.current.trim());
      };

      // Start Web Speech API for real-time live recognition if available in browser
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        try {
          const recognition = new SpeechRecognition();
          recognition.continuous = true;
          recognition.interimResults = true;
          recognition.lang = 'en-US';

          recognition.onresult = (event: any) => {
            let currentText = '';
            for (let i = 0; i < event.results.length; i++) {
              currentText += event.results[i][0].transcript + ' ';
            }
            accumulatedSpeechRef.current = currentText;
            setLiveTranscript(currentText.trim());
          };

          recognition.onerror = () => {
            // Non-fatal: audio blob upload will still happen
          };

          recognition.start();
          speechRecognitionRef.current = recognition;
        } catch (e) {
          console.warn('SpeechRecognition initialization error:', e);
        }
      }

      mediaRecorder.start(250); // Slice in 250ms chunks
      setIsRecording(true);

      timerIntervalRef.current = setInterval(() => {
        recordingTimeRef.current += 1;
        setRecordingTime(recordingTimeRef.current);
      }, 1000);
    } catch (err: any) {
      const msg = err.name === 'NotAllowedError'
        ? 'Microphone permission denied. Please allow microphone access in your browser or use Text Mode.'
        : err.message || 'Could not access microphone.';
      setPermissionError(msg);
      addToast(msg, 'warning');
    }
  };

  const stopRecording = () => {
    if (timerIntervalRef.current) {
      clearInterval(timerIntervalRef.current);
    }

    if (speechRecognitionRef.current) {
      try {
        speechRecognitionRef.current.stop();
      } catch {
        // ignore
      }
    }

    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const processAudioUpload = async (blob: Blob, duration: number, recognizedLiveText: string) => {
    setIsTranscribing(true);

    try {
      if (blob.size < 100 && !recognizedLiveText) {
        addToast('No audio content recorded. Please speak into your microphone or use Text Mode.', 'warning');
        return;
      }

      let finalTranscript = recognizedLiveText;

      // Upload to backend transcription service
      try {
        const res = await interviewsApi.transcribeAudio(blob, duration);
        if (res.transcript && res.transcript.trim()) {
          finalTranscript = res.transcript.trim();
        }
      } catch (uploadErr) {
        console.warn('Backend transcription API unavailable, using client-side recognition:', uploadErr);
      }

      if (finalTranscript && finalTranscript.trim()) {
        addToast('Voice transcribed successfully!', 'success');
        onTranscriptionComplete(finalTranscript.trim(), duration);
      } else {
        addToast('No speech was detected. Please verify your microphone or enter your response in Text Mode.', 'warning');
      }
    } finally {
      setIsTranscribing(false);
    }
  };

  return (
    <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Volume2 className="w-4 h-4 text-brand-400" />
          <h4 className="text-sm font-bold text-white">Voice Input Mode</h4>
        </div>

        {isRecording && (
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-rose-500/20 border border-rose-500/40 text-rose-300 text-xs font-mono font-bold animate-pulse">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-ping" />
            <span>REC {formatTime(recordingTime)}</span>
          </div>
        )}
      </div>

      {permissionError && (
        <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-200 text-xs flex items-start gap-2">
          <AlertCircle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
          <span>{permissionError}</span>
        </div>
      )}

      {/* Recording Visualizer Bars */}
      {isRecording && (
        <div className="space-y-3">
          <div className="flex items-center justify-center gap-1.5 h-12 bg-slate-950/80 rounded-xl px-4 border border-slate-800">
            {[12, 24, 38, 16, 42, 28, 14, 34, 46, 20, 36, 18, 30].map((height, i) => (
              <span
                key={i}
                className="w-1.5 bg-gradient-to-t from-brand-600 to-brand-400 rounded-full animate-wave"
                style={{
                  height: `${height}px`,
                  animationDelay: `${(i * 0.1)}s`,
                }}
              />
            ))}
          </div>

          {liveTranscript && (
            <div className="p-3 rounded-xl bg-slate-950/90 border border-brand-500/20 text-xs text-slate-300 max-h-24 overflow-y-auto">
              <span className="text-[10px] uppercase font-bold text-brand-400 block mb-1">Live Speech Recognition:</span>
              <span>{liveTranscript}</span>
            </div>
          )}
        </div>
      )}

      {/* Control Buttons */}
      <div className="flex items-center gap-3">
        {!isRecording ? (
          <Button
            type="button"
            onClick={startRecording}
            disabled={isTranscribing}
            variant="primary"
            leftIcon={<Mic className="w-4 h-4" />}
            className="w-full bg-emerald-600 hover:bg-emerald-500 border-emerald-400/30"
          >
            Start Voice Recording
          </Button>
        ) : (
          <Button
            type="button"
            onClick={stopRecording}
            variant="danger"
            leftIcon={<Square className="w-4 h-4 fill-current" />}
            className="w-full"
          >
            Stop & Submit Answer
          </Button>
        )}
      </div>

      {isTranscribing && (
        <div className="flex items-center justify-center gap-2 text-xs font-semibold text-brand-300 py-1">
          <Loader2 className="w-4 h-4 animate-spin" />
          <span>Transcribing voice recording...</span>
        </div>
      )}
    </div>
  );
};
