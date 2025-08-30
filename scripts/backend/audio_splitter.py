from pathlib import Path
from typing import List, Dict

try:
    from pydub import AudioSegment
except ImportError:
    raise SystemExit(
        "pydub no está instalado. Ejecuta: pip install pydub\n"
        "y asegúrate de tener ffmpeg/libav instalado en tu sistema."
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
    print("Cargando archivo de audio...")
    try:
        audio = AudioSegment.from_file(str(audio_path))
    except Exception as e:
        raise RuntimeError(f"No se pudo cargar el archivo de audio con pydub: {e}\n"
                         "Asegúrate de que FFmpeg o Libav estén instalados y en el PATH del sistema.")

    print("Parseando archivo RTTM...")
    segments = parse_rttm(rttm_file)
    if not segments:
        raise ValueError("No se encontraron segmentos de hablante válidos en el archivo RTTM.")

    # Agrupar segmentos por hablante
    by_speaker: Dict[str, List[Dict]] = {}
    for s in segments:
        by_speaker.setdefault(s["speaker"], []).append(s)

    outdir.mkdir(parents=True, exist_ok=True)
    total_saved = 0
    print(f"Encontrados {len(by_speaker)} hablantes. Procesando segmentos...")

    for speaker, segs in by_speaker.items():
        speaker_dir = outdir / speaker
        speaker_dir.mkdir(exist_ok=True)
        
        # Ordenar segmentos por tiempo de inicio
        segs = sorted(segs, key=lambda x: x["start"])
        
        for i, s in enumerate(segs, 1):
            if s["duration"] < min_duration:
                continue
            
            start_ms = int(s["start"] * 1000)
            end_ms = int(s["end"] * 1000)
            
            # Extraer el segmento de audio
            chunk = audio[start_ms:end_ms]
            
            # Crear un nombre de archivo descriptivo
            out_name = f"{speaker}_{i:04d}_{s['start']:.2f}s.wav"
            out_path = speaker_dir / out_name
            
            chunk.export(str(out_path), format=fmt)
            total_saved += 1

    print(f"Proceso completado. Se guardaron {total_saved} segmentos en '{outdir.resolve()}'.")
    return total_saved