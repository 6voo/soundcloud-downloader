import os
import re
import json
import requests
import youtube_dl
from pathlib import Path
from bs4 import BeautifulSoup
from colorama import Fore, init
from mutagen.id3 import ID3, WOAR, ID3NoHeaderError, TIT2
from mutagen.mp3 import MP3
import logger

init(autoreset=True)

# [*] for general logs
# [>] for process updates
# [~] for status changes
# [!] for errors or issues
# [+] for successes or completions

# using this instead of print() so it's easeir to remove redundancies from gui.py

def log_output(string: str, tagName: str = "default"):
    try:
        import tkinter as tk

        root = tk._default_root
        if root and hasattr(root, 'winfo_exists'):
            # this is a fallback, it shouldnt be called.
            print(f"[GUI] {string}")
            return
    except:
        pass
    
    if tagName == "good":
        print(Fore.GREEN + string)
    elif tagName == "ok":
        print(Fore.YELLOW + string)
    elif tagName == "bad":
        print(Fore.RED + string)
    elif tagName == "default":
        print(Fore.WHITE + string)
    else:
        print(string)

# Loading the JSON file for configuration
JSON_PASTEBIN = "https://pastebin.com/raw/vKJGU70z" 

def load_config():
    try:
        with open("config.json", "r") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        # Grab the contents of the Pastebin link and overwrite it with the defaults
        logger.log_output("[!] Error decoding config.json", "bad")
        logger.log_output("[~] Fixing config.json", "ok")
        
        try:
            response = requests.get(JSON_PASTEBIN)
        except Exception as e:
            logger.log_output(f"[!] ERROR WHILE GETTING CONFIG.JSON: {e}", "bad")

        if response.status_code == 200:
            default_json_file = response.json()
            logger.log_output("[+] Successfully fetched config.json", "good")
            logger.log_output("[~] Writing to config.json", "ok")
            
            with open("config.json", "w") as file:
                json.dump(default_json_file, file, indent=4)

            logger.log_output("[+] Successfully finished writing to config.json", "good")
    except FileNotFoundError:
        # Download config.json if file is not found
        logger.log_output("[!] File config.json not found.", "bad")
        logger.log_output("[~] Creating config.json...", "ok")
        
        try:
            response = requests.get(JSON_PASTEBIN) 
        except Exception as e:
            logger.log_output(f"[!] ERROR WHILE GETTING CONFIG.JSON: {e}", "bad")
            
        if response.status_code == 200:
            default_json_file = response.text
            logger.log_output("[+] Successfully fetched config.json", "good")
            logger.log_output("[~] Writing to config.json", "ok")
            
            with open("config.json", "w") as file:
                json.dump(default_json_file, file, indent=4)
                                
            logger.log_output("[+] Successfully created config.json", "good")

load_config()

f = open("config.json")        
data = json.load(f)

default_image_type = data["default_image_type"]
download_sc_image = data["download_image"]
download_sc_audio = data["download_audio"]
custom_dir_toggle = data["custom_directory_toggled"]
custom_dir = data["custom_directory"]
edit_metadata = data["edit_metadata"]

# Turn it into a valid path so we can actually use it
custom_dir = Path(custom_dir)
    
# Download image linked to Soundcloud audio 
def download_image(url, download_name):
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
                logger.log_output(f"[~] Save type set to {save_type} as default.", "ok")
                return save_type
            
    save_type = int(input(Fore.LIGHTCYAN_EX + "\nSave image as... \n[1] JPG\n[2] PNG\n[3] PDF\n> " + Fore.WHITE))
    
    match save_type:
        case 1: save_type = ".jpg"
        case 2: save_type = ".png"
        case 3: save_type = ".pdf"
        case _: 
            save_type = ".jpg"
            logger.log_output("[~] No valid save type! Setting safe type to '.jpg' as default.", "ok")
    
    logger.log_output(f"[~] Save type set to {save_type}", "good")
    return save_type

# If the name isn't cleaned, downloading it will result in an error        <- never used this?
# simplified to use regex
def clean_name(name):
    return re.sub(r'[\\/:*?<>|]', '', name)

def validate_url(url):
    if url.startswith("https://"):
        url = url[8:]
    if url.startswith("http://"):
        url = url[7:]     
        
    if url.startswith("soundcloud.com"):
        pass
    elif url.startswith("m.soundcloud.com"):
        url = "soundcloud.com"
        pass
    else:
        logger.log_output("[!] Please check the URL and try again.", "bad")
        return False
    
    url = "https://" + url
    url = url.split('?')[0] 
    logger.log_output(f"[~] Final URL: {url}", "ok")
    return url

