// Primary Cloudflare Tunnel fallback for cloud deployments (e.g. Vercel)
const LIVE_TUNNEL_URL = "https://suited-pieces-latinas-ranger.trycloudflare.com";

const getBaseUrl = () => {
  if (import.meta.env.VITE_API_URL) {
    return `${import.meta.env.VITE_API_URL.replace(/\/$/, '')}/api`;
  }
  if (typeof window !== "undefined") {
    const host = window.location.hostname;
    if (host === "localhost" || host === "127.0.0.1") {
      return "http://127.0.0.1:8000/api";
    }
  }
  return `${LIVE_TUNNEL_URL}/api`;
};

const API_BASE_URL = getBaseUrl();

export async function fetchSamples() {
  try {
    const res = await fetch(`${API_BASE_URL}/samples`);
    if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch test samples from ${API_BASE_URL}`);
    return await res.json();
  } catch (err) {
    console.error(`API Error on ${API_BASE_URL}/samples:`, err);
    throw new Error(`Failed to connect to backend at ${API_BASE_URL}. Ensure the backend is running.`);
  }
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
