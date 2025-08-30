import torch
from pyannote.audio import Pipeline
from typing import Optional

def get_pipeline(token: str):
    if not token:
        raise ValueError("Hugging Face token not found. Please provide a valid token.")
    
    print("Initializing pipeline...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token=token
    )
    pipeline.to(device)
    print("Pipeline initialized.")
    return pipeline

def run_diarization(audio_path: str,
                    output_dir: str,
                    num_speakers: Optional[int] = None,
                    min_speakers: Optional[int] = None,
                    max_speakers: Optional[int] = None,
                    hf_token: Optional[str] = None): 
    
    try:
        pipeline = get_pipeline(token=hf_token)
    except Exception as e:
        raise RuntimeError(f"Failed to initialize pipeline: {e}")

    pipeline_kwargs = {}
    if num_speakers and num_speakers.isdigit():
        pipeline_kwargs["num_speakers"] = int(num_speakers)
    if min_speakers and min_speakers.isdigit():
        pipeline_kwargs["min_speakers"] = int(min_speakers)
    if max_speakers and max_speakers.isdigit():
        pipeline_kwargs["max_speakers"] = int(max_speakers)
    
    print(f"Running diarization with options: {pipeline_kwargs}")

    diarization = pipeline(audio_path, **pipeline_kwargs)

    rttm_file = diarization.to_rttm()

    return rttm_file