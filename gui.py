import main
import json
import tkinter as tk
from tkinter import ttk

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

# Create a button to download
download_button = ttk.Button(frame, text='Download')
download_button.grid(column=2, row=0, sticky='W', **options)
download_button.configure(command=lambda: main.download_soundcloud_audio(main.validate_url(url.get()))) # Validates url then passes it to download

# Basics now, implement logging later

if __name__ == "__main__":
    frame.grid(padx=10, pady=10)
    root.mainloop()