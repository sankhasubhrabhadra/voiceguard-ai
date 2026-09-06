import os
import sqlite3
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "reports.db")
JSON_BACKUP_PATH = os.path.join(os.path.dirname(__file__), "reports.json")

class ReportDatabase:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS call_reports (
                        id TEXT PRIMARY KEY,
                        caller_number TEXT,
                        audio_filename TEXT,
                        risk_level TEXT,
                        overall_risk_score REAL,
                        voice_risk_score REAL,
                        script_risk_score REAL,
                        transcript_snippet TEXT,
                        notes TEXT,
                        created_at TEXT
                    )
                """)
                conn.commit()
        except Exception as e:
            print(f"Error initializing SQLite database: {e}")

    def add_report(
        self,
        caller_number: Optional[str],
        audio_filename: str,
        risk_level: str,
        overall_risk_score: float,
        voice_risk_score: float,
        script_risk_score: float,
        transcript_snippet: str = "",
        notes: str = ""
    ) -> str:
        report_id = f"REP-{uuid.uuid4().hex[:8].upper()}"
        now_iso = datetime.utcnow().isoformat() + "Z"
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO call_reports (
                        id, caller_number, audio_filename, risk_level,
                        overall_risk_score, voice_risk_score, script_risk_score,
                        transcript_snippet, notes, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    report_id,
                    caller_number or "+91-XXXXXXXXXX",
                    audio_filename,
                    risk_level,
                    overall_risk_score,
                    voice_risk_score,
                    script_risk_score,
                    transcript_snippet,
                    notes,
                    now_iso
                ))
                conn.commit()
        except Exception as e:
            print(f"SQLite insert failed, writing to json fallback: {e}")
            self._json_fallback_write(report_id, {
                "id": report_id,
                "caller_number": caller_number or "+91-XXXXXXXXXX",
                "audio_filename": audio_filename,
                "risk_level": risk_level,
                "overall_risk_score": overall_risk_score,
                "voice_risk_score": voice_risk_score,
                "script_risk_score": script_risk_score,
                "transcript_snippet": transcript_snippet,
                "notes": notes,
                "created_at": now_iso
            })

        return report_id

    def list_reports(self, limit: int = 50) -> List[Dict[str, Any]]:
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM call_reports
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (limit,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"SQLite read failed, reading from json fallback: {e}")
            return self._json_fallback_read()

    def _json_fallback_write(self, report_id: str, data: Dict[str, Any]):
        reports = self._json_fallback_read()
        reports.insert(0, data)
        try:
            with open(JSON_BACKUP_PATH, "w", encoding="utf-8") as f:
                json.dump(reports, f, indent=2)
        except Exception:
            pass

    def _json_fallback_read(self) -> List[Dict[str, Any]]:
        if os.path.exists(JSON_BACKUP_PATH):
            try:
                with open(JSON_BACKUP_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []
