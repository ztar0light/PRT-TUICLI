#!/usr/bin/env python3
import argparse
import subprocess
import sys
import os
import json
from dataclasses import dataclass, asdict, field
from typing import List, Generator, Optional, Dict

# --- UI Color Helpers ---
class Style:
    BOLD = "\033[1m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"

    @staticmethod
    def header(text: str): print(f"\n{Style.BOLD}{Style.CYAN}=== {text} ==={Style.RESET}")
    @staticmethod
    def info(text: str): print(f"{Style.GREEN}[INFO]{Style.RESET} {text}")
    @staticmethod
    def warn(text: str): print(f"{Style.YELLOW}[WARN]{Style.RESET} {text}")

# --- Configuration Management ---
@dataclass
class TranscodeConfig:
    input: str = "."
    output: str = "output"
    profile: str = "lt"
    mbps: int = 150
    mode: str = "VBR"  # Added this to the config
    audio_passthrough: bool = False
    metadata_passthrough: bool = False
    recursive: bool = False
    overwrite: bool = False
    dry_run: bool = False

    def to_json(self, path: str):
        with open(path, "w") as f:
            json.dump(asdict(self), f, indent=4)

    @classmethod
    def from_json(cls, path: str):
        if not os.path.exists(path): return None
        with open(path, "r") as f:
            data = json.load(f)
            return cls(**data)

# --- The Core Engine ---
class ProResTranscoder:
    PRORES_PROFILES: Dict[str, int] = {
        "proxy": 0, "lt": 1, "422": 2, "hq": 3, "4444": 4, "xq": 5
    }
    EXTENSIONS = (".mp4", ".mov", ".mxf", ".mkv")
    DEFAULTS_FILE = "prt_defaults.json"

    def __init__(self):
        self.ensure_dependencies()

    def ensure_dependencies(self):
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"{Style.RED}[ERROR] FFmpeg is not installed or not in PATH.{Style.RESET}")
            sys.exit(1)

    def scan_files(self, config: TranscodeConfig) -> Generator[str, None, None]:
        if config.recursive:
            for root, _, files in os.walk(config.input):
                for f in files:
                    if f.lower().endswith(self.EXTENSIONS):
                        yield os.path.join(root, f)
        else:
            if not os.path.exists(config.input):
                return
            for f in os.listdir(config.input):
                if f.lower().endswith(self.EXTENSIONS):
                    yield os.path.join(config.input, f)

    def build_command(self, input_path: str, output_path: str, config: TranscodeConfig):
        # Indentation fixed here
        cmd = [
            "ffmpeg", "-hide_banner", "-loglevel", "error",
            "-i", input_path,
            "-c:v", "prores_ks",
            "-profile:v", str(self.PRORES_PROFILES[config.profile]),
            "-pix_fmt", "yuv422p10le",
        ]

        if config.mode == "CBR":
            cmd += [
                "-b:v", f"{config.mbps}M",
                "-minrate", f"{config.mbps}M",
                "-maxrate", f"{config.mbps}M",
                "-bufsize", f"{config.mbps // 2}M"
            ]
        else:
            cmd += [
                "-b:v", f"{config.mbps}M",
                "-maxrate", f"{config.mbps * 1.5}M",
                "-bufsize", f"{config.mbps * 2}M"
            ]

        if config.audio_passthrough:
            cmd += ["-c:a", "copy"]
        else:
            cmd += ["-c:a", "pcm_s16le"]

        if config.metadata_passthrough:
            cmd += ["-map_metadata", "0"]
        
        cmd += ["-y" if config.overwrite else "-n"]
        cmd.append(output_path)
        return cmd

    def run(self, config: TranscodeConfig):
        files = list(self.scan_files(config))
        if not files:
            Style.warn(f"No video files found in: {config.input}")
            return

        os.makedirs(config.output, exist_ok=True)
        Style.info(f"Found {len(files)} files. Mode: {config.mode}. Starting batch...")

        for f in files:
            base = os.path.splitext(os.path.basename(f))[0]
            out = os.path.join(config.output, f"{base}_prores.mov")
            
            cmd = self.build_command(f, out, config)

            print(f"\n{Style.BOLD}→ {os.path.basename(f)}{Style.RESET}")
            if config.dry_run:
                print(f"  {Style.YELLOW}[DRY RUN]{Style.RESET} Command: {' '.join(cmd)}")
            else:
                try:
                    subprocess.run(cmd, check=True)
                    print(f"  {Style.GREEN}✓ Done{Style.RESET}")
                except subprocess.CalledProcessError:
                    print(f"  {Style.RED}✗ Failed during FFmpeg execution{Style.RESET}")

# --- Interface Logic ---
def run_tui(engine: ProResTranscoder):
    Style.header("Interactive Mode")
    defaults = TranscodeConfig.from_json(engine.DEFAULTS_FILE) or TranscodeConfig()

    def ask(prompt, default):
        res = input(f"{prompt} [{default}]: ").strip()
        return res if res else str(default)

    cfg = TranscodeConfig(
        input=ask("Input folder", defaults.input),
        output=ask("Output folder", defaults.output),
        profile=ask(f"Profile ({', '.join(engine.PRORES_PROFILES.keys())})", defaults.profile),
        mbps=int(ask("Target Mbps", defaults.mbps)),
        mode=ask("Mode (VBR/CBR)", defaults.mode).upper(),
        audio_passthrough=ask("Audio passthrough? (y/n)", "y" if defaults.audio_passthrough else "n").lower() == "y",
        recursive=ask("Recursive? (y/n)", "y" if defaults.recursive else "n").lower() == "y",
        overwrite=ask("Overwrite? (y/n)", "y" if defaults.overwrite else "n").lower() == "y"
    )

    if input(f"\n{Style.YELLOW}Save these as defaults? (y/n): {Style.RESET}").lower() == "y":
        cfg.to_json(engine.DEFAULTS_FILE)
        Style.info("Defaults updated.")

    engine.run(cfg)

def main():
    engine = ProResTranscoder()
    
    if len(sys.argv) == 1:
        Style.header("ProRes Transcoder")
        print("1. Interactive TUI\n2. Run with Defaults\n3. Help\n4. Exit")
        choice = input("\nSelect [1-4]: ")
        if choice == "1": run_tui(engine)
        elif choice == "2":
            cfg = TranscodeConfig.from_json(engine.DEFAULTS_FILE)
            if cfg: engine.run(cfg)
            else: Style.warn("No defaults found. Run TUI first.")
        elif choice == "3": os.system(f"{sys.executable} {sys.argv[0]} --help")
        return

    parser = argparse.ArgumentParser(description="Professional ProRes Transcoder")
    parser.add_argument("input", help="Input folder")
    parser.add_argument("-o", "--output", default="output")
    parser.add_argument("-p", "--profile", choices=engine.PRORES_PROFILES.keys(), default="lt")
    parser.add_argument("-m", "--mbps", type=int, default=150)
    parser.add_argument("--mode", choices=["VBR", "CBR"], default="VBR")
    parser.add_argument("-ap", "--audio-passthrough", action="store_true")
    parser.add_argument("-mp", "--metadata-passthrough", action="store_true")
    parser.add_argument("-r", "--recursive", action="store_true")
    parser.add_argument("-dr", "--dry-run", action="store_true")
    parser.add_argument("-or", "--overwrite", action="store_true")

    args = parser.parse_args()
    config = TranscodeConfig(**vars(args))
    engine.run(config)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Style.RED}Exiting...{Style.RESET}")
        sys.exit(0)