# gui.py

import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from assets.config import APP_SIZE, TITLE, COLORS, STYLING

# Asegúrate de que tu backend.diarize.run_diarization existe
# Si no, puedes comentar la siguiente línea para probar la UI
from backend.diarize import run_diarization

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
        
        # --- Configuración de la validación ---
        validate_cmd = self.register(self._validate_numeric_input)

        # --- UI principal ---
        # Contenedor principal para centrar el contenido
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(expand=True, fill="both", padx=20, pady=20)

        # 1. Marco de selección de archivos
        self._create_file_selection_frame()

        # 2. Marco de configuración de altavoces
        self._create_speaker_options_frame(validate_cmd)

        # 3. Marco de acción y progreso
        self._create_action_progress_frame()

    def _create_file_selection_frame(self):
        """Crea el frame para la selección de archivo de audio y directorio de salida."""
        frame = ctk.CTkFrame(self.main_container, fg_color=COLORS['main_panel'], corner_radius=STYLING['corner_radius'])
        frame.pack(fill="x", pady=(0, 10))

        # Audio file selector
        ctk.CTkLabel(frame, text="Audio File", text_color=COLORS['text_secondary']).grid(row=0, column=0, padx=20, pady=(20,10), sticky="w")
        audio_entry = ctk.CTkEntry(frame, textvariable=self.audio_path_var, fg_color=COLORS['input_surface'], border_color=COLORS['border'], text_color=COLORS['text_primary'])
        audio_entry.grid(row=0, column=1, padx=(0,10), pady=(20,10), sticky="ew")
        ctk.CTkButton(frame, text="Browse", command=self.browse_audio, 
                      fg_color=COLORS['primary_action'],
                      hover_color=COLORS['hover_action']).grid(row=0, column=2, padx=(0,20), pady=(20,10))

        # Output directory selector
        ctk.CTkLabel(frame, text="Output Directory", text_color=COLORS['text_secondary']).grid(row=1, column=0, padx=20, pady=(0,20), sticky="w")
        output_entry = ctk.CTkEntry(frame, textvariable=self.output_dir_var, fg_color=COLORS['input_surface'], border_color=COLORS['border'], text_color=COLORS['text_primary'])
        output_entry.grid(row=1, column=1, padx=(0,10), pady=(0,20), sticky="ew")
        ctk.CTkButton(frame, text="Browse", command=self.browse_output, 
                      hover_color=COLORS['hover_action'],fg_color=COLORS['primary_action']).grid(row=1, column=2, padx=(0,20), pady=(0,20))

        frame.grid_columnconfigure(1, weight=1)

    def _create_speaker_options_frame(self, validate_cmd):
        """Crea el frame para las opciones de número de altavoces."""
        frame = ctk.CTkFrame(self.main_container, fg_color=COLORS['main_panel'], corner_radius=STYLING['corner_radius'])
        frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(frame, text="Speaker Configuration (Optional)", text_color=COLORS['text_secondary']).pack(pady=(10,5))
        
        options_container = ctk.CTkFrame(frame, fg_color="transparent")
        options_container.pack(pady=(5,20))

        # Number of speakers
        ctk.CTkLabel(options_container, text="Num Speakers:").grid(row=0, column=0, padx=(10,5), sticky="e")
        num_entry = ctk.CTkEntry(options_container, textvariable=self.num_speakers_var, width=80, fg_color=COLORS['input_surface'], border_color=COLORS['border'], validate="key", validatecommand=(validate_cmd, '%P'))
        num_entry.grid(row=0, column=1, sticky="w")

        # Min speakers
        ctk.CTkLabel(options_container, text="Min Speakers:").grid(row=0, column=2, padx=(20,5), sticky="e")
        min_entry = ctk.CTkEntry(options_container, textvariable=self.min_speakers_var, width=80, fg_color=COLORS['input_surface'], border_color=COLORS['border'], validate="key", validatecommand=(validate_cmd, '%P'))
        min_entry.grid(row=0, column=3, sticky="w")

        # Max speakers
        ctk.CTkLabel(options_container, text="Max Speakers:").grid(row=0, column=4, padx=(20,5), sticky="e")
        max_entry = ctk.CTkEntry(options_container, textvariable=self.max_speakers_var, width=80, fg_color=COLORS['input_surface'], border_color=COLORS['border'], validate="key", validatecommand=(validate_cmd, '%P'))
        max_entry.grid(row=0, column=5, padx=(0,10), sticky="w")

    def _create_action_progress_frame(self):
        """Crea el frame para el botón de inicio, la barra de progreso y el estado."""
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        frame.pack(fill="x", pady=(20, 0))
        
        self.start_btn = ctk.CTkButton(frame, text="Start Diarization", command=self.start,
                                        fg_color=COLORS['primary_action'],hover_color=COLORS['hover_action'],
                                        height=40)
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
        """Permite solo dígitos o un string vacío."""
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
            self.after(0, lambda: self.status_label.configure(text="Status: Running diarization..."))
            
            # --- Simulación de progreso si no tienes un callback real ---
            # import time
            # for i in range(1, 11):
            #     self.after(0, self._update_progress, i / 10.0)
            #     time.sleep(0.5)
            # rttm_path = "simulation_done.rttm"
            # --- Fin Simulación ---
            
            # --- Tu código real ---
            def progress_cb(progress_float):
                self.after(0, self._update_progress, progress_float)
                
            rttm_path, diar = run_diarization(audio, outdir, num_speakers=num, min_speakers=mn, max_speakers=mx, progress_callback=progress_cb)
            # --- Fin código real ---

            self.after(0, lambda: self.status_label.configure(text=f"Success! RTTM file saved."))
            messagebox.showinfo("Done", f"Diarization complete.\n\nRTTM saved to:\n{rttm_path}")
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.after(0, lambda: self.status_label.configure(text="Status: Error"))
        
        finally:
            self.after(0, lambda: self.start_btn.configure(state="normal", text="Start Diarization"))
            self.after(0, lambda: self.progress.set(0.0))

    def _update_progress(self, value):
        try:
            self.progress.set(max(0.0, min(1.0, float(value))))
        except Exception as e:
            print(f"Error updating progress: {e}")