// VoiceGuard AI Multi-Target Resilient API Client

const LIVE_TUNNEL_URL = "https://suited-pieces-latinas-ranger.trycloudflare.com";

// Determine potential endpoints based on environment
function getCandidateBaseUrls() {
  const urls = [];
  
  if (import.meta.env.VITE_API_URL) {
    urls.push(`${import.meta.env.VITE_API_URL.replace(/\/$/, '')}/api`);
  }

  if (typeof window !== "undefined") {
    const isLocal = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
    if (isLocal) {
      urls.push("http://127.0.0.1:8000/api");
      urls.push("http://localhost:8000/api");
      urls.push(`${LIVE_TUNNEL_URL}/api`);
    } else {
      urls.push(`${LIVE_TUNNEL_URL}/api`);
      urls.push("http://127.0.0.1:8000/api");
      urls.push("http://localhost:8000/api");
    }
  } else {
    urls.push(`${LIVE_TUNNEL_URL}/api`);
    urls.push("http://127.0.0.1:8000/api");
  }

  // Deduplicate
  return Array.from(new Set(urls));
}

let cachedWorkingBaseUrl = null;

async function executeFetch(endpoint, options = {}) {
  const candidates = getCandidateBaseUrls();
  const orderedCandidates = cachedWorkingBaseUrl 
    ? [cachedWorkingBaseUrl, ...candidates.filter(c => c !== cachedWorkingBaseUrl)]
    : candidates;

  let lastError = null;

  for (const base of orderedCandidates) {
    const fullUrl = `${base}${endpoint}`;
    try {
      const res = await fetch(fullUrl, {
        ...options,
        headers: {
          ...(options.headers || {})
        }
      });

      if (res.ok) {
        cachedWorkingBaseUrl = base;
        return await res.json();
      } else {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server error (HTTP ${res.status})`);
      }
    } catch (err) {
      lastError = err;
      // Continue to next candidate
    }
  }

  throw lastError || new Error("Failed to reach VoiceGuard AI backend.");
}

export const FALLBACK_SAMPLES = [
  {
    id: "sample_1",
    title: "Digital Arrest Scam (AI Cloned Voice)",
    category: "Digital Arrest & High Threat",
    expected_risk: "High",
    description: "Synthetic voice clone impersonating Mumbai Police / Cyber Crime Branch alleging money laundering via an intercepted FedEx narcotics parcel, enforcing an illegal 'digital arrest'.",
    filename: "sample_1_digital_arrest_clone.wav"
  },
  {
    id: "sample_2",
    title: "OTP & KYC Expiry Fraud (Human Voice)",
    category: "Banking Credential Theft",
    expected_risk: "High",
    description: "Human scammer calling from fake bank fraud department demanding 6-digit OTP code to stop an unauthorized account suspension.",
    filename: "sample_2_otp_theft_human.wav"
  },
  {
    id: "sample_3",
    title: "AI Voice Clone (Benign Content)",
    category: "Synthetic Voice Only",
    expected_risk: "Medium",
    description: "Cloned AI synthetic voice discussing regular meeting scheduling without fraudulent intent.",
    filename: "sample_3_ai_clone_benign.wav"
  },
  {
    id: "sample_4",
    title: "Legitimate Support Call (Authentic Human)",
    category: "Safe / Bonafide",
    expected_risk: "Low",
    description: "Authentic human conversation from customer support confirming order delivery with no suspicious requests.",
    filename: "sample_4_legitimate_call.wav"
  }
];

export async function fetchSamples() {
  try {
    return await executeFetch("/samples");
  } catch (err) {
    console.warn("Using offline preset fallback samples:", err);
    return FALLBACK_SAMPLES;
  }
}

export function getSampleAudioUrl(filename) {
  const base = cachedWorkingBaseUrl || getCandidateBaseUrls()[0];
  return `${base}/samples/${filename}`;
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

  return await executeFetch("/analyze", {
    method: "POST",
    body: formData
  });
}

export async function submitCallReport(reportData) {
  return await executeFetch("/report", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(reportData)
  });
}

export async function fetchReports() {
  try {
    return await executeFetch("/reports");
  } catch (err) {
    console.warn("Failed to fetch reports:", err);
    return [];
  }
}
