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
def download_soundcloud_image():
    # Find's the "img" tag in html
    image = soup.find('img')  
    
    # If the tag is found, it grabs the source and image name (alt)
    # Then proceeds to download it
    if image:
        image_source = image['src']
        image_name = image['alt'] 
        
        # Printing out image details
        print(Fore.YELLOW + "\nImage source: ", Fore.WHITE + image_source, Fore.YELLOW + "\nImage name: ", Fore.WHITE + image_name)
        # Get file type to save image as, then add that to image name then download
        save_type = get_save_type()
        image_name = clean_name(image_name) + save_type
        
        print(Fore.YELLOW + "\nDownloading image...")
        
        try:
            download_image(image_source, image_name)
            print(Fore.GREEN + "Image download successful! Check your Downloads path.")
        except Exception as e:
            print(Fore.RED + f"Error: {e}")

    else:
        print(Fore.RED + "Image not found.")    
        
            
def download_soundcloud_audio(url):
          
    downloads_path = Path.home() / "Downloads"
    downloads_path.mkdir(parents=True, exist_ok=True)
    # Set the options for youtube_dl
    ydl_options = {
        'format': 'bestaudio/best',  # Download best audio quality
        # Suppress any output or warnings for clean look
        'quiet': True,
        'no_warnings': True
        #'outtmpl': downloads_path / f"{image_name}.mp3"
    }
    
    try:
        #print(Fore.YELLOW + f"Downloading to: {ydl_options['outtmpl']}")
        print(Fore.YELLOW + "Downloading audio...")

    # To not print the error
        with youtube_dl.YoutubeDL(ydl_options) as ydl:
            try:
                ydl.download([url]) # The actual download function. The surrounding ones are decorative.
            except Exception as e:
                pass
        print(Fore.GREEN + "Audio download successful!")
    except Exception as e:
        print(Fore.RED + f"Error: {e}")

url = input(Fore.LIGHTCYAN_EX + "Enter Soundcloud URL\n> " + Fore.WHITE)

response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

if response.status_code == 200:
    #download_soundcloud_image()
    download_soundcloud_audio(url)
else:
    print(Fore.RED + "Failed to retrieve page.")