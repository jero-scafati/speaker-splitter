import os
import threading
import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog, messagebox
from assets.config import APP_SIZE, TITLE, COLORS, STYLING

# Importar ambas funciones del backend
from backend.diarize import run_diarization
from backend.audio_splitter import split_audio_by_speaker

class App(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=COLORS['background'])
        self.title(TITLE)
        self.geometry(f'{APP_SIZE[0]}x{APP_SIZE[1]}')
        self.resizable(False, False)

        # --- Variables de estado ---
        self.audio_path_var = ctk.StringVar()
        self.output_dir_var = ctk.StringVar()
        self.num_speakers_var = ctk.StringVar()
        self.min_speakers_var = ctk.StringVar()
        self.max_speakers_var = ctk.StringVar()
        
        validate_cmd = self.register(self._validate_numeric_input)

        # --- UI principal ---
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(expand=True, fill="both", padx=20, pady=20)
        
        self._create_file_selection_frame()
        self._create_speaker_options_frame(validate_cmd)
        self._create_action_progress_frame()

    def _create_file_selection_frame(self):
        frame = ctk.CTkFrame(self.main_container, fg_color=COLORS['main_panel'], corner_radius=STYLING['corner_radius'])
        frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(frame, text="Audio File", text_color=COLORS['text_secondary']).grid(row=0, column=0, padx=20, pady=(20,10), sticky="w")
        ctk.CTkEntry(frame, textvariable=self.audio_path_var, fg_color=COLORS['input_surface'], border_color=COLORS['border'], text_color=COLORS['text_primary']).grid(row=0, column=1, padx=(0,10), pady=(20,10), sticky="ew")
        ctk.CTkButton(frame, text="Browse", command=self.browse_audio, fg_color=COLORS['primary_action']).grid(row=0, column=2, padx=(0,20), pady=(20,10))

        ctk.CTkLabel(frame, text="Output Directory", text_color=COLORS['text_secondary']).grid(row=1, column=0, padx=20, pady=(0,20), sticky="w")
        ctk.CTkEntry(frame, textvariable=self.output_dir_var, fg_color=COLORS['input_surface'], border_color=COLORS['border'], text_color=COLORS['text_primary']).grid(row=1, column=1, padx=(0,10), pady=(0,20), sticky="ew")
        ctk.CTkButton(frame, text="Browse", command=self.browse_output, fg_color=COLORS['primary_action']).grid(row=1, column=2, padx=(0,20), pady=(0,20))

        frame.grid_columnconfigure(1, weight=1)

    def _create_speaker_options_frame(self, validate_cmd):
        frame = ctk.CTkFrame(self.main_container, fg_color=COLORS['main_panel'], corner_radius=STYLING['corner_radius'])
        frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(frame, text="Speaker Configuration (Optional)", text_color=COLORS['text_secondary']).pack(pady=(10,5))
        options_container = ctk.CTkFrame(frame, fg_color="transparent")
        options_container.pack(pady=(5,20))

        ctk.CTkLabel(options_container, text="Num Speakers:").grid(row=0, column=0, padx=(10,5), sticky="e")
        ctk.CTkEntry(options_container, textvariable=self.num_speakers_var, width=80, fg_color=COLORS['input_surface'], border_color=COLORS['border'], validate="key", validatecommand=(validate_cmd, '%P')).grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(options_container, text="Min Speakers:").grid(row=0, column=2, padx=(20,5), sticky="e")
        ctk.CTkEntry(options_container, textvariable=self.min_speakers_var, width=80, fg_color=COLORS['input_surface'], border_color=COLORS['border'], validate="key", validatecommand=(validate_cmd, '%P')).grid(row=0, column=3, sticky="w")
        ctk.CTkLabel(options_container, text="Max Speakers:").grid(row=0, column=4, padx=(20,5), sticky="e")
        ctk.CTkEntry(options_container, textvariable=self.max_speakers_var, width=80, fg_color=COLORS['input_surface'], border_color=COLORS['border'], validate="key", validatecommand=(validate_cmd, '%P')).grid(row=0, column=5, padx=(0,10), sticky="w")

    def _create_action_progress_frame(self):
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        frame.pack(fill="x", pady=(20, 0))
        
        self.start_btn = ctk.CTkButton(frame, text="Start Diarization & Split", command=self.start, fg_color=COLORS['primary_action'], height=40)
        self.start_btn.pack()

        self.progress = ctk.CTkProgressBar(frame, progress_color=COLORS['accent_cyan'])
        self.progress.set(0.0)
        self.progress.pack(fill="x", padx=50, pady=(20,5))

        self.status_label = ctk.CTkLabel(frame, text="Status: Idle", text_color=COLORS['text_secondary'])
        self.status_label.pack()

    def browse_audio(self):
        path = filedialog.askopenfilename(title="Select audio file", filetypes=[("Audio Files", "*.wav *.flac *.mp3")])
        if path: self.audio_path_var.set(path)

    def browse_output(self):
        path = filedialog.askdirectory(title="Select output directory")
        if path: self.output_dir_var.set(path)
    
    def _validate_numeric_input(self, value_if_allowed):
        return value_if_allowed.isdigit() or value_if_allowed == ""

    def start(self):
        audio = self.audio_path_var.get()
        outdir = self.output_dir_var.get()
        if not audio or not os.path.isfile(audio):
            messagebox.showerror("Error", "Please select a valid audio file.")
            return
        if not outdir:
            messagebox.showerror("Error", "Please select an output directory.")
            return

        self.start_btn.configure(state="disabled", text="Processing...")
        self.status_label.configure(text="Status: Starting...")

        num = self.num_speakers_var.get() or None
        mn = self.min_speakers_var.get() or None
        mx = self.max_speakers_var.get() or None

        thread = threading.Thread(target=self._run_diarize_thread, args=(audio, outdir, num, mn, mx), daemon=True)
        thread.start()

    def _run_diarize_thread(self, audio, outdir, num, mn, mx):
        try:
            # --- FASE 1: DIARIZACIÓN ---
            self.after(0, lambda: self.status_label.configure(text="Status: Running diarization..."))
            
            def progress_cb(progress_float):
                # Usamos la mitad de la barra para la diarización
                self.after(0, self._update_progress, progress_float * 0.5)
                
            rttm_file = run_diarization(audio, outdir, num_speakers=num, min_speakers=mn, max_speakers=mx, progress_callback=progress_cb)
            
            self.after(0, self._update_progress, 0.5) # Marcar 50% completado

            # --- FASE 2: DIVISIÓN DE AUDIO ---
            self.after(0, lambda: self.status_label.configure(text="Status: Splitting audio by speaker..."))
            
            total_saved = split_audio_by_speaker(
                audio_path=Path(audio),
                rttm_file=rttm_file,
                outdir=Path(outdir)
            )
            
            self.after(0, self._update_progress, 1.0) # Marcar 100% completado

            # --- FINALIZACIÓN ---
            final_message = f"Process Complete!\n\nSaved {total_saved} audio segments to:\n{outdir}"
            self.after(0, lambda: self.status_label.configure(text=f"Success! Saved {total_saved} segments."))
            self.after(0, lambda: messagebox.showinfo("Done", final_message))
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.after(0, lambda: self.status_label.configure(text="Status: Error"))
        
        finally:
            self.after(0, lambda: self.start_btn.configure(state="normal", text="Start Diarization & Split"))
            self.after(0, lambda: self.progress.set(0.0))

    def _update_progress(self, value):
        self.progress.set(max(0.0, min(1.0, float(value))))