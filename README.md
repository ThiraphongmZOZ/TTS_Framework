# F5-TTS Framework - Thai Edition

A FastAPI-based Text-to-Speech (TTS) application using F5-TTS models with Thai language support.

## Features

- 🎤 Multiple F5-TTS model versions support (v1, v2)
- 🇹🇭 Thai text processing and normalization
- 🔊 Intelligent text segmentation for optimal audio generation
- 📝 Reference audio-based voice cloning
- ⚡ Configurable generation parameters (speed, CFG scale, inference steps)
- 💾 Result tracking with CSV logging
- 🌐 Web UI for easy interaction
- 🐳 Docker support for easy deployment

## Prerequisites

- Python 3.8 - 3.12
- CUDA-capable GPU (recommended for faster inference)
- 4GB+ RAM
- HuggingFace API access (for model downloads)

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd F5-TTS-Freamwork
```

### 2. Create virtual environment

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup environment variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your configuration
# See .env.example for all available options
```

## Configuration

Create a `.env` file in the project root with the following variables:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
RELOAD=true

# Model Configuration
CURRENT_MODEL_VERSION=v2

# Paths
BASE_DIR=.
DATA_DIR=./data
LEXICON_PATH=./data/stations_600.json
DEFAULT_REF_AUDIO_PATH=./data/reference.wav
RESULTS_DIR=./data/test_results
```

See [.env.example](.env.example) for more details.

## Usage

### Running the Server Locally

```bash
# Activate virtual environment first
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# Run the application
python main.py
```

The application will start at `http://localhost:8000`

### Web UI Guide

1. **Open Browser**: Navigate to `http://localhost:8000`
2. **Interface Elements**:
   - **Text Input**: Enter Thai text you want to convert
   - **Reference Text**: Enter text that matches your reference audio
   - **Model Version**: Select between v1 (older) or v2 (latest)
   - **Normalization**: Automatic Thai text cleanup (recommended: ON)
   - **Auto-split**: Break long text into segments (useful for texts > 100 chars)
   - **Speed**: 0.5 (slower) to 2.0 (faster), default 1.0
   - **Inference Steps**: 32 (default, fast) to 50+ (better quality but slower)
   - **CFG Scale**: 2.0 (default, natural) to 4.0 (more stable, less natural)
   - **Reference Audio**: Upload your voice sample (24kHz WAV recommended)
3. **Generate**: Click Generate to synthesize speech
4. **Save Result**: After generation, save to results database

### API Endpoints

#### 1. **GET /** - Web UI
Access the web interface at the root URL.

#### 2. **POST /api/normalize** - Normalize Thai Text
Normalizes Thai text and returns tokens.

```bash
curl -X POST "http://localhost:8000/api/normalize" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text=สวัสดีครับ"
```

#### 3. **POST /api/generate** - Generate Speech
Generates audio from text using reference audio.

**Parameters:**
- `text` (string): Text to convert to speech
- `ref_text` (string): Reference text (should match reference audio)
- `model_version` (string): Model version to use (default: v1)
- `use_norm` (string): Enable text normalization (default: true)
- `use_auto_split` (string): Enable intelligent text splitting (default: false)
- `speed` (float): Speech speed multiplier (default: 1.0)
- `step` (int): Inference steps (default: 32)
- `cfg` (float): Classifier-free guidance scale (default: 2.0)
- `ref_audio` (file): Reference audio file (optional)

**Example:**
```bash
curl -X POST "http://localhost:8000/api/generate" \
  -F "text=สวัสดีครับ" \
  -F "ref_text=สวัสดีครับ" \
  -F "model_version=v2" \
  -F "use_norm=true" \
  -F "use_auto_split=false" \
  -F "speed=1.0" \
  -F "step=32" \
  -F "cfg=2.0" \
  --output output.wav
```

#### 4. **POST /api/save_result** - Save Generation Result
Saves the generated audio and parameters to the results database.

