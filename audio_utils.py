# audio_utils.py
import numpy as np
import random

# หมายเหตุ: ไม่ต้อง import soundfile แล้ว เพราะเราไม่ได้อ่านไฟล์ Ref มาทำ room tone อีกต่อไป

def get_room_tone(audio_path, duration=0.5, target_sr=24000):
    """
    สร้างเสียงเงียบ (Silence) แทน Room Tone
    (Updated: ปรับให้คืนค่าเป็น 0.0 ทันทีเพื่อความรวดเร็วและสะอาด ตามคำขอ)
    """
    # ไม่ต้องอ่านไฟล์ ไม่ต้องคำนวณ RMS แค่สร้าง array 0 ก็พอ
    # ประสิทธิภาพสูงมาก (O(1) relative to IO)
    # audio_path ถูกรับมาเพื่อให้ signature ตรงกับโค้ดเก่าใน main.py แต่ไม่ได้ถูกใช้
    return np.zeros(int(duration * target_sr))

def apply_fade(audio, fade_duration=0.02, sr=24000):
    """
    ใส่ Fade In/Out
    """
    if len(audio) == 0: return audio
    
    fade_samples = int(fade_duration * sr)
    fade_samples = min(fade_samples, len(audio) // 2) 
    
    if fade_samples <= 0: return audio
    
    fade_in_curve = np.linspace(0, 1, fade_samples)
    audio[:fade_samples] *= fade_in_curve
    
    fade_out_curve = np.linspace(1, 0, fade_samples)
    audio[-fade_samples:] *= fade_out_curve
    
    return audio

def trim_silence_numpy(wav, threshold=0.005, padding=0.02, sr=24000):
    """
    ตัดความเงียบส่วนเกิน (Auto Trim)
    """
    if len(wav) == 0: return wav
    
    is_sound = np.abs(wav) > threshold
    if not np.any(is_sound): return wav
        
    indices = np.where(is_sound)[0]
    start = indices[0]
    end = indices[-1]
    
    pad_samples = int(padding * sr)
    start = max(0, start - pad_samples)
    end = min(len(wav), end + pad_samples)
    
    return wav[start:end]
