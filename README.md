# Video Captioner

**5-Stage AI Pipeline for Accurate, Multi-Style Video Captions**

Built for [AMD Developer Hackathon: ACT II](https://lablab.ai/ai-hackathons/amd-developer-hackathon-act-ii) | Track 2: Video Captioning

---

## The Problem

Speech-to-text systems make mistakes. When building a captioning pipeline, those errors propagate to the final output.

**Real example from our testing:**

```
Raw Whisper: "Big day for the team behind Olimar..."
                                         ^^^^^^ WRONG
```

Whisper transcribed "Ollama" as "Olimar". A basic pipeline would produce captions saying "Olimar raised $88 million" — completely inaccurate.

---

## Our Solution: 5-Stage Validation Pipeline

```
Video → 2x Whisper → Theme + Cross-Compare → Quality Check → 4 Captions → Emotion Check
         (independent)    (single LLM call)     (verify)       (styles)    (tone verify)
```

**Key Innovation:** Multiple independent transcriptions + theme-aware correction catches errors that single-pass pipelines miss.

---

## Results

| Metric | Value |
|--------|-------|
| Success Rate | **100% (6/6 videos)** |
| Processing Time | **66s average** (24% faster than v1) |
| Error Corrections | Olimar→Ollama, silicon→silicone, swimming pro→Zwilling Pro |
| Emotion Scores | **8-10/10** (style-specific verification) |

### Example: Ollama Funding Video

**What Whisper Heard:**
```
Run 1: "Olimar"    Run 2: "Ulmer"
```
All Whisper runs got it wrong.

**What Our Pipeline Output:**
> "Ollama, the open-source platform enabling users to run open models locally, has secured $88 million in funding..."

**The AI used video context to correct "Olimar" → "Ollama" automatically.**

---

## How It Works

### Stage 1: Dual Whisper Transcription
- Runs Whisper twice with different temperatures
- Captures natural variation in speech recognition
- ~15 seconds total

### Stage 2: Theme Detection + Cross-Comparison
- Single LLM call analyzes both transcripts
- Detects video topic/context
- Resolves disagreements using context clues
- Produces verified master transcript

### Stage 3: Quality Check
- LLM reviews master transcript
- Fixes grammar, wrong words, missing text
- Ensures natural phrasing

### Stage 4: Caption Generation
- Generates 4 distinct styles:
  - **Formal** — professional, factual
  - **Sarcastic** — witty, ironic
  - **Humorous-Tech** — developer jokes
  - **Humorous-NonTech** — relatable humor

### Stage 5: Emotion & Tone Verification
- Style-specific scoring (1-10)
- Auto-regenerates captions scoring below 6
- Ensures each caption matches its requested tone

---

## Quick Start

### Prerequisites
- Python 3.10+
- FFmpeg installed

### Installation

```bash
git clone https://github.com/SilverClover49/video-captioner.git
cd video-captioner
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API key
```

### Run

```bash
python captioner.py your_video.mp4
```

### Docker

```bash
docker build -t video-captioner .
docker run --env-file .env -v $(pwd)/videos:/videos video-captioner /videos/video.mp4
```

---

## Performance

| Metric | Value |
|--------|-------|
| Avg Processing Time | 66.3s per video |
| Whisper Runs | 2 (optimized from 4) |
| LLM Calls | 5 (optimized from 6) |
| Success Rate | 100% |

---

## Technology

| Component | Choice | Why |
|-----------|--------|-----|
| Transcription | Whisper (local) | Free, accurate, runs anywhere |
| LLM | MiMo V2.5 / Gemma 4 31B | Strong correction, creative output |
| Audio | FFmpeg | Industry standard |
| Container | Docker | Portable, reproducible |

---

## API Providers

| Provider | Use Case |
|----------|----------|
| `groq` | Testing (fast) |
| `zen` | Testing (free) |
| `fireworks` | Submission (judges provide key) |

Set `PROVIDER` in `.env` to switch.

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
├── design/               # Background images
└── tests/                # Test scripts and results
```

---

## Why This Wins

1. **100% success rate** — No empty outputs, no failures
2. **Context-aware correction** — Fixes errors using video theme, not hardcoded patterns
3. **Style verification** — Emotion check ensures tone matches request
4. **Optimized speed** — 66s/video with no quality loss
5. **Production ready** — Docker container, handles edge cases

---

## License

MIT

---

Built with ❤️ for AMD Developer Hackathon: ACT II
