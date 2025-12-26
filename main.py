# main.py
import os
import io
import uuid
import csv
import random
import numpy as np
import soundfile as sf
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

# Import local modules
import config
import audio_utils
import text_utils
import tts_handler

# --- Lifecycle ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup Dictionary
    text_utils.setup_tokenizer()
    # Pre-load default model
    print(f"🚀 Pre-loading default model ({config.CURRENT_MODEL_VERSION})...")
    tts_handler.get_tts_model(config.CURRENT_MODEL_VERSION)
    yield
    # Cleanup
    tts_handler.clear_cache()
    import gc
    gc.collect()

app = FastAPI(lifespan=lifespan)
app.mount("/files", StaticFiles(directory=config.DATA_DIR), name="files")
templates = Jinja2Templates(directory="templates")

# --- Routes ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/normalize")
async def api_normalize(text: str = Form(...)):
    normalized, tokens = text_utils.normalize_text(text)
    return {"original": text, "normalized": normalized, "tokens": tokens}

@app.post("/api/generate")
async def api_generate(
    text: str = Form(...),
    ref_text: str = Form(...),
    model_version: str = Form("v1"),     
    use_norm: str = Form("true"),
    use_auto_split: str = Form("false"),
    speed: float = Form(1.0),
    step: int = Form(32),               
    cfg: float = Form(2.0),              
    ref_audio: Optional[UploadFile] = File(None)
):
    is_use_norm = use_norm.lower() == 'true'
    is_auto_split = use_auto_split.lower() == 'true' 

    # Prepare input text
    if is_use_norm:
        if not is_auto_split:
            gen_text = text_utils.normalize_text(text)[0]
        else:
            gen_text = text
    else:
        gen_text = text

    print(f"Generating ({model_version}): {gen_text[:50]}... (AutoSplit: {is_auto_split})")

    # Handle Reference Audio
    ref_audio_path = config.DEFAULT_REF_AUDIO_PATH
    temp_audio_path = None
    if ref_audio:
        temp_audio_path = os.path.join(config.DATA_DIR, "temp", f"temp_{ref_audio.filename}")
        with open(temp_audio_path, "wb") as buffer:
            buffer.write(await ref_audio.read())
        ref_audio_path = temp_audio_path

    if not os.path.exists(ref_audio_path):
         return HTTPException(status_code=400, detail="Reference audio file not found.")

    # Get Ref Duration
    try:
        data_ref, sr_ref = sf.read(ref_audio_path)
        ref_duration_sec = len(data_ref) / sr_ref
        print(f"✅ Ref Duration: {ref_duration_sec:.2f}s")
    except Exception as e:
        print(f"⚠️ Could not read ref duration: {e}")
        ref_duration_sec = 5.0

    model = tts_handler.get_tts_model(model_version)
    
    try:
        if model:
            if is_auto_split:
                # =========================================================
                # 🔥 AUTO SPLIT & SHORT TEXT FIX LOGIC 🔥
                # =========================================================
                segments = text_utils.intelligent_split(gen_text)
                audio_clips = []
                print(f"✂️ Split into {len(segments)} segments")

                for i, seg in enumerate(segments):
                    # Normalize segment if needed
                    seg_to_gen = text_utils.normalize_text(seg)[0] if is_use_norm else seg
                    if not seg_to_gen.strip(): continue

                    print(f"  [{i+1}/{len(segments)}] Generating: {seg_to_gen}")
                    
                    # Logic: Short Text
                    is_short = len(seg_to_gen) < 15
                    forced_dur = (ref_duration_sec + 2.0) if is_short else None
                    if is_short: print(f"    ⚡ Short text -> Force Duration: {forced_dur:.2f}s")

                    # Inference
                    wav = model.infer(
                        ref_audio=ref_audio_path,
                        ref_text=ref_text,
                        gen_text=seg_to_gen,
                        step=step, speed=speed,
                        cfg=cfg,
                        fix_duration=forced_dur,
                        max_chars=300 # เพิ่มตาม main.py
                    )
                    
                    if isinstance(wav, tuple): wav = wav[0]
                    if hasattr(wav, 'shape') and len(wav.shape) > 1: wav = wav.flatten()

                    # Retry if silent
                    if np.max(np.abs(wav)) < 0.01:
                         print(f"    ❌ Silent output. Retrying with longer duration...")
                         wav = model.infer(
                            ref_audio=ref_audio_path, ref_text=ref_text, gen_text=seg_to_gen,
                            step=step, speed=speed, cfg=cfg,
                            fix_duration=ref_duration_sec + 6.0
                        )
                         if isinstance(wav, tuple): wav = wav[0]
                         if hasattr(wav, 'shape') and len(wav.shape) > 1: wav = wav.flatten()

                    # Post-Process is_short
                    # if is_short:
                    #     original_len = len(wav)
                    #     wav = audio_utils.trim_silence_numpy(wav, threshold=0.005, padding=0.02)
                    #     print(f"    ✂️ Trimmed: {original_len} -> {len(wav)} samples")

                    # wav = audio_utils.apply_fade(wav, fade_duration=0.05)
                    # audio_clips.append(wav)

                    # Post-Process
                    # 1. ย้ายออกมาข้างนอก เพื่อตัดเงียบทุกกรณี
                    original_len = len(wav)
                    wav = audio_utils.trim_silence_numpy(wav, threshold=0.005, padding=0.02)

                    # 2. (Optional) อาจจะ Print เฉพาะตอนที่ตัดเยอะๆ หรือ Print ตลอดก็ได้
                    if len(wav) < original_len:
                        print(f"    ✂️ Trimmed: {original_len} -> {len(wav)} samples")

                    # 3. ใส่ Fade ตามปกติ
                    wav = audio_utils.apply_fade(wav, fade_duration=0.05)
                    audio_clips.append(wav)


                    # Insert Room Tone
                    if i < len(segments) - 1:
                        pause_dur = random.uniform(0.07, 0.14)
                        room_tone = audio_utils.get_room_tone(ref_audio_path, duration=pause_dur)
                        room_tone = audio_utils.apply_fade(room_tone, fade_duration=0.02)
                        audio_clips.append(room_tone)
                
                if audio_clips:
                    final_wav = np.concatenate(audio_clips)
                else:
                    raise Exception("No audio generated from segments")
            else:
                # --- Standard Logic ---
                final_wav = model.infer(
                    ref_audio=ref_audio_path, ref_text=ref_text, gen_text=gen_text,
                    step=step, speed=speed, cfg=cfg
                )
                if isinstance(final_wav, tuple): final_wav = final_wav[0]
                if hasattr(final_wav, 'shape') and len(final_wav.shape) > 1: final_wav = final_wav.flatten()
                final_wav = audio_utils.apply_fade(final_wav, fade_duration=0.02)

            # Return Streaming Response
            buffer = io.BytesIO()
            sf.write(buffer, final_wav, 24000, format='WAV')
            buffer.seek(0)
            
            if temp_audio_path and os.path.exists(temp_audio_path): os.remove(temp_audio_path)
            return StreamingResponse(buffer, media_type="audio/wav")
        else:
            raise Exception("TTS Model not initialized")

    except Exception as e:
        if temp_audio_path and os.path.exists(temp_audio_path): os.remove(temp_audio_path)
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/save_result")
async def api_save_result(
    text: str = Form(...),
    model_version: str = Form(...),
    speed: float = Form(...),
    step: int = Form(...),
    cfg: float = Form(...),
    gen_time: float = Form(...), 
    audio: UploadFile = File(...)
):
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        utterance_id = uuid.uuid4().hex[:6].upper()
        
        filename = f"{timestamp}_{utterance_id}.wav"
        file_path = os.path.join(config.RESULTS_AUDIO_DIR, filename)

        with open(file_path, "wb") as buffer:
            buffer.write(await audio.read())

        file_exists = os.path.isfile(config.RESULTS_CSV_PATH)
        with open(config.RESULTS_CSV_PATH, mode='a', newline='', encoding='utf-8') as csv_file:
            fieldnames = ['timestamp', 'text', 'model', 'speed', 'step', 'cfg', 'gen_time', 'filename']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow({
                'timestamp': timestamp,
                'text': text,
                'model': model_version,
                'speed': speed,
                'step': step,
                'cfg': cfg,
                'gen_time': f"{gen_time:.2f}",
                'filename': filename
            })

        print(f"✅ Saved result: {filename}")
        return {"status": "success", "filename": filename}
    
    except Exception as e:
        print(f"❌ Error saving result: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=config.HOST, port=config.PORT, reload=config.RELOAD)