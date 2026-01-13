import flet as ft
import sounddevice as sd
import soundfile as sf
import numpy as np
from datetime import datetime
import whisper
import threading
import ollama
import pyperclip
from database import MeetingDatabase
import time

print("🚀 Starting Meeting Notes App...")
print("⏳ Loading AI models (this takes ~10 seconds)...")

whisper_model = whisper.load_model("base")
db = MeetingDatabase()

print("✅ Ready! Opening app...")

def main(page: ft.Page):
    page.title = "Notely!!!"
    page.window_width = 1200
    page.window_height = 900
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.bgcolor = "#000000"
    page.fonts = {
        "DotMatrix": "https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&display=swap",
    }
    
    # ============== STATE ==============
    is_recording = False
    frames = []
    current_transcript = ""
    current_notes = ""
    start_time = None
    recording_duration = 0
    
    # ============== RECORDING TAB ==============
    
    title_input = ft.TextField(
        label="MEETING.TITLE",
        label_style=ft.TextStyle(
            font_family="DotMatrix",
            size=11,
            weight=ft.FontWeight.BOLD,
            color="#FFFFFF"
        ),
        hint_text="Q4.PLANNING.SESSION",
        hint_style=ft.TextStyle(color="#333333", font_family="DotMatrix"),
        width=600,
        border_color="#FFFFFF",
        focused_border_color="#FF0000",
        border_width=2,
        bgcolor="#000000",
        color="#FFFFFF",
        text_style=ft.TextStyle(font_family="DotMatrix", size=14),
        cursor_color="#FF0000",
    )
    
    status_text = ft.Text(
        "SYSTEM.READY",
        size=14,
        weight=ft.FontWeight.BOLD,
        color="#FFFFFF",
        font_family="DotMatrix",
        text_align=ft.TextAlign.CENTER
    )
    
    duration_text = ft.Text(
        "00:00:00",
        size=48,
        weight=ft.FontWeight.W_900,
        color="#FFFFFF",
        font_family="DotMatrix",
        text_align=ft.TextAlign.CENTER
    )
    
    record_indicator = ft.Container(
        width=16,
        height=16,
        bgcolor="#FF0000",
        border_radius=8,
        visible=False,
        animate_opacity=1000,
    )
    
    record_btn = ft.Container(
        content=ft.Stack([
            ft.Container(
                width=200,
                height=200,
                border=ft.border.all(4, "#FFFFFF"),
                border_radius=0,
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("REC", size=32, weight=ft.FontWeight.W_900, color="#FFFFFF", font_family="DotMatrix"),
                    ft.Container(height=8),
                    ft.Container(width=60, height=3, bgcolor="#FFFFFF"),
                    ft.Container(height=8),
                    ft.Text("START", size=16, weight=ft.FontWeight.BOLD, color="#FFFFFF", font_family="DotMatrix"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                width=200,
                height=200,
                alignment=ft.alignment.center,
            ),
        ]),
        width=200,
        height=200,
    )
    
    transcript_box = ft.Container(
        content=ft.Column([
            ft.Text(
                "AWAITING.INPUT",
                size=12,
                color="#666666",
                font_family="DotMatrix",
                weight=ft.FontWeight.BOLD
            ),
        ]),
        bgcolor="#0A0A0A",
        border=ft.border.all(2, "#FFFFFF"),
        padding=20,
        height=200,
    )
    
    notes_box = ft.Container(
        content=ft.Column([
            ft.Text(
                "AI.STANDBY",
                size=12,
                color="#666666",
                font_family="DotMatrix",
                weight=ft.FontWeight.BOLD
            ),
        ]),
        bgcolor="#0A0A0A",
        border=ft.border.all(2, "#FFFFFF"),
        padding=20,
        height=250,
    )
    
    export_btn = ft.Container(
        content=ft.Text("EXPORT", size=14, weight=ft.FontWeight.BOLD, color="#666666", font_family="DotMatrix"),
        bgcolor="#0A0A0A",
        border=ft.border.all(2, "#333333"),
        padding=15,
        width=180,
        height=60,
        alignment=ft.alignment.center,
    )
    
    copy_btn = ft.Container(
        content=ft.Text("COPY", size=14, weight=ft.FontWeight.BOLD, color="#666666", font_family="DotMatrix"),
        bgcolor="#0A0A0A",
        border=ft.border.all(2, "#333333"),
        padding=15,
        width=180,
        height=60,
        alignment=ft.alignment.center,
    )
    
    save_db_btn = ft.Container(
        content=ft.Text("SAVE.DB", size=14, weight=ft.FontWeight.BOLD, color="#666666", font_family="DotMatrix"),
        bgcolor="#0A0A0A",
        border=ft.border.all(2, "#333333"),
        padding=15,
        width=180,
        height=60,
        alignment=ft.alignment.center,
    )
    
    progress_bar = ft.Container(
        content=ft.Row([
            ft.Container(width=0, height=4, bgcolor="#FF0000", animate_opacity=300),
        ]),
        width=600,
        height=4,
        bgcolor="#1A1A1A",
        visible=False,
    )
    
    progress_text = ft.Text("", size=12, color="#FF0000", font_family="DotMatrix", weight=ft.FontWeight.BOLD)
    
    # Timer update
    def update_timer():
        while is_recording:
            elapsed = int(time.time() - start_time)
            hours = elapsed // 3600
            mins = (elapsed % 3600) // 60
            secs = elapsed % 60
            duration_text.value = f"{hours:02d}:{mins:02d}:{secs:02d}"
            page.update()
            time.sleep(1)
    
    def enable_button(btn, text):
        btn.content = ft.Text(text, size=14, weight=ft.FontWeight.BOLD, color="#FFFFFF", font_family="DotMatrix")
        btn.border = ft.border.all(2, "#FFFFFF")
        btn.bgcolor = "#000000"
    
    def disable_button(btn, text):
        btn.content = ft.Text(text, size=14, weight=ft.FontWeight.BOLD, color="#666666", font_family="DotMatrix")
        btn.border = ft.border.all(2, "#333333")
        btn.bgcolor = "#0A0A0A"
    
    def do_export(e):
        if export_btn.border.color == "#333333":
            return
            
        filename = f"notes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            title = title_input.value or "UNTITLED.MEETING"
            f.write(f"MEETING: {title}\n")
            f.write(f"DATE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"\n{'='*60}\nTRANSCRIPT:\n{'='*60}\n{current_transcript}\n\n{'='*60}\nNOTES:\n{'='*60}\n{current_notes}")
        
        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"EXPORT.SUCCESS > {filename}", font_family="DotMatrix", size=12, weight=ft.FontWeight.BOLD),
            bgcolor="#FF0000"
        )
        page.snack_bar.open = True
        page.update()
    
    def do_copy(e):
        if copy_btn.border.color == "#333333":
            return
            
        pyperclip.copy(f"TRANSCRIPT:\n{current_transcript}\n\nNOTES:\n{current_notes}")
        page.snack_bar = ft.SnackBar(
            content=ft.Text("CLIPBOARD.UPDATED", font_family="DotMatrix", size=12, weight=ft.FontWeight.BOLD),
            bgcolor="#FF0000"
        )
        page.snack_bar.open = True
        page.update()
    
    def do_save_db(e):
        if save_db_btn.border.color == "#333333":
            return
            
        title = title_input.value or "UNTITLED.MEETING"
        
        meeting_id = db.save_meeting(
            title=title,
            audio_file="",
            transcript=current_transcript,
            notes=current_notes,
            duration=recording_duration
        )
        
        page.snack_bar = ft.SnackBar(
            content=ft.Text("DATABASE.SAVED > CHECK.HISTORY", font_family="DotMatrix", size=12, weight=ft.FontWeight.BOLD),
            bgcolor="#FF0000"
        )
        page.snack_bar.open = True
        disable_button(save_db_btn, "SAVE.DB")
        page.update()
        
        refresh_history()
    
    export_btn.on_click = do_export
    copy_btn.on_click = do_copy
    save_db_btn.on_click = do_save_db
    
    def make_notes(text):
        nonlocal current_transcript, current_notes
        
        progress_text.value = "AI.PROCESSING"
        progress_bar.visible = True
        progress_bar.content.controls[0].width = 600
        page.update()
        
        response = ollama.chat(model='llama3.2', messages=[{
            'role': 'user',
            'content': f"""Analyze this meeting transcript and create professional notes:

{text}

Format:
📋 EXECUTIVE SUMMARY
(2-3 sentences)

🔑 KEY DISCUSSION POINTS
- Point 1
- Point 2
- Point 3

✅ DECISIONS MADE
- Decision 1
- Decision 2

📝 ACTION ITEMS
- Task 1 - Owner - Deadline
- Task 2 - Owner - Deadline

➡️ NEXT STEPS
- Step 1
- Step 2"""
        }])
        
        current_transcript = text
        current_notes = response['message']['content']
        
        # Update UI
        transcript_box.content = ft.Column([
            ft.Text(text, size=12, selectable=True, color="#FFFFFF", font_family="DotMatrix"),
        ], scroll="auto")
        
        notes_box.content = ft.Column([
            ft.Text(current_notes, size=12, selectable=True, color="#FFFFFF", font_family="DotMatrix"),
        ], scroll="auto")
        
        enable_button(export_btn, "EXPORT")
        enable_button(copy_btn, "COPY")
        enable_button(save_db_btn, "SAVE.DB")
        
        status_text.value = "PROCESS.COMPLETE"
        status_text.color = "#FF0000"
        progress_bar.visible = False
        progress_text.value = ""
        page.update()
    
    def process_audio(filename):
        status_text.value = "TRANSCRIBING"
        status_text.color = "#FF0000"
        progress_bar.visible = True
        progress_bar.content.controls[0].width = 300
        page.update()
        
        audio_data, sr = sf.read(filename)
        audio_data = audio_data.astype(np.float32).flatten()
        
        if sr != 16000:
            from scipy import signal
            audio_data = signal.resample(audio_data, int(len(audio_data) * 16000 / sr))
        
        result = whisper_model.transcribe(audio_data, fp16=False, language="english")
        
        progress_text.value = "TRANSCRIPTION.COMPLETE"
        page.update()
        
        make_notes(result["text"])
    
    def toggle_record(e):
        nonlocal is_recording, frames, start_time, recording_duration
        
        if not is_recording:
            # START
            is_recording = True
            frames = []
            start_time = time.time()
            
            status_text.value = "RECORDING.ACTIVE"
            status_text.color = "#FF0000"
            duration_text.value = "00:00:00"
            
            record_btn.content = ft.Stack([
                ft.Container(
                    width=200,
                    height=200,
                    border=ft.border.all(4, "#FF0000"),
                    border_radius=0,
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("REC", size=32, weight=ft.FontWeight.W_900, color="#FF0000", font_family="DotMatrix"),
                        ft.Container(height=8),
                        ft.Container(width=60, height=3, bgcolor="#FF0000"),
                        ft.Container(height=8),
                        ft.Text("STOP", size=16, weight=ft.FontWeight.BOLD, color="#FF0000", font_family="DotMatrix"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    width=200,
                    height=200,
                    alignment=ft.alignment.center,
                ),
            ])
            
            record_indicator.visible = True
            
            transcript_box.content = ft.Column([
                ft.Text("RECORDING.IN.PROGRESS", size=12, color="#666666", font_family="DotMatrix", weight=ft.FontWeight.BOLD),
            ])
            notes_box.content = ft.Column([
                ft.Text("AI.STANDBY", size=12, color="#666666", font_family="DotMatrix", weight=ft.FontWeight.BOLD),
            ])
            
            disable_button(export_btn, "EXPORT")
            disable_button(copy_btn, "COPY")
            disable_button(save_db_btn, "SAVE.DB")
            
            page.update()
            
            # Start timer
            threading.Thread(target=update_timer, daemon=True).start()
            
            def callback(indata, f, t, s):
                if is_recording:
                    frames.append(indata.copy())
            
            global stream
            stream = sd.InputStream(samplerate=16000, channels=1, callback=callback)
            stream.start()
            
        else:
            # STOP
            is_recording = False
            recording_duration = int(time.time() - start_time)
            stream.stop()
            stream.close()
            
            status_text.value = "PROCESSING"
            status_text.color = "#FFFFFF"
            
            record_btn.content = ft.Stack([
                ft.Container(
                    width=200,
                    height=200,
                    border=ft.border.all(4, "#FFFFFF"),
                    border_radius=0,
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("REC", size=32, weight=ft.FontWeight.W_900, color="#FFFFFF", font_family="DotMatrix"),
                        ft.Container(height=8),
                        ft.Container(width=60, height=3, bgcolor="#FFFFFF"),
                        ft.Container(height=8),
                        ft.Text("START", size=16, weight=ft.FontWeight.BOLD, color="#FFFFFF", font_family="DotMatrix"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    width=200,
                    height=200,
                    alignment=ft.alignment.center,
                ),
            ])
            
            record_indicator.visible = False
            
            page.update()
            
            recording = np.concatenate(frames, axis=0)
            filename = f"meeting_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            sf.write(filename, recording, 16000)
            
            threading.Thread(target=process_audio, args=(filename,), daemon=True).start()
    
    record_btn.on_click = toggle_record
    
    # Helper function to create styled headers
    def styled_header(text, size=28, color="#FFFFFF", indicator_color="#FF0000"):
        return ft.Container(
            content=ft.Row([
                ft.Container(width=4, height=40, bgcolor=indicator_color),
                ft.Container(width=12),
                ft.Text(text, size=size, weight=ft.FontWeight.W_900, color=color, font_family="DotMatrix"),
            ]),
            padding=ft.padding.only(bottom=30),
        )
    
    # Recording tab layout
    recording_content = ft.Container(
        content=ft.Column([
            # Header
            styled_header("NEW.RECORDING"),
            
            ft.Container(
                content=ft.Column([
                    title_input,
                    ft.Container(height=30),
                    
                    # Status grid
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                record_indicator,
                                status_text,
                            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                            ft.Container(height=15),
                            duration_text,
                            ft.Container(height=10),
                            progress_text,
                            progress_bar,
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor="#0A0A0A",
                        border=ft.border.all(2, "#FFFFFF"),
                        padding=30,
                    ),
                    
                    ft.Container(height=40),
                    
                    # Record button
                    ft.Container(
                        content=record_btn,
                        alignment=ft.alignment.center,
                    ),
                    
                    ft.Container(height=40),
                    
                    # Transcript header
                    ft.Row([
                        ft.Container(width=3, height=20, bgcolor="#FFFFFF"),
                        ft.Container(width=8),
                        ft.Text("TRANSCRIPT", size=16, weight=ft.FontWeight.W_900, color="#FFFFFF", font_family="DotMatrix"),
                    ]),
                    ft.Container(height=10),
                    transcript_box,
                    
                    ft.Container(height=30),
                    
                    # Notes header
                    ft.Row([
                        ft.Container(width=3, height=20, bgcolor="#FF0000"),
                        ft.Container(width=8),
                        ft.Text("AI.NOTES", size=16, weight=ft.FontWeight.W_900, color="#FFFFFF", font_family="DotMatrix"),
                    ]),
                    ft.Container(height=10),
                    notes_box,
                    
                    ft.Container(height=40),
                    
                    # Action buttons
                    ft.Row([
                        export_btn,
                        copy_btn,
                        save_db_btn,
                    ], spacing=20, alignment=ft.MainAxisAlignment.CENTER),
                    
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ),
            
        ], scroll="auto", horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=40,
        expand=True,
    )
    
    # ============== HISTORY TAB ==============
    
    history_list = ft.Column(spacing=0, scroll="auto")
    search_field = ft.TextField(
        hint_text="SEARCH.MEETINGS",
        hint_style=ft.TextStyle(color="#333333", font_family="DotMatrix"),
        border_color="#FFFFFF",
        focused_border_color="#FF0000",
        border_width=2,
        bgcolor="#000000",
        color="#FFFFFF",
        text_style=ft.TextStyle(font_family="DotMatrix", size=12),
        cursor_color="#FF0000",
        on_change=lambda e: search_meetings(e.control.value)
    )
    
    detail_view = ft.Column(
        [
            ft.Container(
                content=ft.Column([
                    ft.Container(width=80, height=80, border=ft.border.all(2, "#333333")),
                    ft.Container(height=20),
                    ft.Text("SELECT.MEETING", size=16, color="#666666", weight=ft.FontWeight.BOLD, font_family="DotMatrix"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                expand=True,
            )
        ],
        scroll="auto",
    )
    
    def show_meeting_detail(meeting_id):
        meeting = db.get_meeting(meeting_id)
        
        if meeting:
            mid, title, date, audio, transcript_text, notes_text, duration = meeting
            
            hours = duration // 3600
            mins = (duration % 3600) // 60
            secs = duration % 60
            
            detail_view.controls = [
                # Header
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Container(width=4, height=30, bgcolor="#FF0000"),
                            ft.Container(width=12),
                            ft.Text(title or "UNTITLED", size=24, weight=ft.FontWeight.W_900, color="#FFFFFF", font_family="DotMatrix"),
                        ]),
                        ft.Container(height=15),
                        ft.Row([
                            ft.Text(date.split()[0], size=12, color="#666666", font_family="DotMatrix", weight=ft.FontWeight.BOLD),
                            ft.Container(width=20),
                            ft.Text(f"{hours:02d}:{mins:02d}:{secs:02d}", size=12, color="#666666", font_family="DotMatrix", weight=ft.FontWeight.BOLD),
                        ]),
                    ]),
                    padding=ft.padding.only(bottom=30),
                ),
                
                # Transcript
                ft.Row([
                    ft.Container(width=3, height=16, bgcolor="#FFFFFF"),
                    ft.Container(width=8),
                    ft.Text("TRANSCRIPT", size=14, weight=ft.FontWeight.W_900, color="#FFFFFF", font_family="DotMatrix"),
                ]),
                ft.Container(height=10),
                ft.Container(
                    content=ft.Text(transcript_text or "NO.DATA", size=11, selectable=True, color="#FFFFFF", font_family="DotMatrix"),
                    bgcolor="#0A0A0A",
                    border=ft.border.all(2, "#FFFFFF"),
                    padding=20,
                    height=250,
                ),
                
                ft.Container(height=25),
                
                # Notes
                ft.Row([
                    ft.Container(width=3, height=16, bgcolor="#FF0000"),
                    ft.Container(width=8),
                    ft.Text("AI.NOTES", size=14, weight=ft.FontWeight.W_900, color="#FFFFFF", font_family="DotMatrix"),
                ]),
                ft.Container(height=10),
                ft.Container(
                    content=ft.Text(notes_text or "NO.DATA", size=11, selectable=True, color="#FFFFFF", font_family="DotMatrix"),
                    bgcolor="#0A0A0A",
                    border=ft.border.all(2, "#FFFFFF"),
                    padding=20,
                    height=250,
                ),
                
                ft.Container(height=30),
                
                # Actions
                ft.Row([
                    ft.Container(
                        content=ft.Text("COPY", size=14, weight=ft.FontWeight.BOLD, color="#FFFFFF", font_family="DotMatrix"),
                        bgcolor="#000000",
                        border=ft.border.all(2, "#FFFFFF"),
                        padding=15,
                        width=200,
                        height=60,
                        alignment=ft.alignment.center,
                        on_click=lambda e: copy_meeting(transcript_text, notes_text),
                    ),
                    ft.Container(
                        content=ft.Text("DELETE", size=14, weight=ft.FontWeight.BOLD, color="#FF0000", font_family="DotMatrix"),
                        bgcolor="#000000",
                        border=ft.border.all(2, "#FF0000"),
                        padding=15,
                        width=200,
                        height=60,
                        alignment=ft.alignment.center,
                        on_click=lambda e: delete_meeting(mid),
                    ),
                ], spacing=20),
            ]
            page.update()
    
    def copy_meeting(transcript_text, notes_text):
        pyperclip.copy(f"TRANSCRIPT:\n{transcript_text}\n\nNOTES:\n{notes_text}")
        page.snack_bar = ft.SnackBar(
            content=ft.Text("CLIPBOARD.UPDATED", font_family="DotMatrix", size=12, weight=ft.FontWeight.BOLD),
            bgcolor="#FF0000"
        )
        page.snack_bar.open = True
        page.update()
    
    def delete_meeting(meeting_id):
        db.delete_meeting(meeting_id)
        detail_view.controls = [
            ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Text("✓", size=60, color="#FF0000", font_family="DotMatrix", weight=ft.FontWeight.W_900),
                        width=100,
                        height=100,
                        border=ft.border.all(3, "#FF0000"),
                        alignment=ft.alignment.center,
                    ),
                    ft.Container(height=20),
                    ft.Text("DELETED", size=18, color="#FF0000", weight=ft.FontWeight.BOLD, font_family="DotMatrix"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                expand=True,
            )
        ]
        page.update()
        refresh_history()
    
    def refresh_history():
        meetings = db.get_all_meetings()
        history_list.controls.clear()
        
        if not meetings:
            history_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Container(width=100, height=100, border=ft.border.all(2, "#333333")),
                        ft.Container(height=20),
                        ft.Text("NO.MEETINGS", size=14, color="#666666", font_family="DotMatrix", weight=ft.FontWeight.BOLD),
                        ft.Container(height=10),
                        ft.Text("RECORD.FIRST.MEETING", size=11, color="#333333", font_family="DotMatrix"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=50,
                )
            )
        else:
            for mid, title, date, duration in meetings:
                hours = duration // 3600
                mins = (duration % 3600) // 60
                
                def make_handler(meeting_id):
                    return lambda e: show_meeting_detail(meeting_id)
                
                card = ft.Container(
                    content=ft.Row([
                        ft.Container(width=3, height=50, bgcolor="#FF0000"),
                        ft.Container(width=15),
                        ft.Column([
                            ft.Text(title or "UNTITLED", size=13, weight=ft.FontWeight.W_900, color="#FFFFFF", font_family="DotMatrix"),
                            ft.Container(height=5),
                            ft.Text(f"{date.split()[0]} • {hours:02d}:{mins:02d}", size=10, color="#666666", font_family="DotMatrix", weight=ft.FontWeight.BOLD),
                        ], spacing=0, expand=True),
                        ft.Text(">", size=20, color="#FFFFFF", font_family="DotMatrix", weight=ft.FontWeight.BOLD),
                        ft.Container(width=10),
                    ]),
                    bgcolor="#0A0A0A",
                    border=ft.border.all(2, "#FFFFFF"),
                    padding=20,
                    on_click=make_handler(mid),
                    ink=True,
                )
                history_list.controls.append(card)
                history_list.controls.append(ft.Container(height=2))
        
        page.update()
    
    def search_meetings(keyword):
        if not keyword or keyword.strip() == "":
            refresh_history()
            return
        
        meetings = db.search_meetings(keyword)
        history_list.controls.clear()
        
        if not meetings:
            history_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Container(width=80, height=80, border=ft.border.all(2, "#333333")),
                        ft.Container(height=20),
                        ft.Text("NO.RESULTS", size=14, color="#666666", font_family="DotMatrix", weight=ft.FontWeight.BOLD),
                        ft.Container(height=10),
                        ft.Text(f"'{keyword.upper()}'", size=11, color="#FF0000", font_family="DotMatrix"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=40,
                )
            )
        else:
            for mid, title, date, duration in meetings:
                hours = duration // 3600
                mins = (duration % 3600) // 60
                
                def make_handler(meeting_id):
                    return lambda e: show_meeting_detail(meeting_id)
                
                card = ft.Container(
                    content=ft.Row([
                        ft.Container(width=3, height=50, bgcolor="#FF0000"),
                        ft.Container(width=15),
                        ft.Column([
                            ft.Text(title or "UNTITLED", size=13, weight=ft.FontWeight.W_900, color="#FFFFFF", font_family="DotMatrix"),
                            ft.Container(height=5),
                            ft.Text(f"{date.split()[0]} • {hours:02d}:{mins:02d}", size=10, color="#666666", font_family="DotMatrix", weight=ft.FontWeight.BOLD),
                        ], spacing=0, expand=True),
                        ft.Text(">", size=20, color="#FFFFFF", font_family="DotMatrix", weight=ft.FontWeight.BOLD),
                        ft.Container(width=10),
                    ]),
                    bgcolor="#0A0A0A",
                    border=ft.border.all(2, "#FFFFFF"),
                    padding=20,
                    on_click=make_handler(mid),
                    ink=True,
                )
                history_list.controls.append(card)
                history_list.controls.append(ft.Container(height=2))
        
        page.update()
    
    refresh_history()
    
    # History layout
    history_content = ft.Container(
        content=ft.Row([
            # Left sidebar
            ft.Container(
                content=ft.Column([
                    styled_header("HISTORY", size=24),
                    ft.Container(height=20),
                    search_field,
                    ft.Container(height=20),
                    ft.Container(
                        content=history_list,
                        height=720,
                        bgcolor="#000000",
                    ),
                ]),
                width=450,
                padding=30,
                bgcolor="#000000",
            ),
            
            ft.Container(width=2, bgcolor="#FFFFFF"),
            
            # Right detail panel
            ft.Container(
                content=detail_view,
                expand=True,
                padding=40,
                bgcolor="#000000",
            ),
        ]),
        expand=True,
        bgcolor="#000000",
    )
    
    # ============== TABS ==============
    
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=200,
        label_color="#FFFFFF",
        unselected_label_color="#666666",
        indicator_color="#FF0000",
        indicator_border_radius=0,
        indicator_padding=0,
        tabs=[
            ft.Tab(
                text="RECORD",
                icon=ft.Icons.FIBER_MANUAL_RECORD,
                content=recording_content,
            ),
            ft.Tab(
                text="HISTORY",
                icon=ft.Icons.STORAGE,
                content=history_content,
            ),
        ],
        expand=True,
    )
    
    # Main layout with top bar
    main_view = ft.Column([
        # Top bar - Nothing OS style
        ft.Container(
            content=ft.Row([
                ft.Container(width=20),
                ft.Container(width=6, height=6, bgcolor="#FF0000", border_radius=3),
                ft.Container(width=10),
                ft.Text("MEETING.NOTES.PRO", size=14, weight=ft.FontWeight.W_900, color="#FFFFFF", font_family="DotMatrix"),
                ft.Container(expand=True),
                ft.Text(datetime.now().strftime("%H:%M"), size=14, weight=ft.FontWeight.BOLD, color="#FFFFFF", font_family="DotMatrix"),
                ft.Container(width=20),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor="#000000",
            height=60,
            border=ft.border.only(bottom=ft.BorderSide(2, "#FFFFFF")),
        ),
        tabs,
    ], spacing=0, expand=True)
    
    page.add(main_view)

ft.app(target=main)
