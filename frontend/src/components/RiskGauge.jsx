import React from "react";
import { AlertTriangle, CheckCircle2, AlertOctagon, Flag, ShieldCheck, Activity, BrainCircuit, MessageSquare, Info } from "lucide-react";

export default function RiskGauge({ fusion, voiceAnalysis, transcriptAnalysis, filename, onOpenReportModal }) {
  if (!fusion) return null;

  const {
    overall_risk_score,
    risk_level,
    plain_language_explanation,
    voice_risk_score,
    script_risk_score,
    social_engineering_score = 0,
    acoustic_anomaly_score = 0,
    key_verdicts = [],
    risk_reasons = [],
    suggested_action,
    is_simulation_detected = false
  } = fusion;

  const anomalyCount = voiceAnalysis?.anomalous_regions?.length || 0;
  const isVoiceCloned = voiceAnalysis?.is_cloned || voice_risk_score >= 50.0;
  const isScriptScam = script_risk_score >= 50.0;

  let riskColor = "#0D9488"; // Low (Teal)
  let riskBg = "#F0FDFA";
  let riskBorder = "#CCFBF1";
  let RiskIcon = CheckCircle2;

  if (risk_level === "High" || overall_risk_score >= 70.0) {
    riskColor = "#DC2626"; // High (Red)
    riskBg = "#FEF2F2";
    riskBorder = "#FEE2E2";
    RiskIcon = AlertOctagon;
  } else if (risk_level === "Medium" || overall_risk_score >= 35.0) {
    riskColor = "#D97706"; // Medium (Amber)
    riskBg = "#FFFBEB";
    riskBorder = "#FEF3C7";
    RiskIcon = AlertTriangle;
  }

  // Calculate SVG stroke offset for circular meter (circumference = 2 * pi * 44 ~= 276.46)
  const radius = 44;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (overall_risk_score / 100) * circumference;

  return (
    <div className="bg-white rounded-lg p-6 shadow-card border border-[#E5E7EB]/60 space-y-6">
      {/* Header Bar */}
      <div className="flex items-center justify-between pb-4 border-b border-[#F3F4F6]">
        <div>
          <span className="text-xs font-semibold text-[#6B7280] uppercase tracking-wider">
            Comprehensive Forensic Verdict
          </span>
          <h3 className="text-sm font-semibold text-[#111111] mt-0.5">
            {filename || "Call Recording"}
          </h3>
        </div>

        <button
          onClick={onOpenReportModal}
          className="flex items-center space-x-1.5 text-xs font-semibold text-[#DC2626] bg-[#FEF2F2] hover:bg-[#FEE2E2] px-3 py-1.5 rounded-lg border border-[#FEE2E2] transition-colors"
        >
          <Flag className="w-3.5 h-3.5 stroke-[2]" />
          <span>Report Call</span>
        </button>
      </div>

      {/* Simulation / Educational Notice Banner */}
      {is_simulation_detected && (
        <div className="p-3 bg-[#EEF2FF] border border-[#C7D2FE] rounded-lg text-xs flex items-start space-x-2 text-[#3730A3]">
          <Info className="w-4 h-4 flex-shrink-0 mt-0.5" />
          <div>
            <span className="font-bold block">Cybersecurity Training / Simulated Demonstration Detected</span>
            <span className="text-[11px] text-[#4338CA] mt-0.5 block">
              The conversation contains simulated fraud-call techniques alongside educational/training awareness framing.
            </span>
          </div>
        </div>
      )}

      {/* Overall Score & Core Meter */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-center">
        {/* Left: Overall Risk Dial */}
        <div className="md:col-span-4 flex flex-col items-center justify-center p-4 bg-[#FAFAFA] rounded-lg border border-[#E5E7EB]">
          <div className="relative w-32 h-32 flex items-center justify-center">
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
              <circle
                cx="50"
                cy="50"
                r={radius}
                className="stroke-[#E5E7EB]"
                strokeWidth="7"
                fill="transparent"
              />
              <circle
                cx="50"
                cy="50"
                r={radius}
                stroke={riskColor}
                strokeWidth="7"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                fill="transparent"
                className="transition-all duration-700 ease-out"
              />
            </svg>
            <div className="absolute flex flex-col items-center justify-center">
              <span className="text-3xl font-bold text-[#111111] tracking-tight">
                {Math.round(overall_risk_score)}%
              </span>
              <span className="text-[10px] font-semibold text-[#6B7280] uppercase">
                Overall Risk
              </span>
            </div>
          </div>

          <div
            className="mt-3 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider flex items-center space-x-1.5 border"
            style={{ backgroundColor: riskBg, color: riskColor, borderColor: riskBorder }}
          >
            <RiskIcon className="w-3.5 h-3.5 stroke-[2.5]" />
            <span>{risk_level} Risk Level</span>
          </div>
        </div>

        {/* Right: 4 Distinct Modality Score Cards */}
        <div className="md:col-span-8 grid grid-cols-1 sm:grid-cols-2 gap-3">
          {/* Card 1: Voice Authenticity */}
          <div className="bg-[#FAFAFA] p-3.5 rounded-lg border border-[#E5E7EB] flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-1.5">
                <BrainCircuit className="w-3.5 h-3.5 text-[#4338CA]" />
                <span className="text-[11px] font-semibold text-[#4B5563] uppercase tracking-wider">
                  Voice Authenticity
                </span>
              </div>
              <span
                className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                  isVoiceCloned
                    ? "bg-[#FEF2F2] text-[#DC2626] border-[#FEE2E2]"
                    : "bg-[#F0FDFA] text-[#0D9488] border-[#CCFBF1]"
                }`}
              >
                {isVoiceCloned ? "Synthetic Clone" : "Authentic Human"}
              </span>
            </div>

            <div className="my-2">
              <div className="flex items-baseline justify-between">
                <span className="text-xl font-bold text-[#111111]">{voice_risk_score.toFixed(1)}%</span>
                <span className="text-[10px] text-[#6B7280]">Clone Probability</span>
              </div>
              <div className="w-full bg-[#E5E7EB] h-1.5 rounded-full mt-1.5 overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${voice_risk_score}%`,
                    backgroundColor: voice_risk_score >= 60 ? "#DC2626" : voice_risk_score >= 40 ? "#D97706" : "#0D9488"
                  }}
                />
              </div>
            </div>
            <span className="text-[10px] text-[#6B7280]">
              Forensics: {voiceAnalysis?.vocoder_biomarkers?.length || 0} vocoder markers flagged
            </span>
          </div>

          {/* Card 2: Scam Script Intent */}
          <div className="bg-[#FAFAFA] p-3.5 rounded-lg border border-[#E5E7EB] flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-1.5">
                <MessageSquare className="w-3.5 h-3.5 text-[#4338CA]" />
                <span className="text-[11px] font-semibold text-[#4B5563] uppercase tracking-wider">
                  Scam Script Intent
                </span>
              </div>
              <span
                className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                  isScriptScam
                    ? "bg-[#FEF2F2] text-[#DC2626] border-[#FEE2E2]"
                    : "bg-[#F0FDFA] text-[#0D9488] border-[#CCFBF1]"
                }`}
              >
                {isScriptScam ? "Fraud Pattern Detected" : "Benign Script"}
              </span>
            </div>

            <div className="my-2">
              <div className="flex items-baseline justify-between">
                <span className="text-xl font-bold text-[#111111]">{script_risk_score.toFixed(1)}%</span>
                <span className="text-[10px] text-[#6B7280]">Pattern Similarity</span>
              </div>
              <div className="w-full bg-[#E5E7EB] h-1.5 rounded-full mt-1.5 overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${script_risk_score}%`,
                    backgroundColor: script_risk_score >= 60 ? "#DC2626" : script_risk_score >= 35 ? "#D97706" : "#0D9488"
                  }}
                />
              </div>
            </div>
            <span className="text-[10px] text-[#6B7280]">
              Matches: {transcriptAnalysis?.matches?.length || 0} scam vector patterns
            </span>
          </div>

          {/* Card 3: Social Engineering Analysis */}
          <div className="bg-[#FAFAFA] p-3.5 rounded-lg border border-[#E5E7EB] flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-[#4338CA]" />
                <span className="text-[11px] font-semibold text-[#4B5563] uppercase tracking-wider">
                  Social Engineering
                </span>
              </div>
              <span
                className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                  social_engineering_score >= 50
                    ? "bg-[#FEF2F2] text-[#DC2626] border-[#FEE2E2]"
                    : "bg-[#F0FDFA] text-[#0D9488] border-[#CCFBF1]"
                }`}
              >
                {social_engineering_score >= 50 ? "High Manipulation" : "Normal Interaction"}
              </span>
            </div>

            <div className="my-2">
              <div className="flex items-baseline justify-between">
                <span className="text-xl font-bold text-[#111111]">{social_engineering_score.toFixed(1)}%</span>
                <span className="text-[10px] text-[#6B7280]">Coercion Index</span>
              </div>
              <div className="w-full bg-[#E5E7EB] h-1.5 rounded-full mt-1.5 overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${social_engineering_score}%`,
                    backgroundColor: social_engineering_score >= 60 ? "#DC2626" : social_engineering_score >= 35 ? "#D97706" : "#0D9488"
                  }}
                />
              </div>
            </div>
            <span className="text-[10px] text-[#6B7280]">
              Vectors: {transcriptAnalysis?.social_engineering?.flagged_intents?.length || 0} behavioral triggers
            </span>
          </div>

          {/* Card 4: Acoustic Anomalies */}
          <div className="bg-[#FAFAFA] p-3.5 rounded-lg border border-[#E5E7EB] flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-1.5">
                <Activity className="w-3.5 h-3.5 text-[#4338CA]" />
                <span className="text-[11px] font-semibold text-[#4B5563] uppercase tracking-wider">
                  Acoustic Anomalies
                </span>
              </div>
              <span
                className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                  anomalyCount > 0
                    ? "bg-[#FEF2F2] text-[#DC2626] border-[#FEE2E2]"
                    : "bg-[#F0FDFA] text-[#0D9488] border-[#CCFBF1]"
                }`}
              >
                {anomalyCount > 0 ? `${anomalyCount} Zones Flagged` : "No Anomalies"}
              </span>
            </div>

            <div className="my-2">
              <div className="flex items-baseline justify-between">
                <span className="text-xl font-bold text-[#111111]">{anomalyCount}</span>
                <span className="text-[10px] text-[#6B7280]">Intervals ({acoustic_anomaly_score.toFixed(0)}% score)</span>
              </div>
              <div className="w-full bg-[#E5E7EB] h-1.5 rounded-full mt-1.5 overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${Math.min(100, acoustic_anomaly_score)}%`,
                    backgroundColor: anomalyCount >= 2 ? "#DC2626" : anomalyCount === 1 ? "#D97706" : "#0D9488"
                  }}
                />
              </div>
            </div>
            <span className="text-[10px] text-[#6B7280]">
              Formant / Vocoder phase rigidity intervals
            </span>
          </div>
        </div>
      </div>

      {/* Structured Evidence Reasons (Why Was This Flagged?) */}
      {risk_reasons && risk_reasons.length > 0 && (
        <div className="bg-[#FAFAFA] p-4 rounded-lg border border-[#E5E7EB]">
          <span className="text-xs font-semibold text-[#111111] uppercase tracking-wider block mb-2.5">
            Key Forensic Evidence & Analysis Findings
          </span>
          <ul className="space-y-1.5">
            {risk_reasons.map((reason, idx) => (
              <li key={idx} className="flex items-start space-x-2 text-xs text-[#374151]">
                <span className="text-[#4338CA] font-bold mt-0.5">•</span>
                <span className="leading-relaxed">{reason}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Plain language summary */}
      <div className="bg-[#FAFAFA] p-3.5 rounded-lg border border-[#E5E7EB]">
        <p className="text-xs text-[#374151] leading-relaxed">
          {plain_language_explanation}
        </p>
      </div>

      {/* Suggested Action Alert */}
      <div
        className="p-3.5 rounded-lg border text-xs leading-snug flex items-start space-x-2.5"
        style={{ backgroundColor: riskBg, borderColor: riskBorder, color: riskColor }}
      >
        <RiskIcon className="w-4 h-4 flex-shrink-0 mt-0.5 stroke-[2]" />
        <div>
          <span className="font-bold block">Recommended Action:</span>
          <span className="text-xs text-[#374151] mt-0.5 block">{suggested_action}</span>
        </div>
      </div>
    </div>
  );
}
