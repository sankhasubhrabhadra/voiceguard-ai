import React from "react";
import { Shield, FileText } from "lucide-react";

export default function Header({ onOpenReports, reportCount = 0 }) {
  return (
    <header className="w-full bg-[#FAFAFA] border-b border-[#E5E7EB]/60 py-4 px-6 md:px-12">
      <div className="max-w-6xl mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-lg bg-[#4338CA] flex items-center justify-center text-white">
            <Shield className="w-5 h-5 stroke-[1.75]" />
          </div>
          <div>
            <h1 className="text-base font-semibold text-[#111111] tracking-tight">
              VoiceGuard AI
            </h1>
            <p className="text-xs text-[#6B7280]">
              Real-Time Voice Clone & Scam-Call Forensics
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={onOpenReports}
            className="flex items-center space-x-2 text-xs font-semibold text-[#374151] bg-white hover:bg-[#F3F4F6] px-3.5 py-2 rounded-lg shadow-card border border-[#E5E7EB] transition-colors"
          >
            <FileText className="w-4 h-4 stroke-[1.75] text-[#6B7280]" />
            <span>Reported Incidents</span>
            {reportCount > 0 && (
              <span className="bg-[#4338CA] text-white text-[10px] px-1.5 py-0.5 rounded-full font-bold">
                {reportCount}
              </span>
            )}
          </button>
        </div>
      </div>
    </header>
  );
}