# Download the image from the Soundcloud Url
def download_soundcloud_image(url):
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
                logger.log_output("[!] Error while getting image name. Image name set to 'image'.", "bad")
                image_name = "image"
            
        logger.log_output(f"\n[*] Image source: {image_source}", "ok") 
        # Get file type to save image as, then add that to image name then download
        save_type = get_save_type()
        image_name = "".join(image_name)
        image_name = f"{image_name}{save_type}"
        
        logger.log_output(f"\n[>] Downloading image to {image_name}", "ok")
        logger.log_output("[>] Downloading image...", "ok") 
               
        try:
            download_image(image_source, image_name)
            logger.log_output("[+] Image download successful!", "good") 
        except Exception as e:
            logger.log_output(f"[!] Error: {e}", "bad")

    else:
        logger.log_output("[!] Error: Image not found.", "bad")    
        
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
        logger.log_output(f"[>] Downloading to: {str(ydl_options['outtmpl']).split('%')[0]}", "ok")
        logger.log_output("[>] Downloading audio...", "ok")

    # To not print the error
        with youtube_dl.YoutubeDL(ydl_options) as ydl:
            try:
                ydl.download([url]) # The actual download function. The surrounding ones are decorative.
            except Exception as e:
                logger.log_output(f"[!] Error while downloading: {e}", "bad")
                return
            
        logger.log_output("[+] Audio download successful!", "good")
        logger.log_output(f"[+] Downloaded audio to '{filename}'", "good")
        
    except Exception as e:
        logger.log_output(f"[!] Error: {e}", "bad")
        
def check_custom_dir():
    # Returns if custom directory toggle is off
    if not custom_dir_toggle:
        return 0
            
    dir_exists = os.path.exists(custom_dir)
    
    # If directory exists, it passes through, else, it returns 303 (Error code for missing file path)
    if dir_exists:
        return 0
    else:
        return 303
    
def main():
    url = input(Fore.LIGHTCYAN_EX + "Enter Soundcloud URL\n> " + Fore.WHITE)
    final_url = validate_url(url)
    
    # Returns if the URL isn't valid or not SoundCloud's URL
    if not final_url:
        return

    # Returns if they have both download_image and download_audio as false
    if not download_sc_audio and not download_sc_image:
        logger.log_output("[!] You have both 'download image' and 'download audio' toggled off. Please toggle at least one then try again.", "bad")
        return

    # Checks if it has custom directory toggled
    # Then checks if the custom directory exists    
    if custom_dir_toggle:
        logger.log_output(f"[>] Checking directory: {str(custom_dir)}", "ok")
    elif custom_dir_toggle and custom_dir == "":
        logger.log_output("[!] Custom directory has been set to current directory automatically. Did you leave 'custom_directory' blank?", "ok")
    else:
        logger.log_output(f"[>] Checking directory: {str(downloads_path)}", "ok")

    file_path_error_code = check_custom_dir()
    if file_path_error_code == 303:
        logger.log_output(f"[!] ERROR CODE 303: Directory {str(custom_dir)} does not exist.", "bad")
        return
    else:
        logger.log_output("[+] Directory exists. Continuing download process.", "good")
        
        
    response = requests.get(final_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Downloading the audio and image
    if response.status_code == 200:
        download_soundcloud_audio(final_url)
        download_soundcloud_image(final_url)
        
        # Edit the metadata
        audio_path = rf'{filename}'
        logger.log_output(f"[*] Audio path: {audio_path}", "default")

        if edit_metadata:
            try:
                audio = MP3(audio_path, ID3=ID3)
            except ID3NoHeaderError:
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
                    logger.log_output("[+] Successfully edited metadata audio origin to url.", "good")
                except:
                    logger.log_output("[!] Minor error, could not edit audio origin to url.", "ok")
                    
                try:
                    audio.tags.add(TIT2(encoding=3, text=audio_title))
                    logger.log_output("[+] Successfully edited metadata audio title to title.", "good")
                except:
                    logger.log_output("[!] Minor error, could not edit metadata audio title to title.", "ok")    
                    
                audio.save()
                logger.log_output("[+] Successfully edited metadata", "good")
            except Exception as e:
                logger.log_output(f"[!] Error: {e}", "bad")
                logger.log_output("[!] Failed to edit metadata.", "bad")
    else:
        logger.log_output("[!] Failed to retrieve page.", "bad")
        
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.log_output(f"[!] Error: {e}", "bad")
        
    logger.log_output("[*] Press ENTER to close program.", "default")
    input()