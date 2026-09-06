import React, { useState } from "react";
import { MessageSquare, AlertTriangle, ShieldCheck, ChevronDown, ChevronUp, UserX, ShieldAlert, CheckCircle } from "lucide-react";

export default function TranscriptViewer({ transcriptAnalysis }) {
  const [isOpen, setIsOpen] = useState(true);

  if (!transcriptAnalysis) return null;

  const {
    full_transcript,
    script_risk_score,
    detected_categories = [],
    matches = [],
    segments = [],
    social_engineering
  } = transcriptAnalysis;

  const flaggedIntents = social_engineering?.flagged_intents || [];

  return (
    <div className="bg-white rounded-lg p-6 shadow-card border border-[#E5E7EB]/60">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between text-left focus:outline-none"
      >
        <div className="flex items-center space-x-2">
          <MessageSquare className="w-4 h-4 text-[#4338CA] stroke-[1.75]" />
          <h2 className="text-sm font-semibold text-[#111111] uppercase tracking-wider">
            3. Whisper Speech-to-Text & Conversational Intent Analysis
          </h2>
          {detected_categories.length > 0 && (
            <span className="text-[10px] font-bold bg-[#FEF2F2] text-[#DC2626] border border-[#FEE2E2] px-2 py-0.5 rounded">
              {detected_categories.length} Fraud Patterns
            </span>
          )}
        </div>
        <div className="text-[#6B7280]">
          {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </button>

      {isOpen && (
        <div className="mt-4 space-y-4">
          {/* Social Engineering & Behavioral Intent Badges */}
          {flaggedIntents.length > 0 && (
            <div className="space-y-1.5">
              <span className="text-[10px] font-semibold text-[#6B7280] uppercase tracking-wider block">
                Behavioral & Intent Indicators Detected:
              </span>
              <div className="flex flex-wrap gap-1.5">
                {flaggedIntents.map((intent, idx) => {
                  const isRefusal = intent.includes("Refusal") || intent.includes("Resistance");
                  const isEdu = intent.includes("Awareness") || intent.includes("Simulation");
                  return (
                    <span
                      key={idx}
                      className={`text-[10px] font-semibold px-2.5 py-1 rounded border flex items-center space-x-1 ${
                        isRefusal
                          ? "bg-[#F0FDFA] text-[#0D9488] border-[#CCFBF1]"
                          : isEdu
                          ? "bg-[#EEF2FF] text-[#4338CA] border-[#C7D2FE]"
                          : "bg-[#FEF2F2] text-[#DC2626] border-[#FEE2E2]"
                      }`}
                    >
                      {isRefusal ? (
                        <CheckCircle className="w-3 h-3 stroke-[2]" />
                      ) : isEdu ? (
                        <ShieldCheck className="w-3 h-3 stroke-[2]" />
                      ) : (
                        <ShieldAlert className="w-3 h-3 stroke-[2]" />
                      )}
                      <span>{intent}</span>
                    </span>
                  );
                })}
              </div>
            </div>
          )}

          {/* Detected Category Badges */}
          {detected_categories.length > 0 ? (
            <div className="flex flex-wrap gap-2 pt-1">
              {detected_categories.map((cat, idx) => (
                <div
                  key={idx}
                  className="flex items-center space-x-1.5 bg-[#FEF2F2] text-[#DC2626] border border-[#FEE2E2] px-2.5 py-1 rounded-lg text-xs font-semibold"
                >
                  <AlertTriangle className="w-3.5 h-3.5 stroke-[2]" />
                  <span>{cat}</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex items-center space-x-2 text-xs font-semibold text-[#0D9488] bg-[#F0FDFA] p-2.5 rounded-lg border border-[#CCFBF1]">
              <ShieldCheck className="w-4 h-4 stroke-[2]" />
              <span>No known scam-script phrases or coercive intimidation patterns matched.</span>
            </div>
          )}

          {/* Timestamped Utterance Segments with Role Badges */}
          {segments.length > 0 ? (
            <div className="space-y-2">
              <span className="text-[11px] font-semibold text-[#6B7280] uppercase tracking-wider block">
                Timestamped Conversational Segments:
              </span>
              <div className="space-y-1.5 max-h-64 overflow-y-auto pr-1">
                {segments.map((seg, idx) => {
                  const role = seg.role_tag || "General";
                  const isAttacker = role === "Attacker Request";
                  const isRefusal = role === "Victim Refusal";
                  const isEdu = role === "Educational Note";

                  return (
                    <div
                      key={idx}
                      className={`p-2.5 rounded-lg border text-xs transition-colors ${
                        isAttacker
                          ? "bg-[#FEF2F2]/80 border-[#FEE2E2]"
                          : isRefusal
                          ? "bg-[#F0FDFA]/80 border-[#CCFBF1]"
                          : isEdu
                          ? "bg-[#EEF2FF]/80 border-[#C7D2FE]"
                          : "bg-[#FAFAFA] border-[#E5E7EB]"
                      }`}
                    >
                      <div className="flex items-center justify-between text-[10px] text-[#6B7280] mb-1">
                        <span className="font-mono font-medium">
                          [{seg.start_time.toFixed(1)}s - {seg.end_time.toFixed(1)}s]
                        </span>
                        {role !== "General" && (
                          <span
                            className={`font-bold px-1.5 py-0.5 rounded border text-[9px] ${
                              isAttacker
                                ? "bg-white text-[#DC2626] border-[#FEE2E2]"
                                : isRefusal
                                ? "bg-white text-[#0D9488] border-[#CCFBF1]"
                                : "bg-white text-[#4338CA] border-[#C7D2FE]"
                            }`}
                          >
                            {role}
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-[#111111] leading-snug">{seg.text}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            /* Full Transcript Box Fallback */
            <div className="bg-[#FAFAFA] rounded-lg p-4 border border-[#E5E7EB]">
              <span className="text-[11px] font-semibold text-[#6B7280] uppercase tracking-wider block mb-1.5">
                Decoded Speech Transcript:
              </span>
              <p className="text-xs text-[#111111] leading-relaxed font-normal">
                {full_transcript || "No audible speech recognized."}
              </p>
            </div>
          )}

          {/* Matched Pattern Snippets & Semantic Similarity */}
          {matches.length > 0 && (
            <div className="space-y-2 pt-2">
              <span className="text-[11px] font-semibold text-[#6B7280] uppercase tracking-wider block">
                Semantic Matches Against Fraud Knowledgebase:
              </span>
              <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
                {matches.map((m, idx) => (
                  <div
                    key={idx}
                    className="p-3 bg-white rounded-lg border border-[#E5E7EB] hover:border-[#D1D5DB] transition-colors"
                  >
                    <div className="flex items-center justify-between text-xs mb-1">
                      <span className="font-semibold text-[#DC2626]">{m.category}</span>
                      <span className="text-[10px] font-bold bg-[#FEF2F2] text-[#DC2626] px-2 py-0.5 rounded border border-[#FEE2E2]">
                        {m.similarity_score}% Match
                      </span>
                    </div>
                    <div className="text-xs text-[#111111] bg-[#FAFAFA] p-2 rounded border border-[#E5E7EB]/60 font-mono text-[11px]">
                      "{m.matched_phrase}"
                    </div>
                    <p className="text-[11px] text-[#6B7280] mt-1.5">{m.description}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
