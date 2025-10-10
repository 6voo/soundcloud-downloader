import main
import json
import requests
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from threading import Thread
from mutagen.id3 import ID3, WOAR, ID3NoHeaderError, TIT2
from mutagen.mp3 import MP3
from main import validate_url, download_soundcloud_image, download_soundcloud_audio, load_config, main
import logger

# Load config file
load_config()

f = open('config.json')
data = json.load(f)

default_image_type = data["default_image_type"]
download_sc_image = data["download_image"]
download_sc_audio = data["download_audio"]
custom_dir_toggle = data["custom_directory_toggled"]
custom_dir = data["custom_directory"]
edit_metadata = data["edit_metadata"]        

## ------------------------                  GUI              ------------------- ##

root = tk.Tk()
root.title("Soundcloud Downloader")
root.geometry('550x300')
root.resizable(False, False)

frame = ttk.Frame(root)
options = {'padx': 5, 'pady': 5}

# Create a box for input
url_label = ttk.Label(frame, text='Enter URL:')
url_label.grid(column=0, row=0, sticky='W', **options)

url = tk.StringVar()
url_entry = ttk.Entry(frame, textvariable=url, width=60) # Width is 60 fixed chars, work on reactivity later
url_entry.grid(column=1, row=0)
url_entry.size()
url_entry.focus()

# Logging Panel
logs_label = ttk.Label(frame, text="Output Logs")
logs_label.config(font=("Courier", 9))
logs_label.grid(row=1, column=0)

logs = tk.Text(frame, height=13, width=65)
logs.configure(state="disabled")
logs.grid(row=2, column=0, columnspan=3, sticky='W')

logs.tag_configure(tagName="good", foreground="green")
logs.tag_configure(tagName="ok", foreground="yellow")
logs.tag_configure(tagName="bad", foreground="red")
logs.tag_configure(tagName="default", foreground="black")

def log_output(string: str, tagName: str = "default"):
    def update_log():
        logs.configure(state="normal")
        start_index = logs.index("end-1c") if logs.get("1.0", "end-1c") != "" else logs.index("1.0")
        
        logs.insert(start_index, string + "\n")
        
        end_index = logs.index(f"{start_index} + {len(string)}c")
        logs.tag_add(tagName, start_index, end_index)
        logs.configure(state="disabled")
        
    root.after(0, update_log)

# telling main.log_output to use the tkinter version of our function (otherwise it would print everything!)
logger.log_output = log_output

## ------------------------        DOWNLOAD FUNCTIONS        ------------------- ##
custom_dir = Path(custom_dir)    
filename = None       
                                     
downloads_path = Path.home() / "Downloads"

## ------------------------------------------------------------------------------ ##


## Main Function
def main_function(url):
    final_url = validate_url(url)
    
    # Returns if the URL isn't valid or not SoundCloud's URL
    if not final_url:
        return
    
    # Returns if they have both download_image and download_audio as false
    if not download_sc_audio and not download_sc_image:
        log_output("[!] You have both 'download image' and 'download audio' toggled off. Please toggle at least one then try again.", "bad")
        return

    response = requests.get(final_url)
    
    # Downloading the audio and image
    if response.status_code == 200:
        download_soundcloud_audio(final_url)
        download_soundcloud_image(final_url)

        audio_path = rf'{filename}'
        if audio_path == None: 
            audio_path = filename
        log_output(f"[*] Audio path: {audio_path}", "default")
       

            
        # Edit the metadata
        if edit_metadata:
            try:
                audio = MP3(audio_path, ID3=ID3)
            except:
                audio = MP3(audio_path)
                audio.add_tags()
                audio = MP3(audio_path, ID3=ID3)

            if audio.tags is None:
                audio.add_tags() 
            try:
                audio_name = filename.split("\\")[-1]
                audio_title = "".join(audio_name.split(".")[:1])
                
                try:
                    audio.tags.add(WOAR(encoding=3, url=final_url))
                    log_output("[+] Successfully edited metadata audio origin to url.", "good")
                except:
                    log_output("[!] Minor error, could not edit audio origin to url.", "ok")
                    
                try:
                    audio.tags.add(TIT2(encoding=3, text=audio_title))
                    log_output("[+] Successfully edited metadata audio title to title.", "good")
                except:
                    log_output("[!] Minor error, could not edit metadata audio title to title.", "ok")    
                    
                audio.save()
                log_output("[+] Successfully edited metadata", "good")
            except Exception as e:
                log_output(f"[!] Error: {e}", "bad")
                log_output("[!] Failed to edit metadata.", "bad")
    else:
        log_output("[!] Failed to retrieve page.", "bad")

def threaded_download():
    download_button.configure(state="disabled")
    url_value = url.get()
    
    def run():
        try: 
            main_function(url_value)
        finally:
            root.after(0, lambda: download_button.configure(state="normal"))
            
    thread = Thread(target=run, daemon=True)
    thread.start()
                
# Create a button to download
download_button = ttk.Button(frame, text='Download')
download_button.grid(column=2, row=0, sticky='W', **options)
download_button.configure(command=threaded_download) # Validates url then passes it to download

if __name__ == "__main__":
    frame.grid(padx=10, pady=10)
    root.mainloop()