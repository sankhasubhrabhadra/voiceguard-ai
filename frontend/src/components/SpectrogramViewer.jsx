import React, { useState } from "react";
import { ChevronDown, ChevronUp, AlertCircle, Activity } from "lucide-react";

export default function SpectrogramViewer({ spectrogramData, anomalousRegions = [], duration = 0 }) {
  const [isOpen, setIsOpen] = useState(true);

  if (!spectrogramData) return null;

  const { waveform, spectrogram } = spectrogramData;
  const { times = [], frequencies = [], matrix = [] } = spectrogram || {};
  const { times: waveTimes = [], min: waveMin = [], max: waveMax = [] } = waveform || {};

  // Mel Frequency colors: dark indigo (#312E81) -> teal (#0D9488) -> amber (#D97706) -> red (#DC2626)
  const getHeatmapColor = (val) => {
    // val is 0 - 100
    if (val < 25) return "#1E1B4B"; // deep indigo/black
    if (val < 50) return "#312E81"; // indigo
    if (val < 75) return "#0D9488"; // teal
    if (val < 90) return "#D97706"; // amber
    return "#DC2626"; // hot red
  };

  return (
    <div className="bg-white rounded-lg p-6 shadow-card border border-[#E5E7EB]/60">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between text-left focus:outline-none"
      >
        <div className="flex items-center space-x-2">
          <Activity className="w-4 h-4 text-[#4338CA] stroke-[1.75]" />
          <h2 className="text-sm font-semibold text-[#111111] uppercase tracking-wider">
            2. Waveform & Spectral Forensics
          </h2>
          {anomalousRegions.length > 0 && (
            <span className="text-[10px] font-bold bg-[#FEF2F2] text-[#DC2626] border border-[#FEE2E2] px-2 py-0.5 rounded">
              {anomalousRegions.length} Anomaly Zones Flagged
            </span>
          )}
        </div>
        <div className="text-[#6B7280]">
          {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </button>

      {isOpen && (
        <div className="mt-4 space-y-5">
          {/* Anomaly Callout Badges */}
          {anomalousRegions.length > 0 && (
            <div className="space-y-2">
              <span className="text-[11px] font-semibold text-[#6B7280] uppercase tracking-wider block">
                Flagged Audio Forensics Intervals:
              </span>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {anomalousRegions.map((anom, idx) => (
                  <div
                    key={idx}
                    className="p-2.5 bg-[#FEF2F2]/60 rounded-lg border border-[#FEE2E2] flex items-start space-x-2 text-xs"
                  >
                    <AlertCircle className="w-4 h-4 text-[#DC2626] flex-shrink-0 mt-0.5 stroke-[2]" />
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="font-semibold text-[#DC2626]">{anom.anomaly_type}</span>
                        <span className="text-[10px] bg-white px-1.5 py-0.5 rounded border border-[#FEE2E2] text-[#6B7280]">
                          {anom.start_time}s - {anom.end_time}s
                        </span>
                      </div>
                      <p className="text-[11px] text-[#4B5563] mt-0.5">{anom.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Waveform Envelope */}
          <div>
            <div className="flex justify-between items-center mb-1 text-[11px] text-[#6B7280]">
              <span className="font-semibold uppercase tracking-wider">Acoustic Amplitude Envelope</span>
              <span>{duration > 0 ? `${duration}s` : ""}</span>
            </div>
            <div className="relative w-full h-16 bg-[#FAFAFA] rounded-lg border border-[#E5E7EB] overflow-hidden flex items-center px-1">
              {/* Render waveform bars */}
              <div className="w-full h-full flex items-center justify-between">
                {waveTimes.map((t, idx) => {
                  const minV = waveMin[idx] || 0;
                  const maxV = waveMax[idx] || 0;
                  const heightPct = Math.min(100, Math.max(8, Math.abs(maxV - minV) * 90));
                  
                  // Check if in anomalous region
                  const isAnom = anomalousRegions.some(
                    (a) => t >= a.start_time && t <= a.end_time
                  );

                  return (
                    <div
                      key={idx}
                      className="w-1 rounded-sm mx-[0.5px] transition-all"
                      style={{
                        height: `${heightPct}%`,
                        backgroundColor: isAnom ? "#DC2626" : "#4338CA",
                        opacity: isAnom ? 0.9 : 0.65
                      }}
                      title={`t=${t}s, amp=${heightPct.toFixed(1)}%`}
                    />
                  );
                })}
              </div>

              {/* Anomaly highlight overlays on waveform */}
              {anomalousRegions.map((anom, idx) => {
                if (duration <= 0) return null;
                const leftPct = (anom.start_time / duration) * 100;
                const widthPct = Math.max(4, ((anom.end_time - anom.start_time) / duration) * 100);
                return (
                  <div
                    key={idx}
                    className="absolute top-0 bottom-0 bg-[#DC2626]/15 border-x border-[#DC2626]/40 pointer-events-none"
                    style={{ left: `${leftPct}%`, width: `${widthPct}%` }}
                  />
                );
              })}
            </div>
          </div>

          {/* Mel-Spectrogram Heatmap */}
          <div>
            <div className="flex justify-between items-center mb-1 text-[11px] text-[#6B7280]">
              <span className="font-semibold uppercase tracking-wider">Time-Frequency Spectrogram (0 - 8 kHz)</span>
              <div className="flex items-center space-x-2 text-[10px]">
                <span className="text-[#6B7280]">Energy:</span>
                <span className="inline-block w-3 h-2 rounded-sm bg-[#1E1B4B]"></span>
                <span className="inline-block w-3 h-2 rounded-sm bg-[#312E81]"></span>
                <span className="inline-block w-3 h-2 rounded-sm bg-[#0D9488]"></span>
                <span className="inline-block w-3 h-2 rounded-sm bg-[#D97706]"></span>
                <span className="inline-block w-3 h-2 rounded-sm bg-[#DC2626]"></span>
              </div>
            </div>

            <div className="relative w-full h-32 bg-[#111827] rounded-lg border border-[#374151] overflow-hidden flex flex-col justify-between p-1">
              {/* Frequency grid */}
              <div className="w-full h-full flex flex-col justify-between">
                {/* 6 frequency bands from high to low */}
                {[...Array(6)].map((_, fIdx) => {
                  const reversedFIdx = 5 - fIdx;
                  return (
                    <div key={fIdx} className="w-full flex-1 flex items-center my-[0.5px]">
                      {matrix.map((timeFrame, tIdx) => {
                        const binValue = timeFrame[reversedFIdx * 5] || 0;
                        const cellColor = getHeatmapColor(binValue);
                        return (
                          <div
                            key={tIdx}
                            className="flex-1 h-full mx-[0.5px] rounded-[1px]"
                            style={{ backgroundColor: cellColor }}
                            title={`t=${times[tIdx]}s, energy=${binValue}`}
                          />
                        );
                      })}
                    </div>
                  );
                })}
              </div>

              {/* Anomaly highlight overlays on spectrogram */}
              {anomalousRegions.map((anom, idx) => {
                if (duration <= 0) return null;
                const leftPct = (anom.start_time / duration) * 100;
                const widthPct = Math.max(4, ((anom.end_time - anom.start_time) / duration) * 100);
                return (
                  <div
                    key={idx}
                    className="absolute top-0 bottom-0 border-2 border-[#DC2626] bg-[#DC2626]/20 pointer-events-none rounded"
                    style={{ left: `${leftPct}%`, width: `${widthPct}%` }}
                  >
                    <span className="absolute top-1 left-1 bg-[#DC2626] text-white text-[9px] font-bold px-1 py-0.5 rounded leading-none">
                      Artifact Zone
                    </span>
                  </div>
                );
              })}
            </div>

            <div className="flex justify-between text-[10px] text-[#6B7280] mt-1 px-1">
              <span>0.0s</span>
              <span>Time Axis</span>
              <span>{duration > 0 ? `${duration}s` : "End"}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
