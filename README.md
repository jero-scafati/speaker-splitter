# Speaker Splitter

A desktop GUI application for speaker diarization using pyannote.audio and CustomTkinter.

## Features

- Modern dark-themed GUI built with CustomTkinter
- Speaker diarization using pyannote/speaker-diarization-3.1
- Real-time progress tracking
- Configurable speaker count parameters
- RTTM output format
- Non-blocking UI with background processing

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```

2. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - macOS/Linux: `source .venv/bin/activate`

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your Hugging Face token:
   ```
   HUGGINGFACE_HUB_TOKEN=your_hf_token_here
   ```

## Usage

Run the application:
```bash
python main.py
```

### Using the GUI:

1. **Select Audio File**: Click "Browse" to choose your audio file (WAV, FLAC, MP3)
2. **Choose Output Directory**: Select where to save the RTTM results
3. **Optional Parameters**:
   - Amount of speakers: Exact number if known
   - min_speakers: Minimum expected speakers
   - max_speakers: Maximum expected speakers
4. **Start Processing**: Click "Start" to begin diarization
5. **Monitor Progress**: Watch the progress bar and status updates
6. **Results**: RTTM file will be saved as `<audio_basename>.rttm`

## Requirements

- Python 3.8+
- Hugging Face account and token
- Audio files in supported formats (WAV recommended, 16kHz mono optimal)

## Output Format

The application generates RTTM (Rich Transcription Time Marked) files containing speaker diarization results with timestamps and speaker labels.
