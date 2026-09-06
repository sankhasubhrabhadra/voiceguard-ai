import sys
import os
import requests

sys.stdout.reconfigure(encoding='utf-8')

audio_path = r"C:\Users\Lenovo\Downloads\ai_fraud_call_spoken_demo.wav"
url = "http://127.0.0.1:8000/api/analyze"

with open(audio_path, "rb") as f:
    files = {"file": ("ai_fraud_call_spoken_demo.wav", f, "audio/wav")}
    response = requests.post(url, files=files)

if response.status_code == 200:
    data = response.json()
    print("API ANALYZE SUCCESS:")
    print(f"Filename: {data['filename']}")
    print(f"Overall Risk: {data['fusion']['overall_risk_score']}% ({data['fusion']['risk_level']})")
    print(f"Voice Authenticity: {data['fusion']['voice_risk_score']}%")
    print(f"Scam Script Intent: {data['fusion']['script_risk_score']}%")
    print(f"Social Engineering: {data['fusion']['social_engineering_score']}%")
    print(f"Acoustic Anomalies: {data['fusion']['acoustic_anomaly_score']}%")
    print(f"Is Simulation: {data['fusion']['is_simulation_detected']}")
    print("Risk Reasons:")
    for r in data['fusion']['risk_reasons']:
        print(f"  * {r}")
    print(f"Suggested Action: {data['fusion']['suggested_action']}")
else:
    print(f"Error {response.status_code}: {response.text}")
