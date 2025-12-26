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

### Running the Server

```bash
python main.py
```

The application will start at `http://localhost:8000`

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

1. **GPU Acceleration**: Ensure CUDA is properly configured for faster inference
2. **Model Preloading**: The default model is preloaded on startup
3. **Batch Processing**: Use auto-split feature for longer texts
4. **Reference Audio**: Use high-quality reference audio (24kHz mono recommended)

## Troubleshooting

### Model Download Issues
If models fail to download, check your HuggingFace token and internet connection.

### Audio Quality Issues
- Ensure reference audio is clear and at 24kHz sample rate
- Adjust CFG scale (lower = faster but lower quality, higher = slower but better quality)
- Increase step count for better quality (more inference steps = slower)

### Memory Issues
- Reduce batch size or use shorter text segments
- Enable auto-split to process longer texts in chunks
- Use GPU acceleration if available

## Supported Models

- `v1`: F5-TTS-TH-V2 (Older version)
- `v2`: F5-TTS-THAI (Latest recommended)

## License

[Add your license here]

## Contributing

[Add contribution guidelines]

## Support

For issues and support, please create an issue in the repository.
