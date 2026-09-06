import sys
import os
import requests

sys.stdout.reconfigure(encoding='utf-8')

url = "http://127.0.0.1:8000/api/analyze"

f1 = r"C:\Users\Lenovo\Downloads\ai_fraud_call_spoken_demo.wav"
f2 = r"C:\Users\Lenovo\Downloads\lawyer_benign_test.wav"

for path in [f1, f2]:
    print("=" * 75)
    name = os.path.basename(path)
    print(f"TESTING API WITH: {name}")
    with open(path, "rb") as fp:
        files = {"file": (name, fp, "audio/wav")}
        resp = requests.post(url, files=files)
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"Analysis ID: {data['analysis_id']}")
        print(f"Audio Hash: {data['audio_hash'][:16]}")
        print(f"Duration: {data['duration']}s, Sample Rate: {data['sample_rate']}, Samples: {data['num_samples']}")
        print(f"1. Voice Clone Probability: {data['fusion']['voice_risk_score']}% (Is Cloned: {data['voice_analysis']['is_cloned']})")
        print(f"2. Scam Script Intent: {data['fusion']['script_risk_score']}% (Categories: {data['transcript_analysis']['detected_categories']})")
        print(f"3. Social Engineering: {data['fusion']['social_engineering_score']}% (Credential Theft: {data['transcript_analysis']['social_engineering']['credential_request']})")
        print(f"4. Acoustic Anomalies: {len(data['voice_analysis']['anomalous_regions'])} intervals")
        print(f"5. Overall Risk: {data['fusion']['overall_risk_score']}% [{data['fusion']['risk_level']} Risk]")
        print("Reasons:")
        for r in data['fusion']['risk_reasons']:
            print(f"  * {r}")
    else:
        print(f"Error {resp.status_code}: {resp.text}")
