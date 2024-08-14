import requests
import urllib.request
from bs4 import BeautifulSoup

    
def download_image(url, download_name):
    response = requests.get(url)
    
    with open(download_name, 'wb') as file:
        file.write(response.content)
    

url = input("Enter Soundcloud URL: ")
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

if response.status_code == 200:
    image = soup.find('img')  
    if image:
        image_source = image['src']
        image_name = image['alt'] + ".jpg"
        print("Image source: ", image_source, "\nImage name: ", image_name)
        print("Downloading...")
        try:
            download_image(image_source, image_name)
            print('Download successful!')
        except Exception as e:
            print(f"Error: {e}")

    else:
        print("Image not found.")
else:
    print("Failed to retrieve page.")