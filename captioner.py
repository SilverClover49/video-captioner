import os
import sys
import subprocess
import json
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Auto-detect provider: if FIREWORKS_API_KEY is set, use fireworks
if os.getenv("FIREWORKS_API_KEY"):
    PROVIDER = "fireworks"
elif os.getenv("GROQ_API_KEY"):
    PROVIDER = "groq"
elif os.getenv("ZEN_API_KEY"):
    PROVIDER = "zen"
else:
    PROVIDER = os.getenv("PROVIDER", "fireworks")

PROVIDER_CONFIG = {
    "groq": {
        "api_key": os.getenv("GROQ_API_KEY"),
        "base_url": os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
        "llm_model": os.getenv("GROQ_LLM_MODEL", "llama-3.3-70b-versatile"),
        "stt_model": os.getenv("GROQ_STT_MODEL", "whisper-large-v3"),
    },
    "fireworks": {
        "api_key": os.getenv("FIREWORKS_API_KEY"),
        "base_url": os.getenv("FIREWORKS_BASE_URL", "https://api.fireworks.ai/inference/v1"),
        "llm_model": os.getenv("FIREWORKS_MODEL", "accounts/fireworks/models/gemma-4-31b-it"),
        "stt_model": None,
    },
    "zen": {
        "api_key": os.getenv("ZEN_API_KEY"),
        "base_url": os.getenv("ZEN_BASE_URL", "https://opencode.ai/zen/v1"),
        "llm_model": os.getenv("ZEN_MODEL", "mimo-v2.5-free"),
        "stt_model": None,
    },
}

config = PROVIDER_CONFIG[PROVIDER]
client = OpenAI(api_key=config["api_key"], base_url=config["base_url"])

# ============================================================
# OPTIMIZED CAPTION PROMPTS
# ============================================================

