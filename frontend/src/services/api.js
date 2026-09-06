const API_BASE_URL = import.meta.env.VITE_API_URL 
  ? `${import.meta.env.VITE_API_URL.replace(/\/$/, '')}/api`
  : "http://localhost:8000/api";

export async function fetchSamples() {
  const res = await fetch(`${API_BASE_URL}/samples`);
  if (!res.ok) throw new Error("Failed to fetch test samples");
  return res.json();
}

export function getSampleAudioUrl(filename) {
  return `${API_BASE_URL}/samples/${filename}`;
}

export async function analyzeAudio({ file, sampleFilename, transcriptOverride }) {
  const formData = new FormData();
  if (file) {
    formData.append("file", file);
  }
  if (sampleFilename) {
    formData.append("sample_filename", sampleFilename);
  }
  if (transcriptOverride) {
    formData.append("transcript_override", transcriptOverride);
  }

  const res = await fetch(`${API_BASE_URL}/analyze`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "Audio analysis failed");
  }

  return res.json();
}

export async function submitCallReport(reportData) {
  const res = await fetch(`${API_BASE_URL}/report`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(reportData),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to submit call report");
  }

  return res.json();
}

export async function fetchReports() {
  const res = await fetch(`${API_BASE_URL}/reports`);
  if (!res.ok) throw new Error("Failed to fetch reports");
  return res.json();
}
