import flet as ft
import sounddevice as sd
import soundfile as sf
import numpy as np
from datetime import datetime
import whisper
import threading
import ollama
import pyperclip

print("Loading Whisper...")
whisper_model = whisper.load_model("base")
print("✅ Ready!")

def main(page: ft.Page):
    page.title = "Meeting Notes"
    page.window_width = 700
    page.window_height = 800
    
    is_recording = False
    frames = []
    current_transcript = ""
    current_notes = ""
    
    status = ft.Text("Ready", size=18)
    record_btn = ft.ElevatedButton("🎤 Start", width=150, height=50)
    transcript = ft.Text("", selectable=True)
    notes = ft.Text("", selectable=True)
    
    # BUTTONS ARE HERE - ALWAYS VISIBLE
    export_btn = ft.ElevatedButton("💾 EXPORT TXT", disabled=True)
    copy_btn = ft.ElevatedButton("📋 COPY", disabled=True)
    
    def do_export(e):
        filename = f"notes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w') as f:
            f.write(f"TRANSCRIPT:\n{current_transcript}\n\nNOTES:\n{current_notes}")
        status.value = f"✅ Saved {filename}"
        page.update()
    
    def do_copy(e):
        pyperclip.copy(f"{current_transcript}\n\n{current_notes}")
        status.value = "✅ Copied!"
        page.update()
    
    export_btn.on_click = do_export
    copy_btn.on_click = do_copy
    
    def make_notes(text):
        nonlocal current_transcript, current_notes
        status.value = "🤖 AI working..."
        page.update()
        
        response = ollama.chat(model='llama3.2', messages=[{
            'role': 'user',
            'content': f"Create meeting notes from: {text}"
        }])
        
        current_transcript = text
        current_notes = response['message']['content']
        notes.value = current_notes
        
        # ENABLE BUTTONS
        export_btn.disabled = False
        copy_btn.disabled = False
        
        status.value = "✅ Done!"
        page.update()
    
    def process_audio(filename):
        status.value = "🎯 Transcribing..."
        page.update()
        
        audio_data, sr = sf.read(filename)
        audio_data = audio_data.astype(np.float32).flatten()
        
        if sr != 16000:
            from scipy import signal
            audio_data = signal.resample(audio_data, int(len(audio_data) * 16000 / sr))
        
        result = whisper_model.transcribe(audio_data, fp16=False, language="english")
        transcript.value = result["text"]
        page.update()
        
        make_notes(result["text"])
    
    def toggle_record(e):
        nonlocal is_recording, frames
        
        if not is_recording:
            is_recording = True
            frames = []
            status.value = "🔴 Recording..."
            record_btn.text = "⏹️ STOP"
            record_btn.bgcolor = ft.Colors.RED
            transcript.value = ""
            notes.value = ""
            export_btn.disabled = True
            copy_btn.disabled = True
            page.update()
            
            def callback(indata, f, t, s):
                if is_recording:
                    frames.append(indata.copy())
            
            global stream
            stream = sd.InputStream(samplerate=16000, channels=1, callback=callback)
            stream.start()
        else:
            is_recording = False
            stream.stop()
            stream.close()
            
            status.value = "💾 Saving..."
            page.update()
            
            recording = np.concatenate(frames, axis=0)
            filename = f"meeting_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            sf.write(filename, recording, 16000)
            
            record_btn.text = "🎤 START"
            record_btn.bgcolor = None
            page.update()
            
            threading.Thread(target=process_audio, args=(filename,), daemon=True).start()
    
    record_btn.on_click = toggle_record
    
    # ADD EVERYTHING TO PAGE
    page.add(
        ft.Column([
            ft.Text("🎙️ Meeting Notes App", size=30, weight="bold"),
            ft.Divider(),
            status,
            ft.Container(height=10),
            record_btn,
            ft.Container(height=20),
            ft.Text("Transcript:", size=16, weight="bold"),
            ft.Container(transcript, bgcolor="#f0f0f0", padding=10, height=120),
            ft.Container(height=10),
            ft.Text("Notes:", size=16, weight="bold"),
            ft.Container(notes, bgcolor="#e3f2fd", padding=10, height=150),
            ft.Container(height=15),
            ft.Row([export_btn, copy_btn], spacing=10),  # BUTTONS HERE
        ], scroll="auto")
    )

ft.app(target=main)