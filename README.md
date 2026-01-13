\# 🎙️ Meeting Notes Pro



AI-powered meeting recorder with automatic transcription and intelligent note generation. All processing happens locally - 100% private!



!\[Meeting Notes Pro](screenshot.png)



\## ✨ Features



\- 🎤 \*\*High-quality audio recording\*\*

\- 🤖 \*\*AI-powered transcription\*\* (Whisper)

\- 📋 \*\*Intelligent meeting notes\*\* (Ollama AI)

\- 💾 \*\*Local database\*\* for meeting history

\- 🔍 \*\*Search past meetings\*\*

\- 📤 \*\*Export to TXT\*\* or copy to clipboard

\- 🔒 \*\*100% privacy\*\* - no cloud, all local processing

\- 🎨 \*\*Beautiful dark theme UI\*\*



\## 🚀 Quick Start



\### Prerequisites



1\. \*\*Python 3.10 or 3.11\*\* (not 3.12+)

2\. \*\*Ollama\*\* - \[Download here](https://ollama.com)



\### Installation



1\. \*\*Clone the repository\*\*

```bash

&nbsp;  git clone https://github.com/YOUR\_USERNAME/meeting-notes-pro.git

&nbsp;  cd meeting-notes-pro

```



2\. \*\*Create virtual environment\*\*

```bash

&nbsp;  python -m venv venv

&nbsp;  venv\\Scripts\\activate  # Windows

&nbsp;  # source venv/bin/activate  # Mac/Linux

```



3\. \*\*Install dependencies\*\*

```bash

&nbsp;  pip install -r requirements.txt

```



4\. \*\*Install Ollama model\*\*

```bash

&nbsp;  ollama pull llama3.2

```



5\. \*\*Run the app\*\*

```bash

&nbsp;  python app.py

```



\## 📦 Requirements



All dependencies are in `requirements.txt`:

\- flet - UI framework

\- openai-whisper - Speech recognition

\- ollama - AI note generation

\- sounddevice - Audio recording

\- soundfile - Audio file handling

\- pyperclip - Clipboard operations

\- numpy, scipy - Audio processing



\## 🎯 How to Use



1\. \*\*Record Tab\*\*

&nbsp;  - Enter meeting title

&nbsp;  - Click the big REC button to start

&nbsp;  - Speak your meeting content

&nbsp;  - Click STOP when done

&nbsp;  - Wait for AI to transcribe and generate notes

&nbsp;  - Export or save to database



2\. \*\*History Tab\*\*

&nbsp;  - View all past meetings

&nbsp;  - Search by keyword

&nbsp;  - Click any meeting to view details

&nbsp;  - Copy or delete meetings



\## 🏗️ Project Structure

```

meeting-notes-pro/

├── app.py              # Main application

├── database.py         # SQLite database handler

├── requirements.txt    # Python dependencies

├── README.md          # This file

└── .gitignore         # Git ignore rules

```



\## 🔧 Building Executable



To create a standalone .exe file:

```bash

pip install pyinstaller

pyinstaller --onefile --windowed --name "MeetingNotesPro" app.py

```



The app will be in `dist/MeetingNotesPro.exe`



\## 🛠️ Tech Stack



\- \*\*UI:\*\* Flet (Flutter-based Python framework)

\- \*\*Speech-to-Text:\*\* OpenAI Whisper

\- \*\*AI Notes:\*\* Ollama (Llama 3.2)

\- \*\*Database:\*\* SQLite

\- \*\*Audio:\*\* sounddevice + soundfile



\## 🔐 Privacy



All processing happens on your local machine:

\- ✅ Audio never leaves your device

\- ✅ No cloud services

\- ✅ No API keys needed

\- ✅ Your data stays yours



\## 📝 License



MIT License - feel free to use and modify!



\## 🤝 Contributing



Contributions welcome! Feel free to:

\- Report bugs

\- Suggest features

\- Submit pull requests



\## 👨‍💻 Author



Created by \[Your Name]



\## 🙏 Acknowledgments



\- OpenAI Whisper for speech recognition

\- Anthropic Claude for development assistance

\- Ollama for local AI

\- Flet team for the amazing framework



---



\*\*Star ⭐ this repo if you find it useful!\*\*

