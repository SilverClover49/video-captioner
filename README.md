# Video Captioner

**5-Stage AI Pipeline for Accurate, Multi-Style Video Captions**

Built for [AMD Developer Hackathon: ACT II](https://lablab.ai/ai-hackathons/amd-developer-hackathon-act-ii) | Track 2: Video Captioning

---

## The Problem

Speech-to-text systems make mistakes. When building a captioning pipeline, those errors propagate to the final output.

**Real example from our testing:**

```
Raw Whisper Transcript: "Big day for the team behind Olimar..."
                                                    ^^^^^^
                                                    WRONG
```

Whisper transcribed "Ollama" as "Olimar". A basic pipeline would produce captions saying "Olimar raised $88 million" — completely inaccurate.

**Most pipelines fail because they trust raw transcripts blindly.**

---

## Our Solution: 5-Stage Validation Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  Video ──→ FFmpeg ──→ Whisper ──→ [Error Correction] ──→ [3 Draft Captions] │
│                                  │         │              │                  │
│                                  │    Catches:            │                  │
│                                  │    - Wrong names       │                  │
│                                  │    - Wrong numbers     │                  │
│                                  │    - Technical terms   │                  │
│                                  │         │              │                  │
│                                  │         ▼              ▼                  │
│                                  │    [Cross-Check & Fix] ──→ [4 Styles]    │
│                                  │         │              │                  │
│                                  │    Validates:          │                  │
│                                  │    - All drafts agree  │                  │
│                                  │    - Facts are correct │                  │
│                                  │         │              │                  │
│                                  │         ▼              ▼                  │
│                                  │    Master Caption ──→ Formal             │
│                                  │                    Sarcastic            │
│                                  │                    Humorous-Tech        │
│                                  │                    Humorous-NonTech     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key Innovation:** Stage 2 catches transcription errors BEFORE they reach caption generation. Stage 4 cross-checks multiple drafts to catch remaining errors.

---

## Results

| Metric | Value |
|--------|-------|
| Captions Generated | **24/24** (100%) |
| Videos Tested | **6** |
| Error Corrections | **Olimar→Ollama, silicon→silicone, swimming pro→Shun Pro** |
| Processing Time | ~30 seconds per video |

### Example Output

**Input Video:** "The tool that 8.9M developers chose over ChatGPT"

**Raw Transcript:**
> "Big day for the team behind Olimar..."

**Corrected Transcript (Stage 2):**
> "Big day for the team behind Ollama..."

**Generated Captions:**

| Style | Caption |
|-------|---------|
| **Formal** | "Ollama, a platform enabling users to run open-source models on their own machines, has secured $88 million in funding..." |
| **Sarcastic** | "Because what the world really needed was yet another platform to make AI more accessible, Ollama has raised $88 million..." |
| **Humorous-Tech** | "Ollama just git a massive $88 million investment to further debug its dominance in the AI space..." |
| **Humorous-NonTech** | "Imagine having a super smart personal assistant that you can control entirely on your own device..." |

---

## Quick Start

### Prerequisites
- Python 3.10+
- FFmpeg installed

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/video-captioner.git
cd video-captioner

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API key
```

### Run

```bash
# Process a single video
python captioner.py your_video.mp4

# Check output
cat output.json
```

### Docker

```bash
# Build
docker build -t video-captioner .

# Run
docker run --env-file .env -v $(pwd)/videos:/videos video-captioner /videos/video.mp4
```

---

## How It Works

### Stage 1: Transcription
- Extracts audio from video using FFmpeg
- Transcribes using Whisper (local or API)
- Produces raw transcript

### Stage 2: Error Correction
- LLM analyzes transcript for common errors
- Corrects wrong names, numbers, technical terms
- Maintains a database of known error patterns

### Stage 3: Draft Generation
- Generates 3 different draft captions
- Each with a different perspective (factual, narrative, news-style)
- Provides multiple angles for cross-checking

### Stage 4: Cross-Validation
- Compares all 3 drafts against original transcript
- Identifies discrepancies and errors
- Produces corrected master caption

### Stage 5: Style Generation
- Generates 4 final captions from master
- Each with distinct tone: formal, sarcastic, humorous-tech, humorous-nontech
- Optimized for accuracy and tone match

---

## Technology Choices

| Component | Choice | Why |
|-----------|--------|-----|
| Transcription | Whisper (local/API) | Free, accurate, fast |
| LLM | Llama 3.3 70B / MiMo V2.5 | Strong correction, creative output |
| Audio | FFmpeg | Industry standard, reliable |
| Container | Docker | Portable, reproducible |

---

## API Providers

Set `PROVIDER` in `.env`:

| Provider | Use Case | Notes |
|----------|----------|-------|
| `groq` | Testing (fast) | Free tier, Whisper + Llama |
| `zen` | Testing (free) | MiMo V2.5 Free |
| `fireworks` | Submission | Judges provide API key |

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
├── test-videos/          # Test video files
└── tests/                # Test scripts and results
```

---

## Why This Approach Wins

1. **Error Correction** — Catches mistakes before they propagate
2. **Cross-Validation** — Multiple drafts ensure accuracy
3. **Production Ready** — Docker container, handles edge cases
4. **Tested** — 24/24 captions across 6 diverse videos

---

## Future Work

- Batch processing for multiple videos
- Video frame analysis for visual context
- Real-time captioning for live streams
- Multi-language support

---

## License

MIT

---

Built with ❤️ for AMD Developer Hackathon: ACT II
