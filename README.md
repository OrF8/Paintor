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
### Prerequisites
- Python 3.x (Preferably 3.9)
- `tkinter` library (usually included with Python)
### Installation
1. Clone the repository:
   ````
   git clone https://github.com/OrF8/Paintor.git
   cd Paintor
   ````
2. Create and activate a virtual environment:
   ````bash
   python -m venv venv
   ````
   ````bash
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

# 🗂️ Project Structure
````
Paintor/
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
