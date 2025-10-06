import main
import json
import requests
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import os
import json
import requests
import youtube_dl
from pathlib import Path
from bs4 import BeautifulSoup
from mutagen.id3 import ID3, WOAR, ID3NoHeaderError, TIT2
from mutagen.mp3 import MP3


# Load config file
main.load_config()

f = open('config.json')
data = json.load(f)

default_image_type = data["default_image_type"]
download_sc_image = data["download_image"]
download_sc_audio = data["download_audio"]
custom_dir_toggle = data["custom_directory_toggled"]
custom_dir = data["custom_directory"]
edit_metadata = data["edit_metadata"]        

## GUI
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

#
def log_output(string: str, tagName: str):
    logs.configure(state="normal")
    start_index = logs.index("end-1c") if logs.get("1.0", "end-1c") != "" else logs.index("1.0")
    
    logs.insert(start_index, string + "\n")
    
    end_index = logs.index(f"{start_index} + {len(string)}c")
    logs.tag_add(tagName, start_index, end_index)
    logs.configure(state="disabled")

## ------------------------ DOWNLOAD FUNCTIONS ------------------- ##
custom_dir = Path(custom_dir)
    
def download_image(url, download_name):
    # Checks if they toggled the download image function, leaves if untoggled
    if not download_sc_image:
        return
    
    response = requests.get(url)
    downloads_path = Path.home() / "Downloads"
    
    if custom_dir_toggle:
        file_path = custom_dir / download_name
    else:
        file_path = downloads_path / download_name

    with open(file_path, 'wb') as file:
        file.write(response.content)
        
def get_save_type():
    # Checks if default image type is true in config.json
    # Then iterates through each save type, checks if valid then returns it
    if default_image_type:
        for key, value in data['image_types'].items():
            if value:
                save_type = f".{str(key)}"
                log_output(f"[~] Save type set to {save_type} as default.", "ok")
                return save_type
            
    save_type = int(input("\nSave image as... \n[1] JPG\n[2] PNG\n[3] PDF\n> "))
    
    match save_type:
        case 1: save_type = ".jpg"
        case 2: save_type = ".png"
        case 3: save_type = ".pdf"
        case _: 
            save_type = ".jpg"
            log_output("[~] No valid save type! Setting safe type to \'.jpg\' as default.")
    
    log_output(f"[~] Save type set to {save_type}", "good")
    return save_type

# If the name isn't cleaned, downloading it will result in an error        <- never used this?
def clean_name(name):
    banned_characters = ["\\", "/", ":", "*", "?", "<", ">", "|"]
    
    for char in banned_characters:
        name = name.replace(char, "")
        
    return name  

def validate_url(url):
    if url.startswith("https://"):
        url = url[8:]
    if url.startswith("http://"):
        url = url[7:]     
    
    if url.startswith("soundcloud.com"):
        pass
    elif url.startswith("soundcloud.com"):
        pass
    elif url.startswith("soundcloud.net"):
        pass
    else:
        log_output("[!] Please check the URL and try again. ")
        return False
    
    url = "https://" + url
    url = url.split('?')[0] 
    log_output(f"[~] Final URL: {url}", "good")
    return url

# Download the image from the Soundcloud Url
def download_soundcloud_image(url):
    # Checks if they toggled the download image function, leaves if untoggled
    if not download_sc_image:
        return
    
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    # Find's the "img" tag in html, which is where the image is stored (as of 2025)
    image = soup.find('img')  
    
    # If the tag is found, it grabs the source and image name (alt)
    # Then proceeds to download it
    if image:
        image_source = image['src']
        image_alt = image['alt'] 
        try:
            image_name = filename.split('.')[:-1]
            image_name = '.'.join(image_name)
        except:
            try:
                image_name = image_alt
            except:     
                # This except is the last resort if the image doesn't have an alt.
                log_output("[!] Error while getting image name. Image name set to \'image\'.")
                image_name = "image"
            
        log_output(f"\n[*] Image source: {image_source}", "ok") 
        # Get file type to save image as, then add that to image name then download
        save_type = get_save_type()
        image_name = "".join(image_name)
        image_name = f"{image_name}{save_type}"
        
        log_output(f"\n[>] Downloading image to {image_name}", "ok")
        log_output("[>] Downloading image...", "ok") 
               
        try:
            download_image(image_source, image_name)
            log_output("[+] Image download successful!", "good") 
        except Exception as e:
            log_output(f"[!] Error: {e}", "bad")

    else:
        log_output("[!] Error: Image not found.", "bad")   
    
filename = None       

def hook(d):
    global filename
    if d['status'] == 'finished':
        filename = d['filename']
                                     
downloads_path = Path.home() / "Downloads"

def download_soundcloud_audio(url):
    if not download_sc_audio:
        return
    
    # Checks if custom directory is toggled, if true then makes download path to custom
    # directory, if false it's to Downloads
    if custom_dir_toggle:
        output_template = str(custom_dir / "%(title)s.%(ext)s")
    else:
        output_template = str(downloads_path / "%(title)s.%(ext)s")

    # Set the options for youtube_dl
    ydl_options = {
        'format': 'bestaudio/best',  # Download best audio quality
        # Suppress any output or warnings for clean look
        'quiet': True,
        'no_warnings': True,
        'outtmpl': output_template,
        'progress_hooks': [hook],
        'nopart': True
    }
    
    try:
        log_output(f"[>] Downloading to: {str(ydl_options['outtmpl']).split('%')[0]}", "ok")
        log_output("[>] Downloading audio...", "ok")

    # To not print the error
        with youtube_dl.YoutubeDL(ydl_options) as ydl:
            try:
                ydl.download([url]) # The actual download function. The surrounding ones are decorative.
            except Exception as e:
                log_output(f"[!] Error while downloading: {e}", "bad")
                return
            
        log_output("[+] Audio download successful!", "good")
        log_output("[+] Downloaded audio to \'"f"{filename}\'", "good")
        
    except Exception as e:
        log_output(f"[!] Error: {e}", "bad")
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

# Create a button to download
download_button = ttk.Button(frame, text='Download')
download_button.grid(column=2, row=0, sticky='W', **options)
download_button.configure(command=lambda: main_function(url.get())) # Validates url then passes it to download

if __name__ == "__main__":
    frame.grid(padx=10, pady=10)
    root.mainloop()