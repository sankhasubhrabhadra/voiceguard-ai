import React, { useState, useEffect } from "react";
import { X, FileText, AlertOctagon, CheckCircle2, AlertTriangle, RefreshCw } from "lucide-react";
import { fetchReports } from "../services/api";

export default function ReportedCallsList({ isOpen, onClose }) {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadReports = async () => {
    setLoading(true);
    try {
      const data = await fetchReports();
      setReports(data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadReports();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4 backdrop-blur-sm">
      <div className="bg-white rounded-lg max-w-2xl w-full p-6 shadow-xl border border-[#E5E7EB] max-h-[85vh] flex flex-col">
        <div className="flex items-center justify-between pb-3 border-b border-[#F3F4F6]">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg bg-[#EEF2FF] flex items-center justify-center text-[#4338CA]">
              <FileText className="w-4 h-4 stroke-[1.75]" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-[#111111]">
                Scam Incident Forensics Log
              </h3>
              <p className="text-[11px] text-[#6B7280]">
                Local SQLite store of flagged calls and forensic risk telemetry
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={loadReports}
              disabled={loading}
              className="text-[#6B7280] hover:text-[#111111] p-1.5 rounded-lg hover:bg-[#F3F4F6] transition-colors"
              title="Refresh logs"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            </button>
            <button
              onClick={onClose}
              className="text-[#9CA3AF] hover:text-[#111111] p-1.5 rounded-lg hover:bg-[#F3F4F6]"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Content list */}
        <div className="overflow-y-auto flex-1 mt-4 space-y-3 pr-1">
          {reports.length === 0 ? (
            <div className="text-center py-12 text-[#9CA3AF] text-xs">
              {loading ? "Loading incident logs..." : "No calls have been reported yet."}
            </div>
          ) : (
            reports.map((r) => {
              let badgeColor = "bg-[#FEF2F2] text-[#DC2626] border-[#FEE2E2]";
              if (r.risk_level === "Medium") badgeColor = "bg-[#FFFBEB] text-[#D97706] border-[#FEF3C7]";
              else if (r.risk_level === "Low") badgeColor = "bg-[#F0FDFA] text-[#0D9488] border-[#CCFBF1]";

              return (
                <div
                  key={r.id}
                  className="p-3.5 bg-[#FAFAFA] rounded-lg border border-[#E5E7EB] hover:border-[#D1D5DB] transition-colors text-xs space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className="font-mono font-bold text-[#111111]">{r.id}</span>
                      <span className="text-[#6B7280]">•</span>
                      <span className="font-semibold text-[#374151]">{r.caller_number}</span>
                    </div>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase ${badgeColor}`}>
                      {r.risk_level} ({Math.round(r.overall_risk_score)}%)
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-[11px] text-[#6B7280]">
                    <div>
                      <span>Voice Clone Risk: </span>
                      <strong className="text-[#111111]">{Math.round(r.voice_risk_score)}%</strong>
                    </div>
                    <div>
                      <span>Script Fraud Risk: </span>
                      <strong className="text-[#111111]">{Math.round(r.script_risk_score)}%</strong>
                    </div>
                  </div>

                  {r.transcript_snippet && (
                    <div className="bg-white p-2 rounded border border-[#E5E7EB]/80 text-[11px] text-[#4B5563] italic font-serif">
                      "{r.transcript_snippet}..."
                    </div>
                  )}

                  {r.notes && (
                    <p className="text-[11px] text-[#374151]">
                      <strong>Notes:</strong> {r.notes}
                    </p>
                  )}

                  <div className="text-[10px] text-[#9CA3AF] flex justify-between pt-1 border-t border-[#E5E7EB]/50">
                    <span>File: {r.audio_filename}</span>
                    <span>{new Date(r.created_at).toLocaleString()}</span>
                  </div>
                </div>
              );
            })
          )}
        </div>

        <div className="pt-3 mt-3 border-t border-[#F3F4F6] flex justify-end">
          <button
            onClick={onClose}
            className="bg-[#FAFAFA] hover:bg-[#F3F4F6] text-[#374151] text-xs font-semibold px-4 py-2 rounded-lg border border-[#E5E7EB] transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
