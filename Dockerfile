# Dockerfile สำหรับรัน FastAPI Application ที่ใช้ PyTorch และ TTS
# ใช้ Base Image Python 3.10 (Stable สำหรับ PyTorch/TTS ส่วนใหญ่)
FROM python:3.12.10

# ตั้งค่า Environment Variable เพื่อไม่ให้ Python สร้าง .pyc และให้ Output log ทันที
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ตั้งค่า HF_HOME สำหรับ HuggingFace Model Caching
ENV HF_HOME=/app/data/hf_cache

# ตั้งค่า Default สำหรับ Environment Variables
ENV HOST=0.0.0.0
ENV PORT=8000
ENV RELOAD=false
ENV CURRENT_MODEL_VERSION=v2

# ติดตั้ง System Dependencies ที่จำเป็นสำหรับ Audio
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ตั้ง Working Directory
WORKDIR /app

# Copy requirement
COPY requirements.txt .

# 1. ติดตั้ง PyTorch (CUDA 12.4) แยกก่อน
RUN pip install --no-cache-dir torch==2.4.0+cu124 torchaudio==2.4.0+cu124 --index-url https://download.pytorch.org/whl/cu124

# 2. ติดตั้ง library อื่นๆ (รวมถึง uvicorn ที่อยู่ใน requirements.txt)
RUN pip install --no-cache-dir -r requirements.txt

# Copy โค้ดทั้งหมดเข้า Container
COPY . .

# สร้างโฟลเดอร์สำหรับเก็บข้อมูล
RUN mkdir -p data/hf_cache data/temp data/test_results/audio templates

# Expose Port
EXPOSE 8000

# รัน FastAPI Application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

