import requests
from colorama import Fore, init
from bs4 import BeautifulSoup

init(autoreset=True)
    
def download_image(url, download_name):
    response = requests.get(url)
    
    with open(download_name, 'wb') as file:
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

url = input(Fore.LIGHTCYAN_EX + "Enter Soundcloud URL\n> " + Fore.WHITE)

response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

if response.status_code == 200:
    # Find's the "img" tag in html
    image = soup.find('img')  
    
    # If the tag is found, it grabs the source and image name (alt)
    # Then proceeds to download it
    if image:
        image_source = image['src']
        image_name = image['alt'] 
        
        # Printing out image details
        print(Fore.YELLOW + "Image source: ", Fore.WHITE + image_source, Fore.YELLOW + "\nImage name: ", Fore.WHITE + image_name)
        # Get file type to save image as, then add that to image name then download
        save_type = get_save_type()
        image_name = clean_name(image_name) + save_type
        
        print("Downloading...")
        
        try:
            download_image(image_source, image_name)
            print(Fore.GREEN + 'Download successful!')
        except Exception as e:
            print(Fore.RED + f"Error: {e}")

    else:
        print(Fore.RED + "Image not found.")
else:
    print(Fore.RED + "Failed to retrieve page.")