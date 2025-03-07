import sys
import os

# Only do this if we're running from a frozen EXE (i.e., PyInstaller)
if getattr(sys, 'frozen', False):
    from pydub import AudioSegment
    exe_folder = os.path.dirname(sys.executable)
    # Use local copies of ffmpeg.exe and ffprobe.exe in the same folder as the EXE
    AudioSegment.ffmpeg = os.path.join(exe_folder, "ffmpeg.exe")
    AudioSegment.ffprobe = os.path.join(exe_folder, "ffprobe.exe")

import tkinter as tk
from tkinter import filedialog, messagebox
import os

from audio_chopper import chop_audio

class ChopperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Chopper")

        # --- Input File ---
        tk.Label(root, text="Input Audio File:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.input_file_var = tk.StringVar()
        tk.Entry(root, textvariable=self.input_file_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(root, text="Browse...", command=self.browse_input_file).grid(row=0, column=2, padx=5, pady=5)

        # --- Output Folder ---
        tk.Label(root, text="Output Folder (optional):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.output_folder_var = tk.StringVar()
        tk.Entry(root, textvariable=self.output_folder_var, width=50).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(root, text="Browse...", command=self.browse_output_folder).grid(row=1, column=2, padx=5, pady=5)

        # --- Chunk Type ---
        tk.Label(root, text="Chunk Type (bars/beats):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.chunk_type_var = tk.StringVar(value="bars")
        tk.OptionMenu(root, self.chunk_type_var, "bars", "beats").grid(row=2, column=1, sticky="w")

        # --- Chunk Size ---
        tk.Label(root, text="Chunk Size (# of bars/beats):").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.chunk_size_var = tk.IntVar(value=4)
        tk.Entry(root, textvariable=self.chunk_size_var, width=10).grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # --- Skip Type ---
        tk.Label(root, text="Skip Type (bars/beats):").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.skip_type_var = tk.StringVar(value="bars")
        tk.OptionMenu(root, self.skip_type_var, "bars", "beats").grid(row=4, column=1, sticky="w")

        # --- Skip Count ---
        tk.Label(root, text="Skip Count (# of bars/beats):").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.skip_count_var = tk.IntVar(value=0)
        tk.Entry(root, textvariable=self.skip_count_var, width=10).grid(row=5, column=1, padx=5, pady=5, sticky="w")

        # --- Output Prefix ---
        tk.Label(root, text="Output Prefix:").grid(row=6, column=0, padx=5, pady=5, sticky="e")
        self.output_prefix_var = tk.StringVar(value="segment")
        tk.Entry(root, textvariable=self.output_prefix_var, width=20).grid(row=6, column=1, padx=5, pady=5, sticky="w")

        # --- Chop Button ---
        tk.Button(root, text="Chop!", command=self.run_chop).grid(row=7, column=0, columnspan=3, pady=10)

        # --- Status/Log box ---
        tk.Label(root, text="Status / Log:").grid(row=8, column=0, padx=5, pady=5, sticky="ne")
        self.log_text = tk.Text(root, height=10, width=60, state=tk.DISABLED)
        self.log_text.grid(row=8, column=1, columnspan=2, padx=5, pady=5)

    def browse_input_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[("Audio Files", "*.mp3 *.wav *.flac *.ogg *.m4a"), ("All Files", "*.*")]
        )
        if file_path:
            self.input_file_var.set(file_path)

    def browse_output_folder(self):
        folder_path = filedialog.askdirectory(title="Select Output Folder")
        if folder_path:
            self.output_folder_var.set(folder_path)

    def gui_logger(self, message):
        """
        Appends 'message' to the Text widget log_text.
        """
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.see(tk.END)  # auto-scroll to bottom

    def run_chop(self):
        # Clear the log first (optional)
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)

        input_file = self.input_file_var.get()
        output_folder = self.output_folder_var.get().strip()
        chunk_type = self.chunk_type_var.get()
        chunk_size = self.chunk_size_var.get()
        skip_type = self.skip_type_var.get()
        skip_count = self.skip_count_var.get()
        output_prefix = self.output_prefix_var.get()

        if not input_file or not os.path.exists(input_file):
            messagebox.showerror("Error", "Please select a valid input audio file.")
            return

        # If user left output_folder blank, pass None so the chopper can create one
        if not output_folder:
            output_folder = None

        # Now call chop_audio with our custom logger
        try:
            chop_audio(
                input_audio_path=input_file,
                output_folder=output_folder,
                chunk_type=chunk_type,
                chunk_size=chunk_size,
                skip_type=skip_type,
                skip_count=skip_count,
                output_prefix=output_prefix,
                log_callback=self.gui_logger  # <--- Here is the magic
            )
            messagebox.showinfo("Done", "All segments exported successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ChopperGUI(root)
    root.mainloop()
