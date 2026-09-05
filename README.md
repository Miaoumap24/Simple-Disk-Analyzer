# Simple Disk Analyzer

Simple Disk Analyzer is a lightweight, multithreaded storage visualization tool built in Python. It scans drives or specific directories to inspect disk space distribution across folders and file extensions.

## Requirements

- **Python**: 3.8 or higher.
- **Tkinter**: Included by default in official Python builds for Windows and macOS.

> **Linux users**: If Tkinter is missing from your Python distribution, install it via your system package manager:
> ```bash
> sudo apt install python3-tk    # Ubuntu/Debian
> sudo dnf install python3-tkinter # Fedora
> ```

## Installation & Usage

1. Clone or download this repository.
2. Open a terminal in the project directory.
3. Run the application:

```bash
python SimpleDiskAnalyzer.py

```

## How It Works

1. **Path Selection**: Enter a folder path directly into the input bar or use the **Browse** button.
2. **Analysis Phase**: Click **Scan**. The engine uses `os.scandir` for fast directory walking without loading heavy OS metadata wrappers.
3. **Results**:
* **Directory Structure tab**: Expand folders to inspect subdirectories ranked by storage consumption.
* **Extension Stats tab**: View which file formats occupy the most space on the target partition.



## License

Distributed under the AGPL-3.0 License. See `LICENSE` for details.
