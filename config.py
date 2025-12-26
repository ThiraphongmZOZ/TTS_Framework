# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Config & Paths ---
BASE_DIR = os.getenv("BASE_DIR", os.getcwd())
DATA_DIR = os.getenv("DATA_DIR", os.path.join(BASE_DIR, "data"))
RESULTS_DIR = os.getenv("RESULTS_DIR", os.path.join(DATA_DIR, "test_results"))

# Cache Directories
HF_HOME = os.getenv("HF_HOME", os.path.join(DATA_DIR, "hf_cache"))
os.environ["HF_HOME"] = HF_HOME

# Input Paths
LEXICON_PATH = os.getenv("LEXICON_PATH", os.path.join(DATA_DIR, "stations_600.json"))
DEFAULT_REF_AUDIO_PATH = os.getenv("DEFAULT_REF_AUDIO_PATH", os.path.join(DATA_DIR, "reference.wav"))

# Output Paths
RESULTS_AUDIO_DIR = os.path.join(RESULTS_DIR, "audio")
RESULTS_CSV_PATH = os.path.join(RESULTS_DIR, "results.csv")

# Create directories if not exist
os.makedirs(RESULTS_AUDIO_DIR, exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "temp"), exist_ok=True)

# App Settings
CURRENT_MODEL_VERSION = os.getenv("CURRENT_MODEL_VERSION", "v2")

# Server Settings
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
RELOAD = os.getenv("RELOAD", "true").lower() == "true"

# TTS Generation Default Parameters
DEFAULT_STEPS = int(os.getenv("DEFAULT_STEPS", 32))
DEFAULT_SPEED = float(os.getenv("DEFAULT_SPEED", 1.0))
DEFAULT_CFG = float(os.getenv("DEFAULT_CFG", 2.0))
USE_NORM_DEFAULT = os.getenv("USE_NORM_DEFAULT", "true").lower() == "true"
USE_AUTO_SPLIT_DEFAULT = os.getenv("USE_AUTO_SPLIT_DEFAULT", "false").lower() == "true"

# Audio Processing
FADE_DURATION = float(os.getenv("FADE_DURATION", 0.02))
SILENCE_THRESHOLD = float(os.getenv("SILENCE_THRESHOLD", 0.005))
SILENCE_PADDING = float(os.getenv("SILENCE_PADDING", 0.02))

# Pause/Room Tone Settings
MIN_PAUSE_DURATION = float(os.getenv("MIN_PAUSE_DURATION", 0.07))
MAX_PAUSE_DURATION = float(os.getenv("MAX_PAUSE_DURATION", 0.14))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")