import requests
import json

def run_api_tests():
    samples = [
        ("sample_1_digital_arrest_clone.wav", "High"),
        ("sample_2_otp_theft_human.wav", "High"),
        ("sample_3_ai_clone_benign.wav", "Medium"),
        ("sample_4_legitimate_call.wav", "Low")
    ]

    for fname, expected in samples:
        print(f"\n=======================================================")
        print(f"Testing Analysis on: {fname} (Expected: {expected})")
        print(f"=======================================================")
        res = requests.post("http://127.0.0.1:8000/api/analyze", data={"sample_filename": fname})
        assert res.status_code == 200, f"API Error: {res.text}"
        data = res.json()
        fusion = data["fusion"]
        voice = data["voice_analysis"]
        transcript = data["transcript_analysis"]

        print(f"-> Fused Risk Score: {fusion['overall_risk_score']}% [{fusion['risk_level']} Risk]")
        print(f"-> Voice Clone Risk: {fusion['voice_risk_score']}% (Is Cloned: {voice['is_cloned']})")
        print(f"-> Script Scam Risk: {fusion['script_risk_score']}%")
        print(f"-> Detected Threat Categories: {transcript['detected_categories']}")
        print(f"-> Top Contributing Features Count: {len(voice['top_contributing_features'])}")
        print(f"-> Anomaly Zones: {len(voice['anomalous_regions'])}")
        print(f"-> Plain-Language Explanation: {fusion['plain_language_explanation']}")
        print(f"-> Suggested Action: {fusion['suggested_action']}")

    # Test reporting endpoint
    print("\n--- Testing 'Report This Call' Endpoint ---")
    rep_res = requests.post("http://127.0.0.1:8000/api/report", json={
        "caller_number": "+91-9876543210",
        "audio_filename": "sample_1_digital_arrest_clone.wav",
        "risk_level": "High",
        "overall_risk_score": 85.5,
        "voice_risk_score": 68.0,
        "script_risk_score": 93.0,
        "transcript_snippet": "This is Inspector Vijay Sharma from Cyber Crime...",
        "notes": "Fake police extortion digital arrest call"
    })
    assert rep_res.status_code == 200, f"Report failed: {rep_res.text}"
    rep_data = rep_res.json()
    print(f"Report Created ID: {rep_data['report_id']} | Msg: {rep_data['message']}")

    # Test list reports endpoint
    list_res = requests.get("http://127.0.0.1:8000/api/reports")
    assert list_res.status_code == 200
    reports = list_res.json()
    print(f"Successfully retrieved {len(reports)} reported incidents from SQLite/JSON store.")

    print("\n ALL API END-TO-END TESTS PASSED!")

if __name__ == "__main__":
    run_api_tests()
