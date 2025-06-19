# 🎨 Paintor
Paintor is a lightweight, vector-based painting application developed in Python using Tkinter. It was created as the final project for the course [**67101-1 Introduction to Computer Science**](https://shnaton.huji.ac.il/index.php/NewSyl/67101/2/2024/)
at The Hebrew University of Jerusalem ([**HUJI**](https://en.huji.ac.il/)).

> 🎓 Final Grade: **91**

## 🧰 Features
- Intuitive GUI built with Tkinter
- Vector-based drawing capabilities
- Modular code structure utilizing classes and lambdas
- File I/O support for saving and loading artwork
- Customizable canvas settings

## 🚀 Getting Started
### 💻 Running Locally
#### Prerequisites
- Python 3.x (Preferably 3.9)
- `tkinter` library (usually included with Python)
#### Installation
1. Clone the repository:
   ````
   git clone https://github.com/OrF8/Paintor.git
   cd Paintor
   ````
2. (Optional but recommended): Create and activate a virtual environment:
   ````bash
   python -m venv venv
   source venv/bin/activate     # On Windows: venv\Scripts\activate
   ````
3. Install dependencies:
   ````bash
   pip install -r requirements.txt
   ````
4. Run the application:
   ````bash
   python main.py
   ````

### 🛠️ Running via Dev Container or GitHub Codespace
If you want to skip local setup and run Paintor in a completely containerized environment (no installations needed), you can use:
- GitHub Codespaces: click Code → Open with Codespaces on GitHub and start a new Codespace.
- VS Code Remote – Containers: simply open the repo in VS Code and choose Reopen in Container when prompted.

This uses the included `.devcontainer/` configuration:
- Base image: Python 3.9
- Auto-setup: installs dependencies via requirements.txt
- Ready to run: after opening, run:
  ````bash
  python main.py
  ````
  or use the integrated debugger/terminal, all set up automatically.
> ⏳ Note: The initial Codespace setup may take a few minutes (typically about 5), especially the first time. Subsequent loads will be faster.
> ⚠️ If you get a “no display” error, ensure you’re running the script inside the virtual desktop environment (via port 6080 in your browser).

# 🗂️ Project Structure
````
Paintor/
├── .devcontainer/          # Dev‑container configuration for reproducible dev setup
├── bigvars.py             # Global variables and configurations
├── canvas.py              # Canvas rendering and drawing logic
├── file_manager.py        # File I/O operations for saving/loading
├── main.py                # Entry point of the application
├── test_is_parsed_right.py# Unit tests for file parsing
├── final_project.zip      # Archived version of the project
├── requirements.txt       # Python dependencies
├── LICENSE                # MIT License
└── README.md              # Project documentation
````

# 📄 License
This project is licensed under the MIT License – see the [**LICENSE**](https://github.com/OrF8/Paintor/blob/main/LICENSE) file for details.
