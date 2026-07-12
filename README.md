# Video Captioner

**5-Stage AI Pipeline for Accurate, Multi-Style Video Captions**

Built for [AMD Developer Hackathon: ACT II](https://lablab.ai/ai-hackathons/amd-developer-hackathon-act-ii) | Track 2: Video Captioning

---

## The Problem

Speech-to-text systems make mistakes. When building a captioning pipeline, those errors propagate to the final output.

**Real example:** Whisper transcribes "Ollama" as "Olimar" — a basic pipeline would output wrong captions.

---

## Our Solution: 5-Stage Pipeline

```
Video → 2x Whisper → Theme+Compare → Quality Check → 4 Captions → Emotion Check
```

**Key Innovation:** Theme-aware cross-comparison catches errors that single-pass pipelines miss.

---

## Results

| Metric | Value |
|--------|-------|
| Success Rate | **100% (6/6 videos)** |
| Processing Time | **66s average** |
| Caption Quality | **140-154% of master** (full content preservation) |
| Emotion Scores | **8-10/10** (style-specific verification) |

### Example: Ollama Funding Video

**Whisper got it wrong:** "Olimar" (all runs)

**Our pipeline corrected it:** "Ollama" (using theme context)

**Output:** 4 complete captions, each preserving ALL facts and details.

---

## How It Works

### Stage 1: Dual Whisper Transcription
- Runs Whisper twice with different temperatures
- Captures natural variation in speech recognition

### Stage 2: Theme Detection + Cross-Comparison
- Single LLM call analyzes both transcripts
- Detects video topic/context
- Resolves disagreements using THEME context (not just "most accurate")

### Stage 3: Quality Check
- LLM reviews master transcript
- Fixes errors WITHOUT rephrasing correct content
- Preserves exact original wording

### Stage 4: Caption Generation
- Generates 4 styles: Formal, Sarcastic, Humorous-Tech, Humorous-NonTech
- **Preserves ALL information** — same length as input
- No truncation, no summarization

### Stage 5: Emotion & Tone Verification
- Style-specific scoring (1-10)
- Auto-regenerates captions scoring below 8
- Ensures each caption matches its requested tone

---

## Quick Start

```bash
git clone https://github.com/SilverClover49/video-captioner.git
cd video-captioner
pip install -r requirements.txt
cp .env.example .env
# Add your API key
python captioner.py your_video.mp4
```

### Docker

```bash
docker build -t video-captioner .
docker run --env-file .env -v $(pwd)/videos:/videos video-captioner /videos/video.mp4
```

---

## API Providers

| Provider | Use Case |
|----------|----------|
| `fireworks` | **Submission** (auto-detected when FIREWORKS_API_KEY set) |
| `groq` | Testing (fast) |
| `zen` | Testing (free) |

**For judges:** Just set `FIREWORKS_API_KEY` — code auto-detects and uses **Gemma 4 31B**.

---

## Project Structure

```
video-captioner/
├── captioner.py          # Main 5-stage pipeline
├── Dockerfile            # Container for submission
├── entrypoint.sh         # Docker entry point
├── requirements.txt      # Python dependencies
├── presentation.html     # Slide deck
├── README.md             # This file
├── .env.example          # Environment template
└── output/               # Generated outputs
```

---

## Technology

| Component | Choice |
|-----------|--------|
| Transcription | Whisper (local, 2 runs) |
| LLM | Gemma 4 31B (submission) / MiMo V2.5 (testing) |
| Audio | FFmpeg |
| Container | Docker |

---

## Why This Wins

1. **100% success rate** — No empty outputs
2. **Theme-aware correction** — Fixes errors using context, not hardcoded patterns
3. **Full content preservation** — Captions capture ALL information
4. **Style verification** — Emotion check ensures tone matches
5. **Production ready** — Docker container, handles edge cases

---

## License

MIT
