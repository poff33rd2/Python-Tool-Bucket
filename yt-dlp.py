# yt-dlp.py
import os
import json
import subprocess
import time
from pathlib import Path
from prompt_toolkit import prompt

CONFIG_PATH = Path.home() / ".ytcli_config.json"

def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return None

def save_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f)

def setup_config():
    print("Welcome to yt-dlp CLI setup.")
    output_path = input_prompt("Enter your default output location (e.g., /Users/you/Downloads): ").strip()
    if not os.path.isdir(output_path):
        print("Invalid path. Please create the folder or enter a valid one.")
        raise SystemExit(1)
    config = {"output_dir": output_path}
    save_config(config)
    print(f"Default output directory saved to {CONFIG_PATH}")
    return config

def input_prompt(msg):
    return prompt(msg)

def have_cmd(cmd):
    try:
        subprocess.run([cmd, "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        return True
    except FileNotFoundError:
        return False

def run_yt_dlp(url, output_dir):
    """
    Run yt-dlp and return a list of final .mp4 files.
    We rely on yt-dlp's --print to output the final file paths.
    """
    if not have_cmd("yt-dlp"):
        print("yt-dlp is not installed. Install with: pip install yt-dlp")
        raise SystemExit(1)

    output_template = os.path.join(output_dir, "%(title)s.%(ext)s")
    print("Downloading...")

    # We ask yt-dlp to print the final file paths it writes.
    # Some builds support evented prints like after_move:filepath (final path after recode/merge).
    # We include a fallback --print "%(filepath)s" so we capture something even if after_move isn't supported.
    cmd = [
        "yt-dlp",
        "--recode-video", "mp4",
        "-o", output_template,
        "--print", "after_move:filepath",
        "--print", "filepath",
        url
    ]

    # Capture stdout so we can parse printed paths
    proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.returncode != 0:
        # Show yt-dlp's error to help debugging
        if proc.stderr:
            print(proc.stderr.strip())
        print("yt-dlp exited with a non-zero status. Check the URL or your network and try again.")
        raise SystemExit(proc.returncode)

    # Parse any printed paths that end with .mp4 and actually exist
    created = []
    for line in (proc.stdout or "").splitlines():
        line = line.strip()
        if not line:
            continue
        # Accept only .mp4 that currently exists
        if line.lower().endswith(".mp4"):
            p = Path(line)
            if p.exists():
                created.append(p)

    # As a safety net (e.g., if prints didn't fire), also look for most-recent .mp4 in output_dir
    # within a short window after the command ended.
    if not created:
        end = time.time()
        for p in Path(output_dir).rglob("*.mp4"):
            try:
                # anything modified in the last 3 minutes counts as "just created"
                if end - p.stat().st_mtime <= 180:
                    created.append(p)
            except FileNotFoundError:
                pass

    # De-dup and sort
    uniq = []
    seen = set()
    for p in created:
        s = str(p.resolve())
        if s not in seen:
            seen.add(s)
            uniq.append(p)
    return uniq

def convert_to_mp3(mp4_path: Path, bitrate="192k"):
    if not have_cmd("ffmpeg"):
        print("ffmpeg is not installed. Install with Homebrew: brew install ffmpeg")
        return False
    mp3_path = mp4_path.with_suffix(".mp3")
    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(mp4_path),
        "-vn",
        "-b:a", bitrate,
        str(mp3_path)
    ]
    print(f"Converting to MP3: {mp4_path.name} -> {mp3_path.name}")
    proc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if proc.returncode == 0:
        print(f"✅ MP3 created: {mp3_path}")
        return True
    print(f"⚠️ Failed to convert: {mp4_path.name}")
    return False

def maybe_convert_to_mp3(files):
    if not files:
        return
    print("\nThe following MP4 files were created:")
    for f in files:
        print(f"  • {f.name}")

    ans = input_prompt("\nConvert these to MP3 as well? (y/N): ").strip().lower()
    if ans not in ("y", "yes"):
        return

    for f in files:
        convert_to_mp3(f)

def main():
    config = load_config()
    if not config:
        config = setup_config()

    url = input_prompt("Paste the video or playlist link: ").strip()
    if not url:
        print("No URL provided. Exiting.")
        return

    try:
        new_mp4s = run_yt_dlp(url, config["output_dir"])
    except SystemExit:
        return

    print("\n✅ Download(s) complete.")
    if new_mp4s:
        maybe_convert_to_mp3(new_mp4s)
    else:
        print("No new MP4 files detected in the output directory.")

if __name__ == "__main__":
    main()
