# ProRes Transcode CLI & TUI 

PRT_CLITUI is a Python‑based tool that provides both a **command‑line interface (CLI)** and an **interactive text‑user interface (TUI)** for professional batch‑transcoding into **Apple ProRes**. 

By utilizing the `prores_ks` encoder, this tool gives you granular control over bitrates, encoding modes (CBR/VBR), and metadata, making it ideal for both high-fidelity mastering and lightweight proxy generation.

---

## ✨ **Features**

### 🎛 Pro-Level Control
- **Encoding Modes**: Choose between **VBR** (Variable Bitrate) for maximum quality or **CBR** (Constant Bitrate) for predictable file sizes.
- **ProRes Profiles**: Full support for `proxy`, `lt`, `422`, `hq`, `4444`, and `xq`.
- **Bitrate Targeting**: Specify target Mbps without crashing; the script automatically manages FFmpeg's internal rate-control buffers.

### 🖥 Interface Options
- **CLI Mode**: Fast, flag-based operation for power users and automation.
- **TUI Mode**: A guided, color-coded interactive menu for those who prefer a "wizard" style experience.
- **Defaults System**: Save your preferred settings (Mbps, Profile, Path) to a JSON file to run repetitive tasks with a single click.

### 🛠 Technical Capabilities
- **Audio Passthrough**: Option to copy original audio or transcode to PCM 16-bit.
- **Metadata Passthrough**: Preserve source timecode and tags.
- **Recursive Scanning**: Process entire directory trees while maintaining a clean output structure.
- **Dry-Run Mode**: Preview the exact FFmpeg commands before executing them.

---

## 🚀 **Usage**

### **Interactive Mode (TUI)**
Simply run the script without arguments to open the main menu:
```bash
python PRT_CLITUI.py
```

### **CLI Mode Examples**

**ProRes 422 VBR at 150 Mbps (Standard High Quality)**
```bash
python PRT_CLITUI.py ./source -o ./output -p 422 -m 150 --mode VBR
```

**ProRes LT CBR at 50 Mbps (Strict File Size)**
```bash
python PRT_CLITUI.py ./source -p lt -m 50 --mode CBR --overwrite
```

**Recursive Scan with Audio & Metadata Passthrough**
```bash
python PRT_CLITUI.py ./raw_footage -r -ap -mp
```

---

## 📂 **Encoding Logic**

Unlike standard tools, this script intelligently configures the `prores_ks` rate control:

* **VBR (Variable):** Sets a 1.5x max-rate ceiling and a generous buffer, allowing the encoder to spend bits on high-motion scenes while maintaining your target average.
* **CBR (Constant):** Sets min, max, and target rates to the same value with a constricted buffer to force a consistent data stream.

---

## 📦 **Installation & Requirements**

1.  **FFmpeg**: You must have FFmpeg installed and added to your System PATH.
2.  **Python**: Version 3.8 or higher.
3.  **Setup**:
    ```bash
    git clone https://github.com/yourname/PRT_CLITUI.git
    cd PRT_CLITUI
    python PRT_CLITUI.py
    ```

*Note: This version communicates directly with the FFmpeg binary for maximum stability and no longer requires external Python wrappers.*

---

## ⚙️ **Arguments Reference**

| Flag | Long Flag | Description |
| :--- | :--- | :--- |
| `-o` | `--output` | Output directory (default: "output") |
| `-p` | `--profile` | ProRes profile (proxy, lt, 422, hq, 4444, xq) |
| `-m` | `--mbps` | Target bitrate in Mbps |
| `--mode` | `--mode` | Encoding mode: **VBR** or **CBR** |
| `-ap` | `--audio-passthrough` | Copy audio streams instead of re-encoding |
| `-mp` | `--metadata-passthrough`| Copy source metadata |
| `-r` | `--recursive` | Scan subfolders for video files |
| `-dr` | `--dry-run` | Print commands without executing |
| `-or` | `--overwrite` | Force overwrite of existing files |

---

## 📄 **License**
MIT License. Feel free to use and modify for your post-production pipelines.