```bash
curl -X POST "http://localhost:8000/api/save_result" \
  -F "text=สวัสดีครับ" \
  -F "model_version=v2" \
  -F "speed=1.0" \
  -F "step=32" \
  -F "cfg=2.0" \
  -F "gen_time=5.23" \
  -F "audio=@output.wav"
```

### Advanced Configuration

#### Understanding Parameters

**Text Normalization (`use_norm`)**
- `true`: Cleans Thai text, converts numbers to Thai text, removes extra spaces
- `false`: Uses raw input text
- Recommendation: Keep enabled for most cases

**Auto-split (`use_auto_split`)**
- `false`: Generate entire text at once (faster, but quality drops for long texts)
- `true`: Split text into segments, generate each segment, then concatenate
- Best for: Texts longer than 100 characters
- Example: "สวัสดีครับ วันนี้เป็นวันที่ดี" → generates each sentence separately

**Speed**
- `0.5`: Half speed (slower, deeper voice)
- `1.0`: Normal speed (default)
- `2.0`: Double speed (faster, higher pitch)
- Works by adjusting phoneme durations

**Inference Steps**
- `16`: Fast (5-10 seconds), lower quality
- `32`: Default balance (10-15 seconds), good quality
- `50+`: Slow (20-30 seconds), best quality
- More steps = more refinement iterations

**CFG Scale (Classifier-Free Guidance)**
- `1.0-1.5`: Very natural but may be unstable
- `2.0-3.0`: Default (natural + stable)
- `4.0+`: More controlled but sounds robotic
- Lower = more creative but less stable
- Higher = more predictable but less natural

#### Model Switching

To use a different model version, update `.env`:

```env
# For older model (slower but sometimes more accurate for certain accents)
CURRENT_MODEL_VERSION=v1

# For newer model (faster and recommended)
CURRENT_MODEL_VERSION=v2
```

Or pass at runtime via API:
```bash
curl -X POST "http://localhost:8000/api/generate" \
  -F "text=สวัสดีครับ" \
  -F "ref_text=สวัสดีครับ" \
  -F "model_version=v1" \
  # ... other parameters
```

#### Reference Audio Best Practices

1. **Format**: 24kHz mono WAV (required)
2. **Duration**: 3-10 seconds (longer is better for training the voice)
3. **Quality**: Clear, without background noise
4. **Content**: The reference text should match what's being spoken in audio
5. **Positioning**: Place reference file at `data/reference.wav` or upload via API
6. **Example**:
   ```bash
   # Convert to required format (using ffmpeg)
   ffmpeg -i your_audio.mp3 -acodec pcm_s16le -ar 24000 -ac 1 data/reference.wav
   ```

#### Results Storage

Generated audio and metadata are stored in `data/test_results/`:
- **Audio files**: `data/test_results/audio/*.wav`
- **Log file**: `data/test_results/results.csv` with columns:
  - `timestamp`: Generation time
  - `text`: Input text
  - `model`: Model version used
  - `speed`, `step`, `cfg`: Parameters
  - `gen_time`: Generation duration (seconds)
  - `filename`: Output audio filename

## Project Structure

```
F5-TTS-Freamwork/
├── main.py                 # FastAPI application & routes
├── config.py              # Configuration and paths
├── tts_handler.py         # TTS model management
├── text_utils.py          # Thai text processing & normalization
├── audio_utils.py         # Audio processing utilities
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── README.md              # This file
├── docker-compose.yaml    # Docker compose configuration
├── Dockerfile             # Docker image definition
├── templates/             # HTML templates
│   └── index.html        # Web UI
└── data/                  # Data directory
    ├── hf_cache/         # HuggingFace model cache
    ├── reference.wav     # Default reference audio
    ├── stations_600.json # Thai lexicon
    ├── temp/             # Temporary files
    └── test_results/     # Results output
        ├── audio/        # Generated audio files
        └── results.csv   # Results log
```

## Docker Usage

### Building the Docker image

```bash
docker build -t f5-tts-thai .
```

### Running with Docker

```bash
docker-compose up -d
```

The application will be available at `http://localhost:8000`

### Docker Environment Variables

You can override environment variables when running Docker:

