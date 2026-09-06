import React from "react";
import { Play } from "lucide-react";

export default function SampleAudioSelector({
  samples,
  selectedSample,
  onSelectSample,
  isLoading
}) {
  return (
    <div className="bg-white rounded-lg p-6 shadow-card border border-[#E5E7EB]/60">
      <div className="mb-3">
        <h2 className="text-sm font-semibold text-[#111111] uppercase tracking-wider">
          Or Select Demo Preset Call
        </h2>
        <p className="text-xs text-[#6B7280] mt-0.5">
          Instantly load and test real-world attack vectors & authentic benchmark calls
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-4">
        {samples.map((sample) => {
          const isSelected = selectedSample?.filename === sample.filename;
          
          let riskBadgeClass = "bg-[#F0FDFA] text-[#0D9488] border-[#CCFBF1]";
          if (sample.expected_risk === "High") {
            riskBadgeClass = "bg-[#FEF2F2] text-[#DC2626] border-[#FEE2E2]";
          } else if (sample.expected_risk === "Medium") {
            riskBadgeClass = "bg-[#FFFBEB] text-[#D97706] border-[#FEF3C7]";
          }

          return (
            <div
              key={sample.id}
              onClick={() => !isLoading && onSelectSample(sample)}
              className={`p-3.5 rounded-lg border text-left cursor-pointer transition-all ${
                isSelected
                  ? "border-[#4338CA] bg-[#EEF2FF]/40 shadow-sm"
                  : "border-[#E5E7EB] hover:border-[#D1D5DB] bg-white"
              } ${isLoading ? "opacity-60 cursor-not-allowed" : ""}`}
            >
              <div className="flex items-start justify-between">
                <span className="text-xs font-semibold text-[#111111] leading-snug">
                  {sample.title}
                </span>
                <span
                  className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase tracking-wider ${riskBadgeClass}`}
                >
                  {sample.expected_risk}
                </span>
              </div>
              <p className="text-[11px] text-[#6B7280] mt-1 line-clamp-2">
                {sample.description}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
