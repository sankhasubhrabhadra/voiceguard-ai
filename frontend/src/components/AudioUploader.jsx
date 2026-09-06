import React, { useRef, useState } from "react";
import { Upload, Music, X, Play, Pause, AlertCircle, Sparkles } from "lucide-react";

export default function AudioUploader({
  selectedFile,
  selectedSample,
  onFileSelect,
  onClearAudio,
  onAnalyze,
  isLoading,
  audioUrl
}) {
  const [isDragging, setIsDragging] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [customTranscript, setCustomTranscript] = useState("");
  const [showTranscriptInput, setShowTranscriptInput] = useState(false);
  const fileInputRef = useRef(null);
  const audioRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      if (file.type.startsWith("audio/") || file.name.match(/\.(wav|mp3|m4a|ogg|flac|webm)$/i)) {
        onFileSelect(file);
      }
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      onFileSelect(e.target.files[0]);
    }
  };

  const togglePlayback = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play();
      setIsPlaying(true);
    }
  };

  const handleAudioEnded = () => {
    setIsPlaying(false);
  };

  const activeAudioName = selectedFile ? selectedFile.name : selectedSample ? selectedSample.title : null;

  return (
    <div className="bg-white rounded-lg p-6 shadow-card border border-[#E5E7EB]/60">
      <div className="mb-4">
        <h2 className="text-sm font-semibold text-[#111111] uppercase tracking-wider">
          1. Upload Call Audio
        </h2>
        <p className="text-xs text-[#6B7280] mt-0.5">
          Select or drop call recording (WAV, MP3, M4A, OGG) for voice clone & scam detection
        </p>
      </div>

      {!activeAudioName ? (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragging
              ? "border-[#4338CA] bg-[#EEF2FF]/40"
              : "border-[#E5E7EB] hover:border-[#D1D5DB] bg-[#FAFAFA]"
          }`}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept="audio/*,.wav,.mp3,.m4a,.ogg,.flac,.webm"
            className="hidden"
          />
          <div className="flex flex-col items-center justify-center space-y-3">
            <div className="w-12 h-12 rounded-lg bg-white border border-[#E5E7EB] flex items-center justify-center text-[#4338CA] shadow-sm">
              <Upload className="w-5 h-5 stroke-[1.75]" />
            </div>
            <div>
              <p className="text-xs font-semibold text-[#111111]">
                Click to upload or drag & drop call recording
              </p>
              <p className="text-[11px] text-[#6B7280] mt-0.5">
                WAV, MP3, M4A or OGG (max 25MB)
              </p>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-[#FAFAFA] rounded-lg p-4 border border-[#E5E7EB]">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3 overflow-hidden">
              <button
                type="button"
                onClick={togglePlayback}
                disabled={!audioUrl}
                className="w-10 h-10 rounded-lg bg-[#4338CA] text-white flex items-center justify-center hover:bg-[#3730A3] transition-colors flex-shrink-0 disabled:opacity-50"
              >
                {isPlaying ? (
                  <Pause className="w-4 h-4 fill-white" />
                ) : (
                  <Play className="w-4 h-4 fill-white ml-0.5" />
                )}
              </button>
              <div className="truncate">
                <p className="text-xs font-semibold text-[#111111] truncate">
                  {activeAudioName}
                </p>
                <p className="text-[11px] text-[#6B7280]">
                  {selectedFile
                    ? `${(selectedFile.size / (1024 * 1024)).toFixed(2)} MB • Ready for forensic analysis`
                    : "Preset Sample Loaded"}
                </p>
              </div>
            </div>

            <button
              type="button"
              onClick={() => {
                if (audioRef.current) audioRef.current.pause();
                setIsPlaying(false);
                onClearAudio();
              }}
              className="text-[#9CA3AF] hover:text-[#111111] p-1.5 rounded-lg hover:bg-white transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {audioUrl && (
            <audio
              ref={audioRef}
              src={audioUrl}
              onEnded={handleAudioEnded}
              className="hidden"
            />
          )}
        </div>
      )}

      {/* Transcript override / customization option */}
      <div className="mt-4 pt-4 border-t border-[#F3F4F6]">
        <div className="flex items-center justify-between">
          <button
            type="button"
            onClick={() => setShowTranscriptInput(!showTranscriptInput)}
            className="text-[11px] font-semibold text-[#4338CA] hover:underline flex items-center space-x-1"
          >
            <span>{showTranscriptInput ? "− Hide transcript text override" : "+ Custom transcript / test phrases"}</span>
          </button>
          {customTranscript && (
            <span className="text-[10px] text-[#0D9488] font-semibold bg-[#F0FDFA] px-2 py-0.5 rounded">
              Custom text active
            </span>
          )}
        </div>

        {showTranscriptInput && (
          <div className="mt-2.5">
            <textarea
              rows={3}
              value={customTranscript}
              onChange={(e) => setCustomTranscript(e.target.value)}
              placeholder="Enter or paste speech text to test specific scam keywords (e.g. 'You are under digital arrest by Delhi Police...')"
              className="w-full text-xs text-[#111111] bg-[#FAFAFA] border border-[#E5E7EB] rounded-lg p-2.5 focus:outline-none focus:border-[#4338CA] placeholder-[#9CA3AF]"
            />
          </div>
        )}
      </div>

      {/* Analyze button */}
      <div className="mt-4">
        <button
          type="button"
          onClick={() => onAnalyze(customTranscript)}
          disabled={!activeAudioName || isLoading}
          className="w-full bg-[#4338CA] hover:bg-[#3730A3] disabled:bg-[#E5E7EB] disabled:text-[#9CA3AF] text-white text-xs font-semibold py-3 px-4 rounded-lg transition-colors flex items-center justify-center space-x-2 shadow-sm"
        >
          {isLoading ? (
            <>
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              <span>Analyzing Audio Forensics & Scam Patterns...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4 stroke-[1.75]" />
              <span>Run VoiceGuard Analysis</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
