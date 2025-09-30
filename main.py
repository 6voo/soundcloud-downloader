import os
import json
import requests
import youtube_dl
from pathlib import Path
from bs4 import BeautifulSoup
from colorama import Fore, init
from mutagen.id3 import ID3, WOAR, ID3NoHeaderError, TIT2
from mutagen.mp3 import MP3

init(autoreset=True)

# [*] for general logs
# [>] for process updates
# [~] for status changes
# [!] for errors or issues
# [+] for successes or completions

# Loading the JSON file for configuration
JSON_PASTEBIN = "https://pastebin.com/raw/vKJGU70z" # config.json in pastebin

try:
    with open("config.json", "r") as f:
        data = json.load(f)
except json.JSONDecodeError:
     # Grab the contents of the Pastebin link and overwrite it with the defaults
    print(Fore.RED + "[!] Error decoding " + Fore.WHITE + "config.json")
    print(Fore.YELLOW + "[~] Fixing " + Fore.WHITE + "config.json")
    
    try:
        response = requests.get(JSON_PASTEBIN)
    except Exception as e:
        print(Fore.RED + f"[!] ERROR WHILE GETTING CONFIG.JSON: {e}")

    if response.status_code == 200:
        default_json_file = response.json()
        print(Fore.GREEN + "[+] Successfully fetched " + Fore.WHITE + "config.json")
        print(Fore.YELLOW + "[~] Writing to " + Fore.WHITE + "config.json")
        
        with open("config.json", "w") as file:
            json.dump(default_json_file, file, indent=4)

        print(Fore.GREEN + "[+] Successfully finished writing to " + Fore.WHITE + "config.json")
except FileNotFoundError:
    # Download config.json if file is not found
    print(Fore.RED + "[!] File " + Fore.WHITE + "config.json" + Fore.RED + " not found.")
    print(Fore.YELLOW + "[~] Creating " + Fore.WHITE + "config.json" + Fore.YELLOW + "...")
    
    try:
        response = requests.get(JSON_PASTEBIN) # config.json in pastebin
    except Exception as e:
        print(Fore.RED + f"[!] ERROR WHILE GETTING CONFIG.JSON: {e}")
        
    if response.status_code == 200:
        default_json_file = response.text
        print(Fore.GREEN + "[+] Successfully fetched " + Fore.WHITE + "config.json")
        print(Fore.YELLOW + "[~] Writing to " + Fore.WHITE + "config.json")
        
        with open("config.json", "w") as file:
            json.dump(default_json_file, file, indent=4)
                            
        print(Fore.GREEN + "[+] Successfully created " + Fore.WHITE + "config.json")


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
    
# NOTE: -- THIS FUNCTION IS USELESS <- Dear past me, from what I see, it is indeed useful. Ignored.
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
                print(Fore.YELLOW + "[~] Save type set to " + Fore.WHITE + save_type + Fore.YELLOW + " as default.")
                return save_type
            
    save_type = int(input(Fore.LIGHTCYAN_EX + "\nSave image as... \n[1] JPG\n[2] PNG\n[3] PDF\n> " + Fore.WHITE))
    
    match save_type:
        case 1: save_type = ".jpg"
        case 2: save_type = ".png"
        case 3: save_type = ".pdf"
        case _: 
            save_type = ".jpg"
            print(Fore.YELLOW + "[~] No valid save type! Setting safe type to " + Fore.WHITE + "'.jpg'" + Fore.YELLOW +  " as default.")
    
    print(Fore.GREEN + "[~] Save type set to ", save_type)
    return save_type

# If the name isn't cleaned, downloading it will result in an error        
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
        print(Fore.RED + "[!] Please check the URL and try again. ")
        return False
    
    url = "https://" + url
    url = url.split('?')[0] 
    print(Fore.YELLOW + "[~] Final URL: " + url)
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
                print(Fore.RED + "[!] Error while getting image name. Image name set to \'image\'.")
                image_name = "image"
            
        print(Fore.YELLOW + "\n[*] Image source: " + Fore.WHITE + image_source) 
        # Get file type to save image as, then add that to image name then download
        save_type = get_save_type()
        image_name = "".join(image_name)
        image_name = f"{image_name}{save_type}"
        
        print(Fore.YELLOW + f"\n[>] Downloading image to {image_name}")
        print(Fore.YELLOW + "[>] Downloading image...") 
               
        try:
            download_image(image_source, image_name)
            print(Fore.GREEN + "[+] Image download successful!") 
        except Exception as e:
            print(Fore.RED + f"[!] Error: {e}")

    else:
        print(Fore.RED + "[!] Error: Image not found.")    
        
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
        print(Fore.YELLOW + f"[>] Downloading to: {str(ydl_options['outtmpl']).split('%')[0]}")
        print(Fore.YELLOW + "[>] Downloading audio...")

    # To not print the error
        with youtube_dl.YoutubeDL(ydl_options) as ydl:
            try:
                ydl.download([url]) # The actual download function. The surrounding ones are decorative.
            except Exception as e:
                print(Fore.RED + f"[!] Error while downloading: {e}")
                return
            
        print(Fore.GREEN + "[+] Audio download successful!")
        print(Fore.GREEN + "[+] Downloaded audio to " + Fore.WHITE + f"{filename}")
        
    except Exception as e:
        print(Fore.RED + f"[!] Error: {e}")
        
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
        print(Fore.RED + "[!] You have both 'download image' and 'download audio' toggled off. Please toggle at least one then try again.")
        return

    # Checks if it has custom directory toggled
    # Then checks if the custom directory exists    
    if custom_dir_toggle:
        print(Fore.YELLOW + "[>] Checking directory:", Fore.WHITE + str(custom_dir))
    elif custom_dir_toggle and custom_dir == "":
        print(Fore.YELLOW + "[!] Custom directory has been set to current directory automatically. Did you leave \'", Fore.WHITE, "custom_directory\'", Fore.YELLOW, "vblank?")
    else:
        print(Fore.YELLOW + "[>] Checking directory:", Fore.WHITE + str(downloads_path))

    file_path_error_code = check_custom_dir()
    if file_path_error_code == 303:
        print(Fore.RED + "[!] ERROR CODE 303: Directory", Fore.WHITE + str(custom_dir), Fore.RED + "does not exist.")
        return
    else:
        print(Fore.GREEN + "[+] Directory exists. Continuing download process.")
        
        
    response = requests.get(final_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Downloading the audio and image
    if response.status_code == 200:
        download_soundcloud_audio(final_url)
        download_soundcloud_image(final_url)
        
        # Edit the metadata
        audio_path = rf'{filename}'
        print(Fore.LIGHTCYAN_EX + f"[*] Audio path: {audio_path}")

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
                    print(Fore.GREEN + "[+] Successfully edited metadata audio origin to url.")
                except:
                    print(Fore.YELLOW + "[!] Minor error, could not edit audio origin to url.")
                    
                try:
                    audio.tags.add(TIT2(encoding=3, text=audio_title))
                    print(Fore.GREEN + "[+] Successfully edited metadata audio title to title.")
                except:
                    print(Fore.YELLOW + "[!] Minor error, could not edit metadata audio title to title.")    
                    
                audio.save()
                print(Fore.GREEN + "[+] Successfully edited metadata")
            except Exception as e:
                print(Fore.RED + f"[!] Error: {e}")
                print(Fore.RED + "[!] Failed to edit metadata.")
    else:
        print(Fore.RED + "[!] Failed to retrieve page.")
        
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(Fore.RED + f"[!] Error: {e}")
        
    print(Fore.LIGHTCYAN_EX + "[*] Press ENTER to close program.")
    input()