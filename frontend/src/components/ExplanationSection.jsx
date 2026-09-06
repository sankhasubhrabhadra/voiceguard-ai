import React, { useState } from "react";
import { HelpCircle, ChevronDown, ChevronUp, Cpu, Info, AlertOctagon, CheckCircle2 } from "lucide-react";

export default function ExplanationSection({ voiceAnalysis, fusion }) {
  const [isOpen, setIsOpen] = useState(true);

  if (!voiceAnalysis || !fusion) return null;

  const { top_contributing_features = [], features, vocoder_biomarkers = [] } = voiceAnalysis;

  return (
    <div className="bg-white rounded-lg p-6 shadow-card border border-[#E5E7EB]/60">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between text-left focus:outline-none"
      >
        <div className="flex items-center space-x-2">
          <HelpCircle className="w-4 h-4 text-[#4338CA] stroke-[1.75]" />
          <h2 className="text-sm font-semibold text-[#111111] uppercase tracking-wider">
            4. Deep Vocoder Forensics & Acoustic Biomarkers
          </h2>
          {vocoder_biomarkers.length > 0 && (
            <span className="text-[10px] font-bold bg-[#FEF2F2] text-[#DC2626] border border-[#FEE2E2] px-2 py-0.5 rounded">
              {vocoder_biomarkers.length} Neural Vocoder Markers Found
            </span>
          )}
        </div>
        <div className="text-[#6B7280]">
          {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </button>

      {isOpen && (
        <div className="mt-5 space-y-6">
          {/* Detected Vocoder Physical Biomarkers */}
          {vocoder_biomarkers.length > 0 ? (
            <div>
              <div className="flex items-center space-x-1.5 mb-2.5">
                <AlertOctagon className="w-3.5 h-3.5 text-[#DC2626]" />
                <span className="text-xs font-semibold text-[#DC2626] uppercase tracking-wider">
                  Flagged Physical Neural Vocoder Signatures (ElevenLabs / OpenAI / VITS)
                </span>
              </div>

              <div className="space-y-2">
                {vocoder_biomarkers.map((bio, idx) => (
                  <div
                    key={idx}
                    className="p-3 bg-[#FEF2F2]/60 rounded-lg border border-[#FEE2E2] text-xs"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-[#DC2626]">{bio.name}</span>
                      <span className="text-[10px] font-mono bg-white px-2 py-0.5 rounded border border-[#FEE2E2] text-[#111111]">
                        Measured: <strong>{bio.value}</strong> (Human: {bio.normal})
                      </span>
                    </div>
                    <p className="text-[11px] text-[#4B5563] mt-1.5">
                      {bio.explanation}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="flex items-center space-x-2 text-xs font-semibold text-[#0D9488] bg-[#F0FDFA] p-3 rounded-lg border border-[#CCFBF1]">
              <CheckCircle2 className="w-4 h-4 stroke-[2]" />
              <span>No mathematical vocoder phase artifacts or unnatural pitch spline curves detected.</span>
            </div>
          )}

          {/* Top Contributing Acoustic Forensics Table */}
          <div>
            <div className="flex items-center space-x-1.5 mb-2.5">
              <Cpu className="w-3.5 h-3.5 text-[#4338CA]" />
              <span className="text-xs font-semibold text-[#111111] uppercase tracking-wider">
                Acoustic Feature Importance Rankings
              </span>
            </div>

            <div className="space-y-2.5">
              {top_contributing_features.map((item, idx) => (
                <div
                  key={idx}
                  className="p-3 bg-[#FAFAFA] rounded-lg border border-[#E5E7EB] hover:border-[#D1D5DB] transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <span className="text-xs font-semibold text-[#111111]">
                        {item.name}
                      </span>
                      <span className="text-[11px] text-[#6B7280] ml-2">
                        Measured: <strong className="text-[#111111]">{item.value}</strong> (Normal: {item.normal_range})
                      </span>
                    </div>
                    <span className="text-[10px] font-bold bg-white px-2 py-0.5 rounded border border-[#E5E7EB] text-[#4338CA]">
                      {item.weight_pct}% Weight
                    </span>
                  </div>

                  <p className="text-[11px] text-[#4B5563] mt-1.5">
                    {item.description}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Detailed Metric Quick Table */}
          {features && (
            <div>
              <span className="text-xs font-semibold text-[#111111] uppercase tracking-wider block mb-2">
                Raw Extracted Signal Telemetry
              </span>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                <div className="bg-[#FAFAFA] p-2.5 rounded-lg border border-[#E5E7EB] text-center">
                  <span className="text-[10px] text-[#6B7280] uppercase block">Mean Pitch F0</span>
                  <span className="text-xs font-bold text-[#111111]">{features.mean_pitch_hz} Hz</span>
                </div>
                <div className="bg-[#FAFAFA] p-2.5 rounded-lg border border-[#E5E7EB] text-center">
                  <span className="text-[10px] text-[#6B7280] uppercase block">Pitch Jitter</span>
                  <span className="text-xs font-bold text-[#111111]">{features.pitch_jitter_local}%</span>
                </div>
                <div className="bg-[#FAFAFA] p-2.5 rounded-lg border border-[#E5E7EB] text-center">
                  <span className="text-[10px] text-[#6B7280] uppercase block">F0 Acceleration Var</span>
                  <span className="text-xs font-bold text-[#111111]">{features.pitch_acceleration_variance}</span>
                </div>
                <div className="bg-[#FAFAFA] p-2.5 rounded-lg border border-[#E5E7EB] text-center">
                  <span className="text-[10px] text-[#6B7280] uppercase block">Silence Floor</span>
                  <span className="text-xs font-bold text-[#111111]">{features.silence_noise_floor_db} dB</span>
                </div>
              </div>
            </div>
          )}

          {/* Model calibration note */}
          <div className="bg-white p-3 rounded-lg border border-[#E5E7EB] text-[11px] text-[#6B7280] flex items-start space-x-2">
            <Info className="w-4 h-4 text-[#4338CA] flex-shrink-0 mt-0.5 stroke-[1.75]" />
            <p>
              Voice authenticity is evaluated via an ensemble combining physical neural vocoder biomarker inspection (F0 jerk smoothness, spectral flux variance, pause digital zero purity) and a Random Forest classifier trained on ASVspoof 2019 logical access benchmarks.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