```bash
docker run -e PORT=9000 -e CURRENT_MODEL_VERSION=v2 -p 9000:9000 f5-tts-thai
```

## Performance Tips

### Optimization Strategies

1. **GPU Acceleration**
   - Ensure NVIDIA GPU drivers installed: `nvidia-smi`
   - CUDA 12.4+ recommended (Dockerfile uses CUDA 12.4)
   - 8GB+ VRAM recommended
   - Expected speedup: 3-5x faster than CPU

2. **Model Caching**
   - Models auto-cache on first run (~2GB each)
   - Cached in `data/hf_cache/`
   - Subsequent runs load from cache (very fast)
   - Docker volumes preserve cache between restarts

3. **Batch Processing**
   - Use auto-split for long texts (100+ characters)
   - Reduces memory usage and improves quality
   - Adds slight overhead for concatenation

4. **Reference Audio Quality**
   - Use high-quality reference audio (24kHz mono)
   - Clear speech without background noise
   - Longer recordings (5-10s) = better voice cloning

5. **Parameter Tuning**
   - For speed: `step=16, cfg=1.5` (trade quality for speed)
   - For quality: `step=50+, cfg=3.0` (slower but best results)
   - For balance: `step=32, cfg=2.0` (default, recommended)

### Expected Performance

| Scenario | CPU | GPU |
|----------|-----|-----|
| First run (download models) | ~20 min | ~15 min |
| Typical generation (10 words) | 20-30s | 5-10s |
| Long text with auto-split | 30-60s | 10-20s |
| Model loading (from cache) | <1s | <1s |

## Troubleshooting

### Common Issues

#### 1. **Model Download Fails**
```
Error: Unable to download model from HuggingFace
```
**Solutions:**
- Check internet connection: `ping huggingface.co`
- Verify HuggingFace token (if using private models)
- Check disk space: At least 10GB free required
- Try again (rate limiting may apply)

#### 2. **"CUDA out of memory" Error**
```
RuntimeError: CUDA out of memory
```
**Solutions:**
- Reduce inference steps: `step=16` instead of 32
- Use shorter texts or enable auto-split
- Reduce reference audio length
- Free GPU memory: `nvidia-smi` to check, close other apps
- Use CPU-only mode (slower but works on any machine)

#### 3. **Audio Quality Issues**
**Problem**: Generated audio sounds robotic/unnatural
**Solutions:**
- Lower CFG scale: `cfg=1.5` to `2.0` (too high = robotic)
- Increase inference steps: `step=50` (more refinement)
- Check reference audio quality (clear speech, no noise)
- Ensure reference text matches audio content

**Problem**: Poor voice cloning / voice doesn't match reference
**Solutions:**
- Use longer reference audio (5-10s minimum)
- Ensure reference audio is 24kHz mono format
- Reference text should match what's in the audio
- Try different model version (v1 vs v2)

#### 4. **"Reference audio file not found"**
**Solution:**
- Set `DEFAULT_REF_AUDIO_PATH` in `.env` to valid file
- Or upload reference audio via API
- Verify file exists at `data/reference.wav`

#### 5. **Docker Container Won't Start**
```
Exit code: 1
```
**Solutions:**
```bash
# Check logs for error details
docker logs thai_f5_tts_container

# Common fixes:
# 1. Rebuild image
docker-compose build --no-cache

# 2. Remove old container
docker-compose down -v

# 3. Check .env file exists
ls -la .env

# 4. Verify volume mount
docker inspect thai_f5_tts_container
```

#### 6. **"ModuleNotFoundError: No module named 'f5_tts_th'"**
**Solution:**
```bash
# Install missing package
pip install f5-tts-th

# Or reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

#### 7. **Text Normalization Issues**
**Problem**: Thai text not converting correctly
**Solutions:**
- Check text is valid UTF-8 encoded
- Some abbreviations may not normalize (workaround: spell out)
- Disable normalization if causing issues: `use_norm=false`

### Debug Mode

Enable detailed logging by updating `.env`:
```env
LOG_LEVEL=DEBUG
```

Then check logs:
```bash
# Local
tail -f *.log

