"""Export service for transcripts in multiple formats."""
from typing import List, Dict
import json
import csv
from datetime import datetime


class ExportService:
    """Export translated transcripts to various formats."""
    
    @staticmethod
    def export_txt(segments: List[Dict], translations: Dict[int, Dict[str, str]]) -> str:
        """Export as plain text."""
        lines = []
        for idx, seg in enumerate(segments):
            speaker = seg.get("speaker", "Unknown")
            text = seg.get("text", "")
            trans = translations.get(idx, {})
            for lang, text_trans in trans.items():
                lines.append(f"[{speaker}] ({lang}) {text_trans}")
        return "\n".join(lines)
    
    @staticmethod
    def export_json(segments: List[Dict], translations: Dict[int, Dict[str, str]]) -> str:
        """Export as JSON."""
        data = {
            "exported_at": datetime.now().isoformat(),
            "segments": segments,
            "translations": translations
        }
        return json.dumps(data, indent=2)
    
    @staticmethod
    def export_srt(segments: List[Dict], translations: Dict[int, Dict[str, str]], lang: str = "vi") -> str:
        """Export as SRT subtitle format."""
        lines = []
        for idx, seg in enumerate(segments):
            start_time = seg.get("start", 0)
            end_time = seg.get("end", 0)
            
            def format_time(seconds: float) -> str:
                h = int(seconds // 3600)
                m = int((seconds % 3600) // 60)
                s = int(seconds % 60)
                ms = int((seconds % 1) * 1000)
                return f"{h:02}:{m:02}:{s:02},{ms:03}"
            
            text = translations.get(idx, {}).get(lang, seg.get("text", ""))
            lines.append(f"{idx + 1}")
            lines.append(f"{format_time(start_time)} --> {format_time(end_time)}")
            lines.append(f"[{seg.get('speaker', 'Unknown')}] {text}")
            lines.append("")
        return "\n".join(lines)
    
    @staticmethod
    def export_csv(segments: List[Dict], translations: Dict[int, Dict[str, str]]) -> str:
        """Export as CSV."""
        lines = ["speaker,start_time,end_time,original_text,translations"]
        for idx, seg in enumerate(segments):
            speaker = seg.get("speaker", "Unknown")
            start = seg.get("start", 0)
            end = seg.get("end", 0)
            original = seg.get("text", "")
            trans_str = "; ".join([f"{k}:{v}" for k, v in translations.get(idx, {}).items()])
            lines.append(f'"{speaker}",{start},{end},"{original}","{trans_str}"')
        return "\n".join(lines)