import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pytube import YouTube, Playlist
from threading import Thread
import pyperclip
import os
from ttkthemes import ThemedStyle
import time

def download_video():
    url = url_entry.get()
    if url:
        quality = quality_var.get()
        save_path = save_path_var.get()
        if save_path:
            status_label.config(text="Downloading...", foreground="white")
            thread = Thread(target=download_video_thread, args=(url, quality, save_path))
            thread.start()
        else:
            status_label.config(text="Please select a save location", foreground="red")
    else:
        status_label.config(text="Please enter a valid URL", foreground="red")

def download_video_thread(url, quality, save_path):
    try:
        start_time = time.time()
        def on_progress(stream, chunk, remaining):
            nonlocal start_time
            file_size = stream.filesize
            bytes_downloaded = file_size - remaining
            elapsed_time = time.time() - start_time
            download_speed = bytes_downloaded / elapsed_time
            speed_label.config(text=f"Download Speed: {download_speed/1024:.2f} KB/s")
            update_progress(stream, chunk, remaining)
            
        yt = YouTube(url, on_progress_callback=on_progress)
        video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        video_path = os.path.join(save_path, f"{yt.title}.mp4")
        video.download(save_path)
        status_label.config(text="Video downloaded successfully!", foreground="green")
        update_download_list(yt.title, video_path)
        if convert_var.get():
            convert_to_audio(video_path)
    except Exception as e:
        status_label.config(text=f"An error occurred: {e}", foreground="red")

def update_progress(stream, chunk, remaining):
    file_size = stream.filesize
    bytes_downloaded = file_size - remaining
    percentage = (bytes_downloaded / file_size) * 100
    status_label.config(text=f"Downloading... {percentage:.1f}% complete", foreground="white")

def download_playlist():
    url = url_entry.get()
    if url:
        status_label.config(text="Downloading playlist...", foreground="white")
        thread = Thread(target=download_playlist_thread, args=(url,))
        thread.start()
    else:
        status_label.config(text="Please enter a valid URL", foreground="red")

def download_playlist_thread(url):
    try:
        start_time = time.time()
        def on_progress(stream, chunk, remaining):
            nonlocal start_time
            file_size = stream.filesize
            bytes_downloaded = file_size - remaining
            elapsed_time = time.time() - start_time
            download_speed = bytes_downloaded / elapsed_time
            speed_label.config(text=f"Download Speed: {download_speed/1024:.2f} KB/s")
            update_progress(stream, chunk, remaining)
            
        playlist = Playlist(url)
        save_path = save_path_var.get()
        for video_url in playlist.video_urls:
            yt = YouTube(video_url, on_progress_callback=on_progress)
            video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            video_path = os.path.join(save_path, f"{yt.title}.mp4")
            video.download(save_path)
            update_download_list(yt.title, video_path)
            if convert_var.get():
                convert_to_audio(video_path)
        status_label.config(text="Playlist downloaded successfully!", foreground="green")
    except Exception as e:
        status_label.config(text=f"An error occurred: {e}", foreground="red")

def browse_save_location():
    save_path = filedialog.askdirectory()
    save_path_var.set(save_path)

def clear_fields():
    url_entry.delete(0, tk.END)
    quality_var.set("Best")
    save_path_var.set("")
    status_label.config(text="", foreground="white")

def open_folder():
    save_path = save_path_var.get()
    if save_path:
        os.startfile(save_path)

def pause_resume_download():
    # Implement pause/resume functionality here
    pass

def cancel_download():
    # Implement cancel download functionality here
    pass

def copy_url():
    url = url_entry.get()
    if url:
        pyperclip.copy(url)
        messagebox.showinfo("URL Copied", "The URL has been copied to the clipboard.")

def update_download_list(title, path):
    download_listbox.insert(tk.END, f"{title} - {path}")

def convert_to_audio(video_path):
    try:
        import moviepy.editor as mp
        audio_path = os.path.splitext(video_path)[0] + f".{audio_format_var.get()}"
        video_clip = mp.VideoFileClip(video_path)
        audio_clip = video_clip.audio
        audio_clip.write_audiofile(audio_path)
        audio_clip.close()
        video_clip.close()
    except Exception as e:
        status_label.config(text=f"Error converting video to audio: {e}", foreground="red")

def change_theme(event):
    selected_theme = theme_var.get()
    style.set_theme(selected_theme)

