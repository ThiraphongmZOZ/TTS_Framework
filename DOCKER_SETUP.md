# Docker Deployment & Model Caching Guide

## Docker Setup - What You Need to Know

### ✅ Current Setup

Your Docker configuration is **mostly working**, but there are a few important points to understand:

```
┌─────────────────────────────────────────┐
│       Docker Container Lifecycle         │
└─────────────────────────────────────────┘

First Run:
  1. Docker builds image (install dependencies)
  2. Container starts → FastAPI app loads
  3. app startup → Pre-loads model (CURRENT_MODEL_VERSION)
     ↓
  4. Model downloads from HuggingFace → Cached in /app/data/hf_cache/
  5. Cached models persist in volume (./data:/app/data)
  6. ✅ Ready to generate speech

Next Run:
  1. Container starts
  2. App startup → Loads model FROM CACHE (fast!)
  3. ✅ Ready immediately
```

### 📦 Model Caching Flow

Your setup uses **HuggingFace model caching** with environment variable:

```python
# config.py
HF_HOME = os.getenv("HF_HOME", os.path.join(DATA_DIR, "hf_cache"))
os.environ["HF_HOME"] = HF_HOME
```

This means:
- ✅ Models download to `./data/hf_cache/`
- ✅ `./data` is mapped as Docker volume → **persists between runs**
- ✅ Models stay cached after first run

### 🔧 Issues to Fix

#### 1. **Add `python-dotenv` to requirements.txt**

Your `config.py` now uses `from dotenv import load_dotenv`, so add it:

```bash
pip install python-dotenv
```

Then add to [requirements.txt](requirements.txt):
```
python-dotenv
```

#### 2. **Create `.env` file before Docker**

```bash
# Copy the example
cp .env.example .env

# Or create it manually with:
HOST=0.0.0.0
PORT=8000
RELOAD=false
CURRENT_MODEL_VERSION=v2
DATA_DIR=./data
```

⚠️ **Important**: 
- Set `RELOAD=false` in production/Docker
- The `.env` file should be in the project root (same level as Dockerfile)

#### 3. **Add `.env` to Docker COPY (Optional)**

If you want to use `.env` inside Docker, update [Dockerfile](Dockerfile):

```dockerfile
# Copy .env if it exists
COPY .env* .
```

**OR** use docker-compose environment variables:

```yaml
environment:
  - PYTHONUNBUFFERED=1
  - CURRENT_MODEL_VERSION=v2
  - RELOAD=false
```

#### 4. **Ensure HF_HOME in Dockerfile**

The Dockerfile should set the HF_HOME environment:

```dockerfile
ENV HF_HOME=/app/data/hf_cache
```

### 🚀 Quick Start with Docker

#### Step 1: Prepare files

```bash
# Add python-dotenv to requirements.txt
echo "python-dotenv" >> requirements.txt

# Create .env file
cp .env.example .env
```

#### Step 2: Build & Run

```bash
# Build image
docker build -t f5-tts-thai .

# Run with docker-compose
docker-compose up -d

# Or run directly
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/templates:/app/templates \
  --name thai_f5_tts \
  f5-tts-thai
```

#### Step 3: Monitor first run

```bash
# Check logs (model downloading)
docker logs -f thai_f5_tts_container

# Wait for: "✅ Model v2 Loaded and Cached"
```

Once you see the message, models are cached!

#### Step 4: Next runs are fast

```bash
# Stop container
docker-compose down

# Start again (models already cached!)
docker-compose up -d
```

### 📊 First Run Timeline

```
⏱️  Estimate for First Run:

Environment: CPU only
  - Build image: 5-10 minutes (first time, installs PyTorch)
  - Download models: 10-20 minutes (depends on internet)
  - Total: 15-30 minutes

Environment: GPU (NVIDIA)
  - Build image: 10-15 minutes
  - Download models: 5-10 minutes (faster download)
  - Total: 15-25 minutes
```

### ✅ What Works Automatically

- ✅ Model caching in `./data/hf_cache/`
- ✅ Results saved to `./data/test_results/`
- ✅ Templates updated without rebuild
- ✅ Persistent volumes between Docker restarts
- ✅ GPU support (if nvidia-docker installed)

### ⚠️ Things to Remember

1. **First run downloads models** - Be patient, this can take 10-20 minutes
2. **Models are LARGE** - v2 is ~2GB, v1 is ~2GB
3. **Disk space required** - Minimum 10GB free space
4. **Internet connection** - Required for first model download
5. **GPU optional** - Works on CPU, but slower (20-30s per generation vs 5-10s with GPU)

### 🔍 Troubleshooting Docker

#### Problem: Model keeps re-downloading

**Solution**: Check volume is mounted correctly
```bash
# Verify volume
docker inspect thai_f5_tts_container | grep -A 5 Mounts

# Should show:
# "Source": "/path/to/F5-TTS-Freamwork/data"
# "Destination": "/app/data"
```

#### Problem: Container stops immediately

**Solution**: Check logs
```bash
docker logs thai_f5_tts_container
# Look for error messages about imports or config
```

#### Problem: Out of memory

**Solution**: Increase Docker memory allocation
```yaml
# In docker-compose.yaml
services:
  app:
    deploy:
      resources:
        limits:
          memory: 8G
```

#### Problem: Port already in use

**Solution**: Change port in docker-compose.yaml
```yaml
ports:
  - "9000:8000"  # Access via localhost:9000
```

### 📋 Checklist Before Running Docker

- [ ] `python-dotenv` added to requirements.txt
- [ ] `.env` file created in project root
- [ ] `./data` folder exists
- [ ] `./templates` folder exists with `index.html`
- [ ] At least 10GB free disk space
- [ ] (Optional) NVIDIA Docker installed for GPU support

### 🎯 Summary

**Your Docker setup will work!** Just:
1. Add `python-dotenv` to requirements.txt
2. Create `.env` file from `.env.example`
3. Wait for first model download (10-20 min)
4. Subsequent runs are instant (models cached)

Model caching is **automatic** - models download once and stay in the `./data/hf_cache/` volume.
