import os
import threading
import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog, messagebox
from gui.config import APP_SIZE, TITLE, COLORS, STYLING
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
        self.min_duration_var = ctk.StringVar(value="0.5")
        self.hf_token_var = ctk.StringVar()
        
        validate_cmd = self.register(self._validate_numeric_input)

        # --- UI principal ---
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(expand=True, fill="both", padx=20, pady=20)
        
        self._create_token_frame()
        self._create_file_selection_frame()
        self._create_speaker_options_frame(validate_cmd)
        self._create_action_frame()

    def _create_token_frame(self):
        frame = ctk.CTkFrame(self.main_container, fg_color=COLORS['main_panel'], corner_radius=STYLING['corner_radius'])
        frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(frame, text="Hugging Face Token", text_color=COLORS['text_secondary']).grid(row=0, column=0, padx=20, pady=(15, 0), sticky="w")
        

        token_entry = ctk.CTkEntry(frame, textvariable=self.hf_token_var, show="*", fg_color=COLORS['input_surface'], border_color=COLORS['border'], text_color=COLORS['text_primary'])
        token_entry.grid(row=1, column=0, columnspan=2, padx=20, pady=(5, 5), sticky="ew")

        info_label = ctk.CTkLabel(frame, text="Required for the diarization model. Get your token from your Hugging Face profile.", text_color=COLORS['text_secondary'], font=("Arial", 11))
        info_label.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 15), sticky="w")
        
        frame.grid_columnconfigure(0, weight=1)

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
        options_container.pack(pady=(5,20), padx=20)

        ctk.CTkLabel(options_container, text="Num Speakers:").grid(row=0, column=0, padx=(10,5), sticky="e")
        ctk.CTkEntry(options_container, textvariable=self.num_speakers_var, width=80, fg_color=COLORS['input_surface'], border_color=COLORS['border'], validate="key", validatecommand=(validate_cmd, '%P')).grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(options_container, text="Min Speakers:").grid(row=0, column=2, padx=(20,5), sticky="e")
        ctk.CTkEntry(options_container, textvariable=self.min_speakers_var, width=80, fg_color=COLORS['input_surface'], border_color=COLORS['border'], validate="key", validatecommand=(validate_cmd, '%P')).grid(row=0, column=3, sticky="w")
        ctk.CTkLabel(options_container, text="Max Speakers:").grid(row=0, column=4, padx=(20,5), sticky="e")
        ctk.CTkEntry(options_container, textvariable=self.max_speakers_var, width=80, fg_color=COLORS['input_surface'], border_color=COLORS['border'], validate="key", validatecommand=(validate_cmd, '%P')).grid(row=0, column=5, padx=(0,10), sticky="w")

        ctk.CTkLabel(options_container, text="Min Duration (s):").grid(row=1, column=0, padx=(10,5), pady=(10,0), sticky="e")
        ctk.CTkEntry(options_container, textvariable=self.min_duration_var, width=80, fg_color=COLORS['input_surface'], border_color=COLORS['border']).grid(row=1, column=1, pady=(10,0), sticky="w")
        info_frame = ctk.CTkFrame(options_container, fg_color=COLORS['input_surface'])
        info_frame.grid(row=1, column=2, columnspan=4, padx=(20, 10), pady=(10,0), sticky="we")
        
        info_label = ctk.CTkLabel(info_frame, text="Segments below Min duration won't be saved as audio files", text_color=COLORS['text_secondary'], font=("Arial", 11))
        info_label.pack(padx=10, pady=5)
        options_container.grid_columnconfigure(2, weight=1)

    def _create_action_frame(self):
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        frame.pack(fill="x", pady=(20, 0), expand=True)
        
        self.start_btn = ctk.CTkButton(frame, text="Split Audio", command=self.start, fg_color=COLORS['primary_action'], height=40)
        self.start_btn.pack(pady=(0, 10))

        self.status_label = ctk.CTkLabel(frame, text="Status: Idle", text_color=COLORS['text_secondary'])
        self.status_label.pack(pady=(5,0))

    def browse_audio(self):
        path = filedialog.askopenfilename(title="Select audio file", filetypes=[("Audio Files", "*.wav *.flac *.mp3")])
        if path: self.audio_path_var.set(path)

    def browse_output(self):
        path = filedialog.askdirectory(title="Select output directory")
        if path: self.output_dir_var.set(path)
    
    def _validate_numeric_input(self, value_if_allowed):
        return value_if_allowed.isdigit() or value_if_allowed == ""

    def start(self):
        hf_token = self.hf_token_var.get()
        if not hf_token or not hf_token.startswith("hf_"):
            messagebox.showerror("Error", "Please enter a valid Hugging Face token.")
            return

        audio = self.audio_path_var.get()
        outdir = self.output_dir_var.get()
        if not audio or not os.path.isfile(audio):
            messagebox.showerror("Error", "Please select a valid audio file.")
            return
        if not outdir:
            messagebox.showerror("Error", "Please select an output directory.")
            return

        min_duration_str = self.min_duration_var.get()
        try:
            min_duration = float(min_duration_str)
            if min_duration < 0: raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive number for 'Min Duration'.")
            return

        self.start_btn.configure(state="disabled", text="Processing...")
        self.status_label.configure(text="Status: Starting...")

        num = self.num_speakers_var.get() or None
        mn = self.min_speakers_var.get() or None
        mx = self.max_speakers_var.get() or None

        thread = threading.Thread(target=self._run_process_thread, args=(audio, outdir, num, mn, mx, min_duration, hf_token), daemon=True)
        thread.start()

    def _run_process_thread(self, audio, outdir, num, mn, mx, min_duration, hf_token):
        try:
            self.after(0, lambda: self.status_label.configure(text="Status: Diarizing audio... (this may take a while)"))
            
            rttm_file = run_diarization(audio, outdir, num_speakers=num, min_speakers=mn, max_speakers=mx, hf_token=hf_token)

            self.after(0, lambda: self.status_label.configure(text="Status: Splitting audio by speaker..."))
            
            total_saved = split_audio_by_speaker(
                audio_path=Path(audio),
                rttm_file=rttm_file,
                outdir=Path(outdir),
                min_duration=min_duration
            )

            final_message = f"Process Complete!\n\nSaved {total_saved} audio segments to:\n{outdir}"
            self.after(0, lambda: self.status_label.configure(text=f"Success! Saved {total_saved} segments."))
            self.after(0, lambda: messagebox.showinfo("Done", final_message))
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.after(0, lambda: self.status_label.configure(text="Status: Error"))
        
        finally:
            self.after(0, lambda: self.start_btn.configure(state="normal", text="Split Audio"))
            self.after(0, lambda: self.status_label.configure(text="Status: Idle"))