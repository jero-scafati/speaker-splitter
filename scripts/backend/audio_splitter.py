from pathlib import Path
from typing import List, Dict

try:
    from pydub import AudioSegment
except ImportError:
    raise SystemExit(
        "pydub not installed. Try: pip install pydub\n"
        "make sure to have ffmpeg/libav installed."
    )

def parse_rttm(rttm_file: str) -> List[Dict]:
    segments = []
    for line in rttm_file.splitlines():
        line = line.strip()
        if not line or not line.startswith("SPEAKER"):
            continue
            
        parts = line.split()
        if len(parts) < 8:
            continue
            
        try:
            start = float(parts[3])
            duration = float(parts[4])
            speaker = parts[7]
        except (ValueError, IndexError):
            continue
                
        segments.append({
            "start": start,
            "duration": duration,
            "end": start + duration,
            "speaker": speaker
        })
    return segments


def split_audio_by_speaker(audio_path: Path, rttm_file: str, outdir: Path,
                           fmt: str = "wav", min_duration: float = 0.1):
    audio = AudioSegment.from_file(str(audio_path))

    segments = parse_rttm(rttm_file)
    if not segments:
        raise ValueError("Didn't found valid RTTM segments.")

    # Group segments by speaker
    by_speaker: Dict[str, List[Dict]] = {}
    for s in segments:
        by_speaker.setdefault(s["speaker"], []).append(s)

    outdir.mkdir(parents=True, exist_ok=True)
    total_saved = 0

    for speaker, segs in by_speaker.items():
        speaker_dir = outdir / speaker
        speaker_dir.mkdir(exist_ok=True)
        
        # Order segments by start time
        segs = sorted(segs, key=lambda x: x["start"])
        
        for i, s in enumerate(segs, 1):
            if s["duration"] < min_duration:
                continue
            
            start_ms = int(s["start"] * 1000)
            end_ms = int(s["end"] * 1000)
            
            # Extract audio chunk
            chunk = audio[start_ms:end_ms]
            
            # Create output filename
            out_name = f"{speaker}_{i:04d}_{s['start']:.2f}s.wav"
            out_path = speaker_dir / out_name
            
            chunk.export(str(out_path), format=fmt)
            total_saved += 1

    return total_saved