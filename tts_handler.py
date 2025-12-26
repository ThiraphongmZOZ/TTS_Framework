# tts_handler.py
import numpy as np
import torch

try:
    from f5_tts_th.tts import TTS
except ImportError:
    print("Warning: f5_tts_th not found. Using Mock TTS.")
    class MockTTS:
        def __init__(self, model="v1"):
            self.model = model
            print(f"   [MockTTS] Initialized with model {model}")
        def infer(self, ref_audio, ref_text, gen_text, step=32, cfg=2.0, speed=1.0, fix_duration=None):
            print(f"   [MockTTS] Inferring: '{gen_text}' (Speed={speed}, FixDur={fix_duration})")
            sr = 24000
            duration = fix_duration if fix_duration else max(0.5, len(gen_text) * 0.1 / speed)
            samples = int(duration * sr)
            audio = np.random.uniform(-0.1, 0.1, samples)
            return audio
    TTS = MockTTS

# Model Cache
model_cache = {}

def get_tts_model(version="v1"):
    global model_cache
    if version in model_cache:
        return model_cache[version]
    
    print(f"🔄 Loading Model {version} to memory...")
    if TTS:
        try:
            model = TTS(model=version)
            model_cache[version] = model
            print(f"✅ Model {version} Loaded and Cached")
            return model
        except Exception as e:
            print(f"❌ Error loading model {version}: {e}")
            return None
    return None

def clear_cache():
    global model_cache
    model_cache.clear()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()