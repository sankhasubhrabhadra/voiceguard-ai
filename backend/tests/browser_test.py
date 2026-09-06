import os
import sys
import time
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\Lenovo\.gemini\antigravity\brain\756cc06c-2c8b-435d-9ffb-b0bca8440cd3"
os.makedirs(ARTIFACT_DIR, exist_ok=True)

def test_voiceguard_in_browser():
    print("Launching Chromium browser to test VoiceGuard AI...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 960})
        page = context.new_page()

        # Step 1: Navigate to Dashboard
        print("Navigating to http://localhost:5173 ...")
        page.goto("http://localhost:5173", wait_until="networkidle", timeout=15000)
        time.sleep(1)

        # Step 2: Take initial dashboard screenshot
        initial_shot = os.path.join(ARTIFACT_DIR, "screenshot_1_dashboard_initial.png")
        page.screenshot(path=initial_shot, full_page=True)
        print(f"Captured initial dashboard screenshot: {initial_shot}")

        # Step 3: Select Digital Arrest Preset and Click Analyze
        print("Selecting Digital Arrest Scam preset...")
        page.locator("span:has-text('Digital Arrest Scam')").first.click()
        time.sleep(0.5)

        print("Clicking 'Run VoiceGuard Analysis' button...")
        page.locator("button:has-text('Run VoiceGuard Analysis')").click()

        # Step 4: Wait for results panel to render
        print("Waiting for risk verdict and forensics results...")
        page.wait_for_selector("text=Analysis Verdict", timeout=20000)
        time.sleep(1)

        # Step 5: Expand the Explainability Breakdown
        print("Expanding Vocoder Forensics & Acoustic Contributions section...")
        page.locator("text=Deep Vocoder Forensics & Acoustic Biomarkers").click()
        time.sleep(1)

        # Step 6: Take analysis results screenshot
        results_shot = os.path.join(ARTIFACT_DIR, "screenshot_2_analysis_results.png")
        page.screenshot(path=results_shot, full_page=True)
        print(f"Captured full analysis results screenshot: {results_shot}")

        # Step 7: Test the Report Call flow
        print("Testing 'Report Call' flow...")
        page.locator("button:has-text('Report Call')").first.click()
        time.sleep(0.5)

        page.fill("input[placeholder*='+91-']", "+91-9876543210")
        page.fill("textarea[placeholder*='E.g. Caller claimed']", "Suspect claimed to be Mumbai Police regarding a seized FedEx parcel.")
        time.sleep(0.5)

        report_modal_shot = os.path.join(ARTIFACT_DIR, "screenshot_3_report_modal.png")
        page.screenshot(path=report_modal_shot)
        print(f"Captured report modal screenshot: {report_modal_shot}")

        page.locator("button:has-text('Confirm & Report')").click()
        time.sleep(1)

        page.wait_for_selector("text=Incident Logged Successfully", timeout=10000)
        report_success_shot = os.path.join(ARTIFACT_DIR, "screenshot_4_report_success.png")
        page.screenshot(path=report_success_shot)
        print(f"Captured report success screenshot: {report_success_shot}")

        page.locator("button:has-text('Done')").click()
        time.sleep(0.5)

        browser.close()
        print("Browser automated verification completed successfully!")

if __name__ == "__main__":
    test_voiceguard_in_browser()
