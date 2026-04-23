### *ProResTranscode CLI & TUI — A Flexible ProRes Batch Transcoder*

PRT_CLITUI is a Python‑based tool that provides both a **command‑line interface (CLI)** and an **interactive text‑user interface (TUI)** for batch‑transcoding video files into **Apple ProRes**.  
It supports custom bitrates, multiple ProRes profiles, audio/metadata passthrough, recursive folder scanning, and a persistent defaults system.

Whether you prefer typing flags or answering simple prompts, PRT_CLITUI adapts to your workflow.

---

## ✨ **Features**

### 🎛 CLI Mode
- Choose any ProRes profile:
  - `proxy`, `lt`, `422`, `hq`, `4444`, `xq`
- Set custom target Mbps
- Audio passthrough (`--audio-passthrough`)
- Metadata passthrough (`--metadata-passthrough`)
- Recursive folder processing (`--recursive`)
- Dry‑run mode (`--dry-run`)
- Overwrite control (`--overwrite`)
- Automatic output folder creation
- Auto‑installs `ffmpeg-python` if missing

### 🖥 TUI Mode (Interactive)
When launched with **no arguments**, the app asks what you want to do:
1. View help menu  
2. Enter TUI mode  
3. Run with saved defaults  
4. Quit  

TUI mode walks you through:
- Input/output folders  
- ProRes profile selection (1–6)  
- Target Mbps  
- Audio passthrough (y/n)  
- Metadata passthrough (y/n)  
- Recursive scanning (y/n)  
- Overwrite behavior (y/n)  
- Dry‑run mode (y/n)  

Then it shows a summary and asks:
- **Run now?**  
- **Save these settings as default?**

Defaults are stored in a JSON file and can be reused automatically.

---

## 📦 **Installation**

Clone the repository:

```
git clone https://github.com/yourname/PRT_CLITUI.git
cd PRT_CLITUI
```

Run the script:

```
python PRT_CLITUI.py
```

The script will automatically install `ffmpeg-python` if needed.

You must have **FFmpeg** installed and available in your system PATH.

---

## 🚀 **Usage**

### ▶ Run with no arguments (recommended)
```
python PRT_CLITUI.py
```

You will be prompted to:
- View help  
- Enter TUI mode  
- Run defaults  
- Quit  

---

### ▶ CLI Mode Examples

#### ProRes LT at 150 Mbps
```
python PRT_CLITUI.py ./videos --profile lt --mbps 150
```

#### Process subfolders
```
python PRT_CLITUI.py ./videos --recursive
```

#### ProRes HQ at 220 Mbps with audio passthrough
```
python PRT_CLITUI.py ./videos --profile hq --mbps 220 --audio-passthrough
```

#### Dry run (show commands only)
```
python PRT_CLITUI.py ./videos --dry-run
```

#### Overwrite existing files
```
python PRT_CLITUI.py ./videos --overwrite
```

---

## 📁 **Output**

Transcoded files are written to the output folder (default: `./output`).  
If the folder does not exist, it is created automatically.

---

## 🧠 **Bitrate Logic**

The script converts Mbps → FFmpeg’s `bits_per_mb` using a scaling formula.  
This allows approximate ProRes bitrate targeting while keeping full control.

---

## 🛠 **Requirements**

- Python 3.8+
- FFmpeg installed and accessible in PATH
- `ffmpeg-python` (auto‑installed)

---

## 🤝 **Contributing**

Pull requests are welcome.  
If you have ideas for new features (parallel encoding, watch‑folder mode, GUI, presets, etc.), open an issue.

---

## 📄 **License**

MIT License.

---
