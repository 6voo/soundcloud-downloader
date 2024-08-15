import os
import sys
import requests
import youtube_dl
from colorama import Fore, init
from bs4 import BeautifulSoup
from pathlib import Path

init(autoreset=True)

def download_image(url, download_name):
    response = requests.get(url)
    downloads_path = Path.home() / "Downloads"
    file_path = downloads_path / download_name

    with open(file_path, 'wb') as file:
        file.write(response.content)
        
def get_save_type():
    save_type = int(input(Fore.LIGHTCYAN_EX + "\nSave image as... \n[1] JPG\n[2] PNG\n[3] PDF\n> " + Fore.WHITE))
    match save_type:
        case 1:
            save_type = ".jpg"
            print(Fore.GREEN + "[!] Save type set to ", save_type)
            return save_type
        case 2:
            save_type = ".png"
            print(Fore.GREEN + "[!] Save type set to ", save_type)
            return save_type
        case 3:
            save_type = ".pdf"
            print(Fore.GREEN + "[!] Save type set to ", save_type)
            return save_type
        case _:
            save_type = ".jpg"
            print(Fore.YELLOW + "[!] Save type set to '.jpg' as default.")
            return save_type

# If the name isn't cleaned, downloading it will result in an error        
def clean_name(name):
    banned_characters = ["\\", "/", ":", "*", "?", "<", ">", "|"]
    
    for char in banned_characters:
        name = name.replace(char, "")
        
    return name  

# Download the image from the Soundcloud Url
def download_soundcloud_image(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Find's the "img" tag in html
    image = soup.find('img')  
    
    # If the tag is found, it grabs the source and image name (alt)
    # Then proceeds to download it
    if image:
        image_source = image['src']
        # image_name = image['alt'] -- NOTE: Not needed as image name will use the same name as the audio name
        image_name = filename.split('.')[:-1]
        image_name = "".join(image_name)
        # Printing out image details
        print(Fore.YELLOW + "\nImage source: ", Fore.WHITE + image_source, Fore.YELLOW + "\nImage name: ", Fore.WHITE + image_name)
        # Get file type to save image as, then add that to image name then download
        save_type = get_save_type()
        image_name = "".join(image_name)
        image_name = f"{image_name}{save_type}"
        
        print(Fore.YELLOW + f"\nDownloading image as {image_name}...")
        
        try:
            download_image(image_source, image_name)
            print(Fore.GREEN + "Image download successful! Check your Downloads path.")
        except Exception as e:
            print(Fore.RED + f"Error: {e}")

    else:
        print(Fore.RED + "Image not found.")    
        
filename = None       
def hook(d):
    global filename
    if d['status'] == 'finished':
        filename = d['filename']
                    
def download_soundcloud_audio(url):
    downloads_path = Path.home() / "Downloads"
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
    
    # -- NOTE: Error turned out to be not that the file deleted itself,
    # But that the audio file's date was set to a long time ago, so it 
    # Was grouped differently
    try:
        print(Fore.YELLOW + f"Downloading to: {str(ydl_options['outtmpl']).split('%')[0]}")
        print(Fore.YELLOW + "Downloading audio...")

    # To not print the error
        with youtube_dl.YoutubeDL(ydl_options) as ydl:
            #full_path = Path(filename)

            try:
                #os.utime(full_path, None)
                ydl.download([url]) # The actual download function. The surrounding ones are decorative.
                
            except Exception as e:
                print(Fore.RED + f"Error while downloading: {e}")
                return
        print(Fore.GREEN + "Audio download successful!")
        print(Fore.GREEN + f"Downloaded file as {filename}")
    except Exception as e:
        print(Fore.RED + f"Error: {e}")

def main():
    url = input(Fore.LIGHTCYAN_EX + "Enter Soundcloud URL\n> " + Fore.WHITE)

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    if response.status_code == 200:
        download_soundcloud_audio(url)
        download_soundcloud_image(url)
    else:
        print(Fore.RED + "Failed to retrieve page.")
        
if __name__ == "__main__":
    main()