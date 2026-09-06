import React, { useState, useEffect } from "react";
import Header from "./components/Header";
import AudioUploader from "./components/AudioUploader";
import SampleAudioSelector from "./components/SampleAudioSelector";
import RiskGauge from "./components/RiskGauge";
import SpectrogramViewer from "./components/SpectrogramViewer";
import TranscriptViewer from "./components/TranscriptViewer";
import ExplanationSection from "./components/ExplanationSection";
import ReportModal from "./components/ReportModal";
import ReportedCallsList from "./components/ReportedCallsList";
import { fetchSamples, getSampleAudioUrl, analyzeAudio, fetchReports } from "./services/api";

export default function App() {
  const [samples, setSamples] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedSample, setSelectedSample] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState(null);

  const [isReportModalOpen, setIsReportModalOpen] = useState(false);
  const [isReportListOpen, setIsReportListOpen] = useState(false);
  const [reportCount, setReportCount] = useState(0);

  // Load sample presets and report count on start
  useEffect(() => {
    loadSamples();
    loadReportCount();
  }, []);

  const loadSamples = async () => {
    try {
      const data = await fetchSamples();
      setSamples(data || []);
      // Pre-select first sample as default convenience
      if (data && data.length > 0) {
        handleSelectSample(data[0]);
      }
    } catch (err) {
      console.error("Failed to load samples:", err);
    }
  };

  const loadReportCount = async () => {
    try {
      const data = await fetchReports();
      setReportCount(data?.length || 0);
    } catch (err) {
      console.error(err);
    }
  };

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setSelectedSample(null);
    setError(null);
    const localUrl = URL.createObjectURL(file);
    setAudioUrl(localUrl);
  };

  const handleSelectSample = (sample) => {
    setSelectedSample(sample);
    setSelectedFile(null);
    setError(null);
    const url = getSampleAudioUrl(sample.filename);
    setAudioUrl(url);
  };

  const handleClearAudio = () => {
    setSelectedFile(null);
    setSelectedSample(null);
    setAudioUrl(null);
    setAnalysisResult(null);
    setError(null);
  };

  const handleAnalyze = async (customTranscript = "") => {
    if (!selectedFile && !selectedSample) return;

    setIsLoading(true);
    setError(null);

    try {
      const res = await analyzeAudio({
        file: selectedFile,
        sampleFilename: selectedSample ? selectedSample.filename : null,
        transcriptOverride: customTranscript
      });
      setAnalysisResult(res);
      loadReportCount();
    } catch (err) {
      setError(err.message || "An error occurred during audio forensics.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#FAFAFA] text-[#111111] flex flex-col antialiased">
      <Header
        onOpenReports={() => setIsReportListOpen(true)}
        reportCount={reportCount}
      />

      <main className="flex-1 max-w-5xl w-full mx-auto px-4 py-8 space-y-8">
        {/* Intro banner */}
        <div className="space-y-1">
          <h2 className="text-xl font-semibold text-[#111111] tracking-tight">
            AI Voice Clone & Scam-Call Threat Analysis
          </h2>
          <p className="text-xs text-[#6B7280]">
            Dual-vector detection engine analyzing physical acoustic vocal tract anomalies and conversational scam-script patterns.
          </p>
        </div>

        {/* Input section: 2 columns */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-6">
            <AudioUploader
              selectedFile={selectedFile}
              selectedSample={selectedSample}
              onFileSelect={handleFileSelect}
              onClearAudio={handleClearAudio}
              onAnalyze={handleAnalyze}
              isLoading={isLoading}
              audioUrl={audioUrl}
            />
          </div>

          <div className="lg:col-span-6">
            <SampleAudioSelector
              samples={samples}
              selectedSample={selectedSample}
              onSelectSample={handleSelectSample}
              isLoading={isLoading}
            />
          </div>
        </div>

        {/* Error Notification */}
        {error && (
          <div className="p-4 bg-[#FEF2F2] border border-[#FEE2E2] rounded-lg text-xs text-[#DC2626] font-semibold">
            {error}
          </div>
        )}

        {/* Analysis Results Panel */}
        {analysisResult && (
          <div className="space-y-6 pt-2">
            {/* 1. Primary Risk Verdict */}
            <RiskGauge
              fusion={analysisResult.fusion}
              voiceAnalysis={analysisResult.voice_analysis}
              transcriptAnalysis={analysisResult.transcript_analysis}
              filename={analysisResult.filename}
              onOpenReportModal={() => setIsReportModalOpen(true)}
            />

            {/* 2. Waveform & Spectrogram */}
            <SpectrogramViewer
              spectrogramData={analysisResult.voice_analysis?.spectrogram_data}
              anomalousRegions={analysisResult.voice_analysis?.anomalous_regions}
              duration={analysisResult.duration}
            />

            {/* 3. Whisper STT & Scam Matching */}
            <TranscriptViewer
              transcriptAnalysis={analysisResult.transcript_analysis}
            />

            {/* 4. Explainability & Acoustic Contributions */}
            <ExplanationSection
              voiceAnalysis={analysisResult.voice_analysis}
              fusion={analysisResult.fusion}
            />
          </div>
        )}
      </main>

      {/* Modals */}
      <ReportModal
        isOpen={isReportModalOpen}
        onClose={() => setIsReportModalOpen(false)}
        analysisData={analysisResult}
        onReportSuccess={() => {
          loadReportCount();
        }}
      />

      <ReportedCallsList
        isOpen={isReportListOpen}
        onClose={() => setIsReportListOpen(false)}
      />

      <footer className="border-t border-[#E5E7EB]/60 py-6 text-center text-[11px] text-[#9CA3AF]">
        VoiceGuard AI • Real-Time Voice Clone Forensics & Scam Call Prevention Platform
      </footer>
    </div>
  );
}
