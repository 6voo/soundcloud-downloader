import requests
from colorama import Fore, init
from bs4 import BeautifulSoup

init(autoreset=True)
    
def download_image(url, download_name):
    response = requests.get(url)
    
    with open(download_name, 'wb') as file:
        file.write(response.content)
    

url = input(Fore.CYAN + "Enter Soundcloud URL\n> " + Fore.WHITE)

response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

if response.status_code == 200:
    # Find's the "img" tag in html
    image = soup.find('img')  
    
    # If the tag is found, it grabs the source and image name (alt)
    # Then proceeds to download it
    if image:
        image_source = image['src']
        image_name = image['alt'] + ".jpg"
        
        # Printing out image details
        print(Fore.YELLOW + "Image source: ", Fore.WHITE + image_source, Fore.YELLOW + "\nImage name: ", Fore.WHITE + image_name)
        
        save_type = input(Fore.CYAN + "Save image as... (.jpg, .png)\n> " + Fore.WHITE)
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