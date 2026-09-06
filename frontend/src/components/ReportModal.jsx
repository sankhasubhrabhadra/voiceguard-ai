import React, { useState } from "react";
import { X, Flag, CheckCircle } from "lucide-react";
import { submitCallReport } from "../services/api";

export default function ReportModal({ isOpen, onClose, analysisData, onReportSuccess }) {
  const [callerNumber, setCallerNumber] = useState("");
  const [notes, setNotes] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submittedId, setSubmittedId] = useState(null);
  const [error, setError] = useState(null);

  if (!isOpen || !analysisData) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const payload = {
        caller_number: callerNumber.trim() || "Unknown Suspect Number",
        audio_filename: analysisData.filename,
        risk_level: analysisData.fusion.risk_level,
        overall_risk_score: analysisData.fusion.overall_risk_score,
        voice_risk_score: analysisData.fusion.voice_risk_score,
        script_risk_score: analysisData.fusion.script_risk_score,
        transcript_snippet: analysisData.transcript_analysis?.full_transcript?.slice(0, 200) || "",
        notes: notes.trim()
      };

      const res = await submitCallReport(payload);
      setSubmittedId(res.report_id);
      if (onReportSuccess) onReportSuccess();
    } catch (err) {
      setError(err.message || "Failed to submit report");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    setSubmittedId(null);
    setCallerNumber("");
    setNotes("");
    setError(null);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4 backdrop-blur-sm">
      <div className="bg-white rounded-lg max-w-md w-full p-6 shadow-xl border border-[#E5E7EB]">
        <div className="flex items-center justify-between pb-3 border-b border-[#F3F4F6]">
          <div className="flex items-center space-x-2">
            <div className="w-7 h-7 rounded-lg bg-[#FEF2F2] flex items-center justify-center text-[#DC2626]">
              <Flag className="w-4 h-4 stroke-[2]" />
            </div>
            <h3 className="text-sm font-semibold text-[#111111]">
              Report Suspect Scam Call
            </h3>
          </div>
          <button
            onClick={handleClose}
            className="text-[#9CA3AF] hover:text-[#111111] p-1 rounded-lg"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {submittedId ? (
          <div className="py-6 text-center space-y-3">
            <div className="w-12 h-12 rounded-full bg-[#F0FDFA] text-[#0D9488] mx-auto flex items-center justify-center">
              <CheckCircle className="w-6 h-6 stroke-[2]" />
            </div>
            <h4 className="text-sm font-bold text-[#111111]">
              Incident Logged Successfully
            </h4>
            <p className="text-xs text-[#6B7280]">
              Report Reference ID: <span className="font-mono font-bold text-[#111111]">{submittedId}</span>
            </p>
            <p className="text-[11px] text-[#6B7280]">
              The acoustic markers and extracted fraud script patterns have been logged to the local forensics audit store.
            </p>
            <button
              onClick={handleClose}
              className="mt-4 w-full bg-[#4338CA] hover:bg-[#3730A3] text-white text-xs font-semibold py-2.5 rounded-lg transition-colors"
            >
              Done
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="mt-4 space-y-4">
            <div>
              <label className="text-xs font-semibold text-[#374151] block mb-1">
                Caller Phone Number (if available)
              </label>
              <input
                type="text"
                value={callerNumber}
                onChange={(e) => setCallerNumber(e.target.value)}
                placeholder="+91-XXXXXXXXXX / Unknown"
                className="w-full text-xs text-[#111111] bg-[#FAFAFA] border border-[#E5E7EB] rounded-lg p-2.5 focus:outline-none focus:border-[#4338CA]"
              />
            </div>

            <div className="bg-[#FAFAFA] p-3 rounded-lg border border-[#E5E7EB] text-xs space-y-1">
              <div className="flex justify-between">
                <span className="text-[#6B7280]">Audio Recording:</span>
                <span className="font-semibold text-[#111111] truncate max-w-[200px]">{analysisData.filename}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#6B7280]">Fused Risk Level:</span>
                <span className="font-bold text-[#DC2626]">{analysisData.fusion.risk_level} ({analysisData.fusion.overall_risk_score}%)</span>
              </div>
            </div>

            <div>
              <label className="text-xs font-semibold text-[#374151] block mb-1">
                Incident Remarks & Context (Optional)
              </label>
              <textarea
                rows={3}
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="E.g. Caller claimed to be Mumbai Cyber Crime police regarding an intercepted DHL courier package."
                className="w-full text-xs text-[#111111] bg-[#FAFAFA] border border-[#E5E7EB] rounded-lg p-2.5 focus:outline-none focus:border-[#4338CA]"
              />
            </div>

            {error && (
              <p className="text-xs text-[#DC2626] bg-[#FEF2F2] p-2 rounded-lg border border-[#FEE2E2]">
                {error}
              </p>
            )}

            <div className="flex space-x-2 pt-2">
              <button
                type="button"
                onClick={handleClose}
                className="flex-1 bg-white hover:bg-[#F3F4F6] text-[#374151] text-xs font-semibold py-2.5 rounded-lg border border-[#E5E7EB] transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="flex-1 bg-[#DC2626] hover:bg-[#B91C1C] text-white text-xs font-semibold py-2.5 rounded-lg transition-colors flex items-center justify-center space-x-1"
              >
                {isSubmitting ? "Logging..." : "Confirm & Report"}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