# Docker
docker logs -f thai_f5_tts_container
```

## Supported Models

- `v1`: F5-TTS-TH-V2 (Older version)
- `v2`: F5-TTS-THAI (Latest recommended)

## Frequently Asked Questions (FAQ)

### General

**Q: How long does it take to generate speech?**
A: Typically 5-15 seconds on GPU, 20-30 seconds on CPU, depending on text length and inference steps.

**Q: Can I use English text?**
A: The models are primarily trained for Thai. English may work but quality is not guaranteed. For best results, use Thai text.

**Q: Do I need a GPU?**
A: No, but it's highly recommended. CPU inference is ~5x slower.

**Q: How much disk space do I need?**
A: At least 10GB free. Models (~4GB) + cache + generated audio.

**Q: Can I switch models without restarting?**
A: Yes, via API parameter `model_version=v1` or `model_version=v2`. Models are cached separately.

### Audio & Voice

**Q: How do I change the voice/speaker?**
A: Upload a different reference audio file with the voice you want to clone.

**Q: What's the best quality setting?**
A: `step=50, cfg=2.5, speed=1.0` gives best quality but takes 25-30 seconds.

**Q: Can I adjust the accent or speaking style?**
A: Limited control. Voice characteristics depend on the reference audio. Try different reference samples.

**Q: Does auto-split affect quality?**
A: Slightly. Segments are concatenated, which may cause small artifacts. But it handles long texts better.

### Docker & Deployment

**Q: Do I need to run `pip install` before Docker?**
A: No. `docker-compose up --build` installs everything inside the container.

**Q: How do I use the app on another machine?**
A: Push to git (excluding `.env` and `data/hf_cache`), then clone and run `docker-compose up --build`.

**Q: Can I use Docker on Windows/Mac?**
A: Yes. GPU support requires additional setup (Docker Desktop + NVIDIA Container Runtime).

**Q: How do I backup generated audio?**
A: Copy `data/test_results/audio/` folder. Results are also logged in `data/test_results/results.csv`.

### Troubleshooting

**Q: Why does the app use so much RAM?**
A: Models are loaded into RAM for fast inference. Models are ~2GB each. Use GPU if possible.

**Q: Can I run multiple instances?**
A: Yes, but ensure different ports. Update `PORT` in `.env`.

**Q: How do I delete cached models to free space?**
A: Run:
```bash
rm -rf data/hf_cache/hub/models--*
```
Models will re-download on next use.

## Development & Contributing

### Setting Up for Development

```bash
# Clone and setup
git clone <repository-url>
cd F5-TTS-Freamwork
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Create .env from example
cp .env.example .env

# Run in development mode
python main.py
```

### Project Structure Details

```
main.py              - FastAPI app, routes, request handlers
config.py            - Environment variables, paths, settings (uses .env)
tts_handler.py       - Model loading/caching, inference wrapper
text_utils.py        - Thai text normalization, tokenization, splitting
audio_utils.py       - Audio processing (fade, trim silence, room tone)
templates/index.html - Web UI (HTML+JavaScript frontend)
```

### Key Functions

**text_utils.py**
- `normalize_text()`: Clean Thai text, convert numbers
- `intelligent_split()`: Split text into segments for auto-split mode

**tts_handler.py**
- `get_tts_model()`: Load or return cached model
- `model.infer()`: Generate audio from text

**audio_utils.py**
- `apply_fade()`: Add fade-in/fade-out
- `trim_silence_numpy()`: Remove silence at start/end
- `get_room_tone()`: Extract background tone from reference audio

## License

[Add your license here]

## Contributing

[Add contribution guidelines]

## Support

For issues, questions, or feature requests:
1. Check the [FAQ](#frequently-asked-questions-faq) section above
2. Review [DOCKER_SETUP.md](DOCKER_SETUP.md) for Docker-specific issues
3. Check application logs: `docker logs thai_f5_tts_container`
4. Create an issue in the repository with error details and environment info
