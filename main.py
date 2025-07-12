import os
import io
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from yt_dlp import YoutubeDL
from urllib.request import urlopen
from PIL import Image, ImageTk
import ctypes
import subprocess
import sys

def clean_title(title):
    return "".join(c for c in title if c.isalnum() or c in " _-.").strip(" _-.")

class SocialSnapApp(tk.Tk):
    def __init__(self):
        super().__init__()
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
        self.title("✨ SocialSnap Media Downloader")
        self.geometry("1000x800")
        self.minsize(800, 600)
        self.download_dir = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads", "SocialSnap"))
        os.makedirs(self.download_dir.get(), exist_ok=True)
        self.tk.call("tk", "scaling", 1.5)
        self.playlist_entries = []
        self._setup_widgets()

    def _setup_widgets(self):
        BG_COLOR = "#1A1A2E"
        FRAME_COLOR = "#16213E"
        TEXT_COLOR = "#E5E5E5"
        ACCENT_COLOR = "#7B2CBF"
        ENTRY_BG = "#242B52"
        SUBTLE_TEXT = "#9BA4B4"
        BUTTON_HOVER = "#9D4EDD"

        self.configure(bg=BG_COLOR)
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=BG_COLOR)
        style.configure("TLabelframe", background=FRAME_COLOR, foreground=TEXT_COLOR)
        style.configure("TLabelframe.Label", background=FRAME_COLOR, foreground=TEXT_COLOR, font=("Segoe UI", 10, "bold"))
        style.configure("TLabel", background=FRAME_COLOR, foreground=TEXT_COLOR, font=("Segoe UI", 10))
        style.configure("TButton", background=ACCENT_COLOR, foreground=TEXT_COLOR, padding=10, font=("Segoe UI", 10, "bold"))
        style.map("TButton", background=[("active", BUTTON_HOVER)], foreground=[("active", TEXT_COLOR)])
        style.configure("TEntry", fieldbackground=ENTRY_BG, foreground=TEXT_COLOR, padding=8)
        style.configure("TCombobox", fieldbackground=ENTRY_BG, background=ACCENT_COLOR, foreground=TEXT_COLOR, arrowcolor=TEXT_COLOR, padding=8)
        style.map("TCombobox", fieldbackground=[("readonly", ENTRY_BG)], selectbackground=[("readonly", ACCENT_COLOR)])
        style.configure("Horizontal.TProgressbar", thickness=8, background=ACCENT_COLOR, troughcolor=ENTRY_BG, bordercolor=FRAME_COLOR)

        canvas_frame = ttk.Frame(self)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(canvas_frame, bg=BG_COLOR, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_frame, width=e.width))

        url_group = ttk.LabelFrame(self.scrollable_frame, text=" Video / Playlist URL ", padding=15)
        url_group.pack(fill=tk.X, pady=(20,10), padx=20)
        url_layout = ttk.Frame(url_group)
        url_layout.pack(fill=tk.X, padx=5, pady=5)

        self.url_entry = ttk.Entry(url_layout)
        self.url_entry.insert(0, "Enter YouTube URL or Playlist...")
        self.url_entry.bind("<FocusIn>", lambda e: self.url_entry.delete(0, tk.END) if self.url_entry.get().startswith("Enter") else None)
        self.url_entry.pack(fill=tk.X, pady=5, ipady=6)
        self.url_entry.bind("<Return>", lambda e: self.fetch_formats())

        self.fetch_button = ttk.Button(url_layout, text="Detect Available Formats", command=self.fetch_formats)
        self.fetch_button.pack(fill=tk.X, pady=5, ipady=8)

        options_group = ttk.LabelFrame(self.scrollable_frame, text=" Download Options ", padding=15)
        options_group.pack(fill=tk.X, pady=15, padx=20)
        options_layout = ttk.Frame(options_group)
        options_layout.pack(fill=tk.X, padx=5, pady=5)

        self.format_combo = ttk.Combobox(options_layout, state="readonly")
        self.format_combo.pack(fill=tk.X, pady=5, ipady=6)

        progress_group = ttk.LabelFrame(self.scrollable_frame, text=" Download Progress ", padding=15)
        progress_group.pack(fill=tk.X, pady=15, padx=20)
        progress_layout = ttk.Frame(progress_group)
        progress_layout.pack(fill=tk.X, padx=5, pady=5)

        self.progress_bar = ttk.Progressbar(progress_layout, mode="indeterminate")
        self.progress_bar.pack(fill=tk.X, pady=5)
        self.percent_label = ttk.Label(progress_layout, text="", foreground=SUBTLE_TEXT)
        self.percent_label.pack()

        self.title_label = ttk.Label(progress_layout, text="Current video: None", wraplength=800)
        self.title_label.pack(fill=tk.X, pady=2)
        self.thumbnail_label = ttk.Label(progress_layout)
        self.thumbnail_label.pack(pady=5)

        self.download_button = ttk.Button(self.scrollable_frame, text="Download", command=self.start_playlist_download, state=tk.DISABLED)
        self.download_button.pack(fill=tk.X, pady=10, padx=10, ipady=8)

    def fetch_formats(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Input Required", "Please enter a valid URL.")
            return
        threading.Thread(target=self._get_formats_worker, args=(url,), daemon=True).start()

    def _get_formats_worker(self, url):
        self._set_loading(True)
        try:
            with YoutubeDL({"quiet": True, "nocheckcertificate": True}) as ydl:
                info = ydl.extract_info(url, download=False)
            self.playlist_entries = []
            if info.get('_type') == 'playlist':
                for entry in info.get('entries', []):
                    if entry and entry.get("url"):
                        self.playlist_entries.append(entry["url"])
                    elif entry and entry.get("webpage_url"):
                        self.playlist_entries.append(entry["webpage_url"])
                    elif entry and entry.get("id"):
                        self.playlist_entries.append(f"https://www.youtube.com/watch?v={entry['id']}")
            else:
                self.playlist_entries = [url]
            first_video_url = self.playlist_entries[0]
            with YoutubeDL({"quiet": True, "nocheckcertificate": True}) as ydl:
                first_info = ydl.extract_info(first_video_url, download=False)
            self._load_thumbnail(first_info.get("thumbnail"))
            self.title_label.config(text=f"Current video: {first_info.get('title')}")
            formats = []
            for f in first_info.get("formats", []):
                if not f.get('format_id'):
                    continue
                label = self._create_format_label(f)
                if label:
                    formats.append((0 if f.get("ext")=="webm" else 1, label, f.get("format_id")))
            formats.sort()
            self.format_combo["values"] = [l for _,l,_ in formats]
            self.format_ids = [f_id for _,_,f_id in formats]
            if formats:
                self.format_combo.set(formats[0][1])
                self.download_button.config(state=tk.NORMAL)
            else:
                self.download_button.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Error", f"Could not fetch formats.\n\nDetails: {str(e)}")
        self._set_loading(False)

    def _set_loading(self, loading=True):
        if loading:
            self.fetch_button.config(state=tk.DISABLED)
            self.download_button.config(state=tk.DISABLED)
            self.progress_bar.start(10)
        else:
            self.fetch_button.config(state=tk.NORMAL)
            self.progress_bar.stop()
            self.progress_bar['value'] = 0

    def _create_format_label(self, f):
        acodec, vcodec = f.get("acodec", "none"), f.get("vcodec", "none")
        ext, height, abr = f.get("ext", "n/a"), f.get("height"), f.get("abr")
        label_parts = []
        if vcodec != "none":
            label_parts.append(f"{height}p" if height else "Video")
        if acodec != "none" and vcodec != "none":
            label_parts.append("with Audio")
        elif acodec != "none":
            label_parts.append(f"{round(abr)}kbps" if abr else "Audio")
        return f"{' | '.join(label_parts)} ({ext})"

    def _load_thumbnail(self, url):
        try:
            if url:
                with urlopen(url, timeout=5) as u:
                    raw_data = u.read()
                img = Image.open(io.BytesIO(raw_data)).resize((240, 135))
                self.thumbnail_image = ImageTk.PhotoImage(img)
                self.thumbnail_label.config(image=self.thumbnail_image)
            else:
                self.thumbnail_label.config(image="")
        except:
            self.thumbnail_label.config(image="")

    def start_playlist_download(self):
        selected = self.format_combo.get()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a format.")
            return
        idx = self.format_combo["values"].index(selected)
        format_id = self.format_ids[idx]
        threading.Thread(target=self._download_worker, args=(format_id,), daemon=True).start()

    def _download_worker(self, format_id):
        self._set_loading(True)
        try:
            for idx, video_url in enumerate(self.playlist_entries, start=1):
                with YoutubeDL({"quiet": True, "nocheckcertificate": True}) as ydl:
                    info = ydl.extract_info(video_url, download=False)
                title = clean_title(info.get("title", f"video_{idx}"))
                self.title_label.config(text=f"Downloading: {title} ({idx}/{len(self.playlist_entries)})")
                self._load_thumbnail(info.get("thumbnail"))

                selected_format = next((f for f in info["formats"] if f.get("format_id") == format_id), None)
                acodec, vcodec = selected_format.get("acodec", "none"), selected_format.get("vcodec", "none")
                ext = selected_format.get("ext", "mp4")

                ffmpeg_path = "ffmpeg"
                if getattr(sys, 'frozen', False):
                    ffmpeg_path = os.path.join(sys._MEIPASS, "ffmpeg.exe")

                if acodec != "none" and vcodec == "none":
                    out_path = os.path.join(self.download_dir.get(), f"{title}.{ext}")
                    with YoutubeDL({'format': format_id, 'outtmpl': out_path, 'quiet': True, 'progress_hooks': [self._on_progress]}) as ydl:
                        ydl.download([video_url])

                elif acodec != "none" and vcodec != "none":
                    out_path = os.path.join(self.download_dir.get(), f"{title}.mp4")
                    with YoutubeDL({'format': f"{format_id}+bestaudio/best", 'outtmpl': out_path, 'merge_output_format': 'mp4', 'quiet': True, 'progress_hooks': [self._on_progress]}) as ydl:
                        ydl.download([video_url])

                elif vcodec != "none" and acodec == "none":
                    audio_streams = [f for f in info["formats"] if f.get("acodec") != "none" and f.get("vcodec") == "none"]
                    best_audio = sorted(audio_streams, key=lambda f: f.get("abr") or 0, reverse=True)[0]

                    video_path = os.path.join(self.download_dir.get(), f"{title}_video.{ext}")
                    audio_path = os.path.join(self.download_dir.get(), f"{title}_audio.{best_audio['ext']}")
                    final_path = os.path.join(self.download_dir.get(), f"{title}.mp4")

                    with YoutubeDL({'format': format_id, 'outtmpl': video_path, 'quiet': True, 'progress_hooks': [self._on_progress]}) as ydl:
                        ydl.download([video_url])
                    with YoutubeDL({'format': best_audio["format_id"], 'outtmpl': audio_path, 'quiet': True, 'progress_hooks': [self._on_progress]}) as ydl:
                        ydl.download([video_url])

                    cmd = [ffmpeg_path, "-y", "-i", video_path, "-i", audio_path, "-c", "copy", final_path]
                    subprocess.run(cmd, capture_output=True, text=True)

                    for f in (video_path, audio_path):
                        try: os.remove(f)
                        except: pass

            messagebox.showinfo("Done", f"All downloads complete!\nSaved to: {self.download_dir.get()}")

        except Exception as e:
            messagebox.showerror("Download Failed", str(e))
        self._set_loading(False)

    def _on_progress(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            if total:
                pct = (d['downloaded_bytes'] / total) * 100
                self.progress_bar.config(mode='determinate')
                self.progress_bar['value'] = pct
                self.percent_label.config(text=f"{pct:.1f}%")
        elif d['status'] == 'finished':
            self.progress_bar.config(mode='indeterminate')
            self.progress_bar.start(10)
            self.percent_label.config(text="Processing...")

if __name__ == "__main__":
    SocialSnapApp().mainloop()
