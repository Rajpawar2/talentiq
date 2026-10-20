import React from 'react';

interface ScoreRingProps {
  score: number;
  size?: number;
  strokeWidth?: number;
  label?: string;
  subLabel?: string;
}

export const ScoreRing: React.FC<ScoreRingProps> = ({
  score,
  size = 120,
  strokeWidth = 10,
  label,
  subLabel,
}) => {
  const normalizedScore = Math.min(Math.max(score, 0), 100);
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (normalizedScore / 100) * circumference;

  const getColor = (s: number) => {
    if (s >= 80) return '#10b981'; // Emerald
    if (s >= 65) return '#6366f1'; // Brand Indigo
    if (s >= 50) return '#f59e0b'; // Amber
    return '#f43f5e';             // Rose
  };

  const ringColor = getColor(normalizedScore);

  return (
    <div className="flex flex-col items-center justify-center text-center">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="transform -rotate-90">
          {/* Background circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="#1e293b"
            strokeWidth={strokeWidth}
            fill="transparent"
          />
          {/* Foreground progress circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={ringColor}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-extrabold text-white tracking-tight">
            {Math.round(score)}
          </span>
          <span className="text-[10px] uppercase font-bold text-slate-400 -mt-0.5">
            /100
          </span>
        </div>
      </div>
      {label && <p className="text-sm font-semibold text-slate-200 mt-2">{label}</p>}
      {subLabel && <p className="text-xs text-slate-400 mt-0.5">{subLabel}</p>}
    </div>
  );
};
