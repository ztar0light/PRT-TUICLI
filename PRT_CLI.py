#!/usr/bin/env python3
import argparse
import subprocess
import sys
import os
import json

DEFAULTS_FILE = "prt_defaults.json"

# -----------------------------
# Dependency auto-installer
# -----------------------------
def ensure_dependencies():
    try:
        import ffmpeg
    except ImportError:
        print("[INFO] ffmpeg-python not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "ffmpeg-python"])
        print("[INFO] Installed ffmpeg-python successfully.")

ensure_dependencies()
import ffmpeg


# -----------------------------
# ProRes profiles lookup
# -----------------------------
PRORES_PROFILES = {
    "proxy": 0,
    "lt": 1,
    "422": 2,
    "hq": 3,
    "4444": 4,
    "xq": 5
}

PROFILE_LIST = list(PRORES_PROFILES.keys())


# -----------------------------
# Load/save defaults
# -----------------------------
def load_defaults():
    if os.path.exists(DEFAULTS_FILE):
        with open(DEFAULTS_FILE, "r") as f:
            return json.load(f)
    return None

def save_defaults(settings):
    with open(DEFAULTS_FILE, "w") as f:
        json.dump(settings, f, indent=4)
    print("[INFO] Defaults saved.")


# -----------------------------
# Build FFmpeg command
# -----------------------------
def build_ffmpeg_cmd(input_file, output_file, profile, mbps, passthrough_audio, passthrough_metadata, overwrite):
    bits_per_mb = int((mbps * 1_000_000) / (16 * 16 * 30))  # rough scaling

    cmd = [
        "ffmpeg",
        "-i", input_file,
        "-c:v", "prores_ks",
        "-profile:v", str(PRORES_PROFILES[profile]),
        "-bits_per_mb", str(bits_per_mb),
        "-pix_fmt", "yuv422p10le",
    ]

    if passthrough_audio:
        cmd += ["-c:a", "copy"]
    else:
        cmd += ["-c:a", "pcm_s16le"]

    if passthrough_metadata:
        cmd += ["-map_metadata", "0"]

    cmd += ["-y" if overwrite else "-n"]
    cmd.append(output_file)

    return cmd


# -----------------------------
# File scanning
# -----------------------------
def scan_files(path, recursive):
    exts = (".mp4", ".mov", ".mxf")
    if recursive:
        for root, _, files in os.walk(path):
            for f in files:
                if f.lower().endswith(exts):
                    yield os.path.join(root, f)
    else:
        for f in os.listdir(path):
            if f.lower().endswith(exts):
                yield os.path.join(path, f)


# -----------------------------
# Main transcoding logic
# -----------------------------
def process_files(args):
    files = list(scan_files(args.input, args.recursive))

    if not files:
        print("No video files found.")
        return

    os.makedirs(args.output, exist_ok=True)

    for f in files:
        base = os.path.splitext(os.path.basename(f))[0]
        out = os.path.join(args.output, f"{base}_prores.mov")

        cmd = build_ffmpeg_cmd(
            f, out, args.profile, args.mbps,
            args.audio_passthrough,
            args.metadata_passthrough,
            args.overwrite
        )

        print("\n----------------------------------------")
        print("Processing:", f)
        print("Output:", out)
        print("Command:", " ".join(cmd))

        if not args.dry_run:
            subprocess.run(cmd)


# -----------------------------
# NEW: TUI MODE
# -----------------------------
def run_tui():
    print("\n=== ProRes Transcoder TUI Mode ===\n")

    defaults = load_defaults()

    def ask(prompt, default=None):
        if default is not None:
            prompt = f"{prompt} [{default}]: "
        else:
            prompt = f"{prompt}: "
        ans = input(prompt).strip()
        return ans if ans else default

    input_folder = ask("Input folder", defaults.get("input") if defaults else ".")
    output_folder = ask("Output folder", defaults.get("output") if defaults else "output")

    print("\nSelect ProRes profile:")
    for i, p in enumerate(PROFILE_LIST):
        print(f"{i+1}. {p}")

    profile_idx = int(ask("Choose 1-6", "2")) - 1
    profile = PROFILE_LIST[profile_idx]

    mbps = int(ask("Target Mbps", defaults.get("mbps") if defaults else "150"))

    audio_pass = ask("Audio passthrough? (y/n)", "n").lower() == "y"
    meta_pass = ask("Metadata passthrough? (y/n)", "n").lower() == "y"
    recursive = ask("Process subfolders? (y/n)", "n").lower() == "y"
    overwrite = ask("Overwrite existing files? (y/n)", "n").lower() == "y"
    dry_run = ask("Dry run only? (y/n)", "n").lower() == "y"

    print("\n=== Summary ===")
    print(f"Input: {input_folder}")
    print(f"Output: {output_folder}")
    print(f"Profile: {profile}")
    print(f"Mbps: {mbps}")
    print(f"Audio passthrough: {audio_pass}")
    print(f"Metadata passthrough: {meta_pass}")
    print(f"Recursive: {recursive}")
    print(f"Overwrite: {overwrite}")
    print(f"Dry run: {dry_run}")

    if input("Run now? (y/n): ").lower() != "y":
        print("Cancelled.")
        return

    if input("Save these settings as default? (y/n): ").lower() == "y":
        save_defaults({
            "input": input_folder,
            "output": output_folder,
            "profile": profile,
            "mbps": mbps
        })

    args = argparse.Namespace(
        input=input_folder,
        output=output_folder,
        profile=profile,
        mbps=mbps,
        audio_passthrough=audio_pass,
        metadata_passthrough=meta_pass,
        recursive=recursive,
        overwrite=overwrite,
        dry_run=dry_run,
        verbose=False
    )

    process_files(args)


# -----------------------------
# NEW: No-argument behavior
# -----------------------------
def no_argument_menu():
    print("\n=== ProRes Transcoder ===")
    print("No arguments provided.")
    print("Choose an option:")
    print("1. View help menu")
    print("2. Enter TUI mode")
    print("3. Run with default settings")
    print("4. Quit")

    choice = input("Select 1-4: ").strip()

    if choice == "1":
        os.system(f"{sys.executable} {sys.argv[0]} --help")
    elif choice == "2":
        run_tui()
    elif choice == "3":
        defaults = load_defaults()
        if not defaults:
            print("No defaults saved. Entering TUI mode instead.")
            run_tui()
            return

        args = argparse.Namespace(
            input=defaults["input"],
            output=defaults["output"],
            profile=defaults["profile"],
            mbps=defaults["mbps"],
            audio_passthrough=False,
            metadata_passthrough=False,
            recursive=False,
            overwrite=False,
            dry_run=False,
            verbose=False
        )
        process_files(args)
    else:
        print("Goodbye.")


# -----------------------------
# CLI Argument Parser
# -----------------------------
def main():
    if len(sys.argv) == 1:
        return no_argument_menu()

    parser = argparse.ArgumentParser(
        description="ProRes Transcoding CLI with bitrate control, passthrough options, and recursive scanning."
    )

    parser.add_argument("input", help="Input folder containing video files.")
    parser.add_argument("-o", "--output", default="output", help="Output folder.")
    parser.add_argument("-p", "--profile", choices=PRORES_PROFILES.keys(), default="lt",
                        help="ProRes profile (proxy, lt, 422, hq, 4444, xq).")
    parser.add_argument("-m", "--mbps", type=int, default=150,
                        help="Target Mbps for video bitrate.")
    parser.add_argument("-ap", "--audio-passthrough", action="store_true",
                        help="Copy audio instead of re-encoding.")
    parser.add_argument("-mp", "--metadata-passthrough", action="store_true",
                        help="Copy metadata from source.")
    parser.add_argument("-r", "--recursive", action="store_true",
                        help="Process subfolders recursively.")
    parser.add_argument("-dr", "--dry-run", action="store_true",
                        help="Show commands without running them.")
    parser.add_argument("-or", "--overwrite", action="store_true",
                        help="Overwrite existing files.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose output.")

    args = parser.parse_args()
    process_files(args)


if __name__ == "__main__":
    main()