root = tk.Tk()
root.title("YouTube Downloader")
root.geometry("800x500")
root.configure(bg="#212121")  # Dark background color

# Themed Style
style = ThemedStyle(root)

# Available Themes
available_themes = style.theme_names()

# Creator Label
creator_label = ttk.Label(root, text="Created by: RAKIB", font=('Helvetica', 10, 'italic'), background='#212121', foreground='#FFA726')
creator_label.grid(row=0, column=0, columnspan=3, pady=5)

# Theme Selection
theme_label = ttk.Label(root, text="Select Theme:")
theme_label.grid(row=1, column=0, padx=10, pady=5)
theme_var = tk.StringVar(value=available_themes[0])
theme_menu = ttk.OptionMenu(root, theme_var, *available_themes, command=change_theme)
theme_menu.grid(row=1, column=1, padx=10, pady=5)

# URL Entry
url_label = ttk.Label(root, text="Enter YouTube URL:")
url_label.grid(row=2, column=0, padx=10, pady=10)
url_entry = ttk.Entry(root, width=40)
url_entry.grid(row=2, column=1, padx=10, pady=10)

# Quality Selection
quality_label = ttk.Label(root, text="Select Video Quality:")
quality_label.grid(row=3, column=0, padx=10, pady=5)
quality_var = tk.StringVar(value="Best")
quality_menu = ttk.OptionMenu(root, quality_var, "Best", "720p", "480p", "360p", "240p", "144p")
quality_menu.grid(row=3, column=1, padx=10, pady=5)

# Save Location
save_path_var = tk.StringVar()
save_path_label = ttk.Label(root, text="Select Save Location:")
save_path_label.grid(row=4, column=0, padx=10, pady=5)
save_path_entry = ttk.Entry(root, textvariable=save_path_var, width=30)
save_path_entry.grid(row=4, column=1, padx=10, pady=5)
browse_button = ttk.Button(root, text="Browse", command=browse_save_location)
browse_button.grid(row=4, column=2, padx=5, pady=5)

# Download Buttons
download_video_button = ttk.Button(root, text="Download Video", command=download_video)
download_video_button.grid(row=5, column=0, padx=10, pady=5)
download_playlist_button = ttk.Button(root, text="Download Playlist", command=download_playlist)
download_playlist_button.grid(row=5, column=1, padx=10, pady=5)

# Additional Buttons
clear_fields_button = ttk.Button(root, text="Clear Fields", command=clear_fields)
clear_fields_button.grid(row=6, column=0, padx=10, pady=5)
open_folder_button = ttk.Button(root, text="Open Folder", command=open_folder)
open_folder_button.grid(row=6, column=1, padx=10, pady=5)
pause_resume_button = ttk.Button(root, text="Pause/Resume", command=pause_resume_download)
pause_resume_button.grid(row=7, column=0, padx=10, pady=5)
cancel_button = ttk.Button(root, text="Cancel", command=cancel_download)
cancel_button.grid(row=7, column=1, padx=10, pady=5)
copy_url_button = ttk.Button(root, text="Copy URL", command=copy_url)
copy_url_button.grid(row=8, column=0, columnspan=2, padx=10, pady=5)

# Convert to Audio Checkbox
convert_var = tk.BooleanVar()
convert_checkbox = ttk.Checkbutton(root, text="Convert to Audio", variable=convert_var)
convert_checkbox.grid(row=9, column=0, columnspan=2, padx=10, pady=5)

# Audio Format Selection
audio_format_label = ttk.Label(root, text="Select Audio Format:")
audio_format_label.grid(row=10, column=0, padx=10, pady=5)
audio_format_var = tk.StringVar(value="mp3")
audio_format_menu = ttk.OptionMenu(root, audio_format_var, "mp3", "wav", "ogg")
audio_format_menu.grid(row=10, column=1, padx=10, pady=5)

# Download Listbox
download_listbox = tk.Listbox(root, width=80, height=15)
download_listbox.grid(row=11, column=0, columnspan=3, padx=10, pady=10)

# Status Label
status_label = ttk.Label(root, text="", foreground="white", background="#212121")
status_label.grid(row=12, column=0, columnspan=3, pady=10)

# Download Speed Label
speed_label = ttk.Label(root, text="", foreground="white", background="#212121")
speed_label.grid(row=13, column=0, columnspan=3, pady=10)

root.mainloop()
