import React, { useState, useEffect } from 'react';
import {
  UploadCloud,
  FileText,
  CheckCircle2,
  AlertCircle,
  Briefcase,
  GraduationCap,
  Award,
  Layers,
  Sparkles,
  Phone,
  Mail,
  User,
  Plus
} from 'lucide-react';
import { Button } from '../components/common/Button';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { resumesApi } from '../api/resumes';
import type { ResumeData, ResumeListItem } from '../types';
import { useToast } from '../context/ToastContext';
import { Skeleton } from '../components/common/FeedbackStates';

export const ResumePage: React.FC = () => {
  const { addToast } = useToast();
  const fileInputRef = React.useRef<HTMLInputElement>(null);
  const [resumes, setResumes] = useState<ResumeListItem[]>([]);
  const [selectedResume, setSelectedResume] = useState<ResumeData | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isDragging, setIsDragging] = useState(false);

  useEffect(() => {
    fetchResumes();
  }, []);

  const fetchResumes = async () => {
    try {
      const list = await resumesApi.getResumes();
      setResumes(list);
      if (list.length > 0) {
        const detail = await resumesApi.getResumeById(list[0].id);
        setSelectedResume(detail);
      }
    } catch (err) {
      console.error('Failed to load resumes', err);
    } finally {
      setIsLoading(false);
    }
  };

  const processFile = async (file: File | undefined | null) => {
    if (!file) {
      addToast('Please select a resume first.', 'error');
      return;
    }

    // Validate file extension
    const nameLower = file.name.toLowerCase();
    const isPdf = nameLower.endsWith('.pdf');
    const isDocx = nameLower.endsWith('.docx');
    if (!isPdf && !isDocx) {
      addToast('Only PDF and DOCX files are supported.', 'error');
      return;
    }

    // Check size limit (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      addToast('Resume size must be less than 10 MB.', 'error');
      return;
    }

    setIsUploading(true);
    try {
      const uploaded = await resumesApi.uploadResume(file);
      addToast(`Resume "${file.name}" uploaded and parsed successfully!`, 'success');
      setSelectedResume(uploaded);
      await fetchResumes();
    } catch (err: any) {
      console.error('Resume upload error:', err);
      let errorMsg = 'Resume upload failed. Please try again.';
      if (err.response?.status === 413) {
        errorMsg = 'Resume size must be less than 10 MB.';
      } else if (err.response?.status === 400) {
        errorMsg = err.response?.data?.detail || 'Only PDF and DOCX files are supported.';
      } else if (err.response?.status === 422) {
        errorMsg = err.response?.data?.detail || 'Resume uploaded, but text extraction failed.';
      } else if (err.response?.status === 401) {
        errorMsg = 'Authentication session expired. Please sign in again.';
      } else if (err.response?.data?.detail) {
        errorMsg = typeof err.response.data.detail === 'string'
          ? err.response.data.detail
          : 'Failed to process resume.';
      }
      addToast(errorMsg, 'error');
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    processFile(file);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!isUploading) setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (isUploading) return;
    const file = e.dataTransfer.files?.[0];
    processFile(file);
  };

  const selectResume = async (id: string) => {
    try {
      const detail = await resumesApi.getResumeById(id);
      setSelectedResume(detail);
    } catch (err) {
      addToast('Could not load resume details.', 'error');
    }
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Resume Management & Parsing
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Upload your resume (PDF or DOCX). TalentIQ extracts entities, skills, and semantic vectors.
          </p>
        </div>

        {/* Hidden File Input */}
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          onChange={handleFileUpload}
          disabled={isUploading}
          className="hidden"
        />

        {/* Upload Trigger Button */}
        <Button
          type="button"
          isLoading={isUploading}
          disabled={isUploading}
          variant="primary"
          leftIcon={<UploadCloud className="w-4 h-4" />}
          onClick={() => fileInputRef.current?.click()}
        >
          {isUploading ? 'Parsing Resume...' : 'Upload New Resume'}
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: List of Uploaded Resumes */}
        <div className="space-y-4">
          <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
            <FileText className="w-4 h-4 text-brand-400" />
            <span>Uploaded Resumes ({resumes.length})</span>
          </h3>

          {isLoading ? (
            <div className="space-y-3">
              <Skeleton className="h-20 rounded-xl" />
              <Skeleton className="h-20 rounded-xl" />
            </div>
          ) : resumes.length > 0 ? (
            <div className="space-y-2.5">
              {resumes.map((r) => {
                const isSelected = selectedResume?.id === r.id;
                return (
                  <div
                    key={r.id}
                    onClick={() => selectResume(r.id)}
                    className={`p-4 rounded-xl border cursor-pointer transition-all duration-200 ${
                      isSelected
                        ? 'bg-brand-600/15 border-brand-500/50 shadow-md'
                        : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-xs font-bold text-white truncate max-w-[180px]">
                        {r.filename}
                      </span>
                      <Badge variant="brand" size="sm">{r.skills_count} Skills</Badge>
                    </div>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {r.top_skills.slice(0, 3).map((s, i) => (
                        <span key={i} className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="p-8 rounded-2xl border border-dashed border-slate-800 text-center space-y-3">
              <FileText className="w-8 h-8 text-slate-500 mx-auto" />
              <p className="text-xs text-slate-400">No resumes uploaded yet.</p>
            </div>
          )}

          {/* Quick upload drop box */}
          <div
            onClick={() => !isUploading && fileInputRef.current?.click()}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`p-6 rounded-2xl border-2 border-dashed transition-all cursor-pointer text-center space-y-3 select-none ${
              isDragging
                ? 'border-brand-400 bg-brand-500/10 scale-[1.01]'
                : isUploading
                ? 'opacity-60 cursor-not-allowed border-slate-800 bg-slate-900/20'
                : 'border-slate-800 hover:border-brand-500/50 bg-slate-900/30'
            }`}
          >
            <UploadCloud className={`w-8 h-8 mx-auto ${isDragging ? 'text-brand-300 animate-bounce' : 'text-brand-400'}`} />
            <h4 className="text-xs font-bold text-white">
              {isUploading ? 'Uploading & parsing...' : isDragging ? 'Drop your resume file here' : 'Drag & drop your resume'}
            </h4>
            <p className="text-[11px] text-slate-400">PDF or DOCX up to 10MB</p>
          </div>
        </div>

        {/* Right Column: Detailed Parsed Resume Entities */}
        <div className="lg:col-span-2 space-y-6">
          {selectedResume ? (
            <div className="space-y-6">
              {/* Candidate Info Header Card */}
              <Card className="p-6 bg-slate-900/90 border-slate-800">
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
                  <div>
                    <h2 className="text-xl font-bold text-white">
                      {selectedResume.parsed_data.name || 'Candidate Profile'}
                    </h2>
                    <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400 mt-1">
                      {selectedResume.parsed_data.email && (
                        <span className="flex items-center gap-1.5">
                          <Mail className="w-3.5 h-3.5 text-brand-400" />
                          {selectedResume.parsed_data.email}
                        </span>
                      )}
                      {selectedResume.parsed_data.phone && (
                        <span className="flex items-center gap-1.5">
                          <Phone className="w-3.5 h-3.5 text-emerald-400" />
                          {selectedResume.parsed_data.phone}
                        </span>
                      )}
                    </div>
                  </div>
                  <Badge variant="emerald" size="md">Parsed with AI</Badge>
                </div>

                {selectedResume.parsed_data.summary && (
                  <p className="text-xs text-slate-300 leading-relaxed mt-4 italic">
                    "{selectedResume.parsed_data.summary}"
                  </p>
                )}
              </Card>

              {/* Extracted Skills */}
              <Card className="p-6 bg-slate-900/90 border-slate-800 space-y-3">
                <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-brand-400" />
                  <span>Identified Skills ({selectedResume.skills.length})</span>
                </h3>
                <div className="flex flex-wrap gap-2 pt-1">
                  {selectedResume.skills.map((skill, i) => (
                    <Badge key={i} variant="brand" size="md">{skill}</Badge>
                  ))}
                </div>
              </Card>

              {/* Experience Timeline */}
              {selectedResume.parsed_data.experience && selectedResume.parsed_data.experience.length > 0 && (
                <Card className="p-6 bg-slate-900/90 border-slate-800 space-y-4">
                  <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                    <Briefcase className="w-4 h-4 text-indigo-400" />
                    <span>Work Experience</span>
                  </h3>
                  <div className="space-y-4">
                    {selectedResume.parsed_data.experience.map((exp, i) => (
                      <div key={i} className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-2">
                        <div className="flex items-start justify-between">
                          <div>
                            <h4 className="text-sm font-bold text-white">{exp.role}</h4>
                            <p className="text-xs font-medium text-brand-300">{exp.company}</p>
                          </div>
                          <span className="text-[11px] text-slate-400">{exp.duration}</span>
                        </div>
                        {exp.highlights && exp.highlights.length > 0 && (
                          <ul className="list-disc list-inside space-y-1 text-xs text-slate-300 pt-1">
                            {exp.highlights.map((hl, j) => (
                              <li key={j} className="leading-relaxed">{hl}</li>
                            ))}
                          </ul>
                        )}
                      </div>
                    ))}
                  </div>
                </Card>
              )}

              {/* Projects */}
              {selectedResume.parsed_data.projects && selectedResume.parsed_data.projects.length > 0 && (
                <Card className="p-6 bg-slate-900/90 border-slate-800 space-y-4">
                  <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                    <Layers className="w-4 h-4 text-cyan-400" />
                    <span>Notable Projects</span>
                  </h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {selectedResume.parsed_data.projects.map((proj, i) => (
                      <div key={i} className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-2">
                        <h4 className="text-xs font-bold text-white">{proj.name}</h4>
                        <p className="text-xs text-slate-400 leading-relaxed">{proj.description}</p>
                        <div className="flex flex-wrap gap-1 pt-1">
                          {proj.tech?.map((t, k) => (
                            <span key={k} className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                              {t}
                            </span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>
              )}

              {/* Education & Certifications */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                {selectedResume.parsed_data.education && (
                  <Card className="p-5 bg-slate-900/90 border-slate-800 space-y-3">
                    <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                      <GraduationCap className="w-4 h-4 text-emerald-400" />
                      <span>Education</span>
                    </h3>
                    {selectedResume.parsed_data.education.map((edu, i) => (
                      <div key={i} className="text-xs space-y-0.5">
                        <p className="font-bold text-white">{edu.degree}</p>
                        <p className="text-slate-400">{edu.institution} ({edu.year})</p>
                      </div>
                    ))}
                  </Card>
                )}

                {selectedResume.parsed_data.certifications && (
                  <Card className="p-5 bg-slate-900/90 border-slate-800 space-y-3">
                    <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                      <Award className="w-4 h-4 text-amber-400" />
                      <span>Certifications</span>
                    </h3>
                    <ul className="space-y-1 text-xs text-slate-300">
                      {selectedResume.parsed_data.certifications.map((c, i) => (
                        <li key={i} className="flex items-center gap-2">
                          <CheckCircle2 className="w-3.5 h-3.5 text-amber-400" />
                          <span>{c}</span>
                        </li>
                      ))}
                    </ul>
                  </Card>
                )}
              </div>
            </div>
          ) : (
            <Card className="p-12 text-center text-slate-400 bg-slate-900/40 border-dashed border-slate-800 space-y-3">
              <FileText className="w-12 h-12 text-slate-600 mx-auto" />
              <h3 className="text-base font-bold text-white">No Resume Selected</h3>
              <p className="text-xs max-w-sm mx-auto">
                Upload your resume above to view extracted structured entities, skills, and projects.
              </p>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};