STYLE_PROMPTS = {
    "formal": """Rewrite this master caption as a formal, professional caption.

CRITICAL: Preserve ALL information from the master caption. Do not summarize or omit any facts, numbers, names, or details.
The output MUST be approximately the same length as the input. Include EVERY piece of information from the original.
Rewrite the ENTIRE content in formal tone.

Master caption: {caption}""",

    "sarcastic": """Rewrite this master caption as a sarcastic, witty caption.

CRITICAL: Preserve ALL information from the master caption. Do not summarize or omit any facts, numbers, names, or details.
The output MUST be approximately the same length as the input. Include EVERY piece of information from the original.
Rewrite the ENTIRE content with sarcastic tone.

Master caption: {caption}""",

    "humorous_tech": """Rewrite this master caption as a humorous caption for developers.

CRITICAL: Preserve ALL information from the master caption. Do not summarize or omit any facts, numbers, names, or details.
The output MUST be approximately the same length as the input. Include EVERY piece of information from the original.
Rewrite the ENTIRE content with tech humor.

Master caption: {caption}""",

    "humorous_nontech": """Rewrite this master caption as a funny caption for anyone.

CRITICAL: Preserve ALL information from the master caption. Do not summarize or omit any facts, numbers, names, or details.
The output MUST be approximately the same length as the input. Include EVERY piece of information from the original.
Rewrite the ENTIRE content with everyday humor.

Master caption: {caption}""",
}

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def extract_audio(video_path: str, audio_path: str = "temp_audio.wav"):
    cmd = [
        "ffmpeg", "-i", video_path,
        "-vn", "-acodec", "pcm_s16le",
        "-ar", "16000", "-ac", "1",
        audio_path, "-y"
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    return audio_path

def call_llm(system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=config["llm_model"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1500,
                temperature=temperature,
            )
            content = response.choices[0].message.content
            if content:
                return content.strip()
            time.sleep(1)
        except Exception as e:
            print(f"    Retry {attempt+1}: {e}")
            time.sleep(2)
    return ""

# ============================================================
# STAGE 1: WHISPER TRANSCRIPTION (2 runs for speed)
# ============================================================

def stage1_transcribe(video_path: str) -> list:
    print("\n[STAGE 1] Running 2 Whisper transcriptions...")
    
    import whisper
    transcripts = []
    model = whisper.load_model("base")
    
    # Run 1: temperature 0 (deterministic)
    print("  Run 1/2: temp=0.0...")
    audio_path = extract_audio(video_path, "temp_run1.wav")
    result = model.transcribe(audio_path, temperature=0.0)
    transcripts.append({"run": 1, "text": result["text"]})
    print(f"    {result['text'][:80]}...")
    os.remove(audio_path)
    
    # Run 2: temperature 0.7 (varied)
    print("  Run 2/2: temp=0.7...")
    audio_path = extract_audio(video_path, "temp_run2.wav")
    result = model.transcribe(audio_path, temperature=0.7)
    transcripts.append({"run": 2, "text": result["text"]})
    print(f"    {result['text'][:80]}...")
    os.remove(audio_path)
    
    return transcripts

# ============================================================
# STAGE 2: THEME + CROSS-COMPARISON (combined for speed)
# ============================================================

def stage2_theme_and_compare(transcripts: list) -> tuple:
    print("\n[STAGE 2] Theme detection + cross-comparison...")
    
    # Validate transcripts
    valid = [t for t in transcripts if t['text'] and len(t['text'].strip()) > 20]
    if len(valid) < 2:
        print("  WARNING: Less than 2 valid transcripts")
        fallback = max(transcripts, key=lambda t: len(t['text']))['text']
        return "Unknown theme", fallback
    
    all_text = "\n\n".join([f"=== Transcript {t['run']} ===\n{t['text']}" for t in valid])
    
    # Single LLM call for theme + master transcript
    for attempt in range(3):
        result = call_llm(
            system_prompt="""You have 2 transcripts of the same video. Do TWO things:

1. DETECT THEME: What is this video about? (1 sentence)

2. CREATE MASTER TRANSCRIPT: Combine the 2 transcripts into one clean version.
   - Where they agree, use that text
   - Where they disagree, prefer the version that fits the detected THEME
   - If one transcript has a name/entity error (e.g., "Olimar" vs "Ollama"), correct it based on THEME context
   - Preserve ALL details, numbers, and names from both transcripts

Output format:
THEME: <what the video is about>
MASTER: <combined clean transcript>""",
            user_prompt=all_text,
            temperature=0.1
        )
        
        # Validate output
        if result and "THEME:" in result and "MASTER:" in result:
            parts = result.split("MASTER:")
            theme = parts[0].replace("THEME:", "").strip()
            master = parts[1].strip() if len(parts) > 1 else ""
            
            if master and len(master) > 50 and "empty" not in master.lower():
                print(f"  Theme: {theme[:100]}...")
                print(f"  Master: {master[:100]}...")
                return theme, master
        
        print(f"  Attempt {attempt+1}: Invalid response, retrying...")
    
    # Fallback
    fallback = max(valid, key=lambda t: len(t['text']))['text']
    return "Unknown theme", fallback

# ============================================================
# STAGE 3: QUALITY CHECK
# ============================================================

def stage3_quality_check(master: str, theme: str) -> str:
    print("\n[STAGE 3] Quality checking...")
    
    if not master or len(master) < 20:
        return master
    
    checked = call_llm(
        system_prompt=f"""Fix ONLY clear errors in this transcript.
Video theme: {theme}

Rules:
- Fix grammar errors (subject-verb agreement, tenses)
- Fix wrong words/names (e.g., "Olimar" → "Ollama")
- Fix obvious typos
- DO NOT rephrase or rewrite sentences that are already correct
- DO NOT change the writing style or tone
- Keep the EXACT original wording wherever possible
- Output ONLY the corrected transcript""",
        user_prompt=master,
        temperature=0.1
    )
    
    if checked and len(checked) > 20 and "empty" not in checked.lower():
        print(f"  Checked: {checked[:100]}...")
        return checked
    
    return master

# ============================================================
# STAGE 4: CAPTION GENERATION
# ============================================================

def stage4_generate_captions(master: str) -> dict:
    print("\n[STAGE 4] Generating 4 style captions...")
    
    if not master or len(master) < 20:
        master = "[Video transcript unavailable]"
    
    captions = {}
    for style, prompt_template in STYLE_PROMPTS.items():
        print(f"  {style}...")
        prompt = prompt_template.format(caption=master)
        caption = call_llm(
            system_prompt="Output ONLY the caption. No labels, no explanation.",
            user_prompt=prompt,
            temperature=0.7
        )
        if not caption or len(caption) < 10 or "empty" in caption.lower():
            caption = f"[{style.upper()}] {master[:200]}"
        captions[style] = caption
        print(f"    {caption[:80]}...")
    
    return captions

# ============================================================
# STAGE 5: EMOTION CHECK (style-specific)
# ============================================================

def stage5_emotion_check(captions: dict) -> tuple:
    print("\n[STAGE 5] Emotion & tone verification...")
    
    scores = {}
    
    # Style-specific criteria
    criteria = {
        "formal": "MUST be factual, professional, NO humor, NO slang, suitable for news",
        "sarcastic": "MUST include irony, exaggeration, dry humor, mocking tone",
        "humorous_tech": "MUST reference coding/tech concepts (git, debug, API, etc)",
        "humorous_nontech": "MUST use everyday analogies, NO technical jargon"
    }
    
    for style in captions.keys():
        caption = captions[style]
        crit = criteria.get(style, "match the requested tone")
        
        review = call_llm(
            system_prompt=f"""Rate this caption for TONE MATCH (1-10).
Required tone: {crit}
Output ONLY a number (1-10). Nothing else.""",
            user_prompt=f"Caption: {caption}",
            temperature=0.1
        )
        
        # Parse score
        try:
            score = int(''.join(filter(str.isdigit, review[:3]))) if review else 5
            score = min(10, max(1, score))
        except:
            score = 5
        
        print(f"  {style}: {score}/10")
        scores[style] = score
        
        # If score < 8, regenerate
        if score < 8:
            print(f"    Regenerating {style}...")
            new_caption = call_llm(
                system_prompt=f"""Rewrite this caption to EXACTLY match this tone: {crit}

Rules:
- Keep ALL factual information from the original
- Change ONLY the wording, tone, and style
- Do NOT change the length drastically
- Output ONLY the improved caption""",
                user_prompt=caption,
                temperature=0.8
            )
            if new_caption and len(new_caption) > 10:
                captions[style] = new_caption
                print(f"    Improved: {new_caption[:80]}...")
    
    return captions, scores

# ============================================================
# MAIN PIPELINE
# ============================================================

def process_video(video_path: str) -> dict:
    print(f"\n{'='*60}")
    print(f"Processing: {os.path.basename(video_path)}")
    print(f"Provider: {PROVIDER} | LLM: {config['llm_model']}")
    print(f"{'='*60}")
    
    start = time.time()
    
    # Stage 1: 2x Whisper
    transcripts = stage1_transcribe(video_path)
    
    # Stage 2: Theme + Cross-compare (combined)
    theme, master = stage2_theme_and_compare(transcripts)
    
    # Stage 3: Quality check
    master = stage3_quality_check(master, theme)
    
    # Stage 4: Generate captions
    captions = stage4_generate_captions(master)
    
    # Stage 5: Emotion check
    captions, emotion_scores = stage5_emotion_check(captions)
    
    elapsed = round(time.time() - start, 1)
    print(f"\n  Completed in {elapsed}s")
    
    return {
        "video": os.path.basename(video_path),
        "processing_time": elapsed,
        "theme": theme,
        "transcripts": transcripts,
        "master_caption": master,
        "captions": captions,
        "emotion_scores": emotion_scores
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python captioner.py <video_file>")
        sys.exit(1)
    
    video_file = sys.argv[1]
    if not os.path.exists(video_file):
        print(f"File not found: {video_file}")
        sys.exit(1)
    
    result = process_video(video_file)
    
    # Save output to output/ folder (in current working directory)
    output_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "output.json")
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"DONE - Saved to {output_path}")
    print(f"{'='*60}")
