from tkinter import *
import pygame
import regex as re
from tkinter import filedialog
import shutil
from mutagen.mp3 import MP3
from mutagen.wave import WAVE
from mutagen.ogg import OggFileType
from yt_dlp import YoutubeDL
import os
from datetime import datetime
from pytube import Playlist, YouTube
import subprocess
import random
from pydub import AudioSegment
from pypresence import Presence
from pydub.silence import split_on_silence
import platform


CMD = '''
on run argv
  display notification (item 2 of argv) with title (item 1 of argv)
end run
'''
# Mac OS notification
if platform.system() == "Darwin":
    def notify(title, text):
        subprocess.call(['osascript', '-e', CMD, title, text])

#GLOBAL VARS
global timer

root = Tk()
root.title("JaxPlayer")
#root.iconbitmap("assets/icons/acorn.ico")
root.geometry("500x400")
pygame.mixer.init()

#Grab song length time info
def play_time():
    # Song lapsed time
    current_time = pygame.mixer.music.get_pos() / 1000
    
    # Convert to time format
    converted_time = datetime.utcfromtimestamp(current_time).strftime('%H:%M:%S')
    

    #Grab the song title from the playlist
    song = song_box.get(ACTIVE)
    #Add directory structure
    song = f'assets/music/{song}'
    
    #load song with mut
    song_mut = MP3(song)
    # get song length
    song_length = song_mut.info.length
    #convert to time format
    converted_song_length = datetime.utcfromtimestamp(song_length).strftime('%H:%M:%S')
    

    #Output
    status_bar.config(text=f'Song: {converted_time} of {converted_song_length}  ')
    
    # At the end of the song call the next song function
    if int(song_mut.info.length) == int(current_time) or int(song_mut.info.length) - 1 == int(current_time):
        end_of_song()
    

    
    # Update time
    status_bar.after(1000, play_time)

###DEF###
def remove_end_silence(input_folder="assets/music/"):
    # Ensure the input folder exists
    if not os.path.exists(input_folder):
        print(f"The folder '{input_folder}' does not exist.")
        return

    # Iterate through the files in the folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".mp3"):
            file_path = os.path.join(input_folder, filename)
            print(f"Processing: {file_path}")

            # Load the audio file
            audio = AudioSegment.from_mp3(file_path)

            # Split the audio based on silence
            audio_segments = split_on_silence(audio, silence_thresh=-50)

            # Combine the non-silent segments
            combined_audio = audio_segments[0]
            for segment in audio_segments[1:]:
                combined_audio += segment

            # Export the modified audio back to the file
            combined_audio.export(file_path, format="mp3")

            print(f"Processed: {file_path}")

# RPC
client_id = "1146587859726372964"
RPC = Presence(client_id)
def start_rpc():
    RPC.connect()
    RPC.update(
        state="Listening to Music",
        large_image="acorn",
        buttons=[{"label": "Download Acorn", "url": "https://jaxfry.me/"}]
    )

def stop_rpc():
    RPC.close()
def megumin():
    RPC.update(
        state="Listening To Some Explosion! Music",
        large_image="megumin",
        buttons=[{"label": "Download Acorn", "url": "https://jaxfry.me/"}]
    )
def no_megumin():
    RPC.update(
        state="Listening to Music",
        large_image="acorn",
        buttons=[{"label": "Download Acorn", "url": "https://jaxfry.me/"}]
    )
    
# Create a timer to stop the music after a certain amount of time
def set_timer():
    # Create a new window with a text entry box
    window = Toplevel(root)
    window.title("Set Timer")
    window.geometry("500x150")
    window.resizable(False, False)
    window.configure(bg="grey")

    
    # Create a label for the text entry box
    label = Label(window, text="Enter the number of minutes to set the timer for:", bg="grey", fg="black")
    label.pack(pady=10)

    # Create a text entry box
    entry = Entry(window, width=50, borderwidth=2)
    entry.pack(pady=10)
    
    # Create a button to start the timer
    button = Button(window, text="Start Timer", command=lambda: start_timer(entry.get(), window))
    button.pack(pady=10)
    
def start_timer(minutes, window):
    # Close the window
    window.destroy()
    
    # Convert the minutes to seconds
    minutes = int(minutes)
    seconds = minutes * 60
    
    # Start the timer
    global timer
    timer = root.after(seconds * 1000, stop)
    
    # Update the status bar to show the timer
    timer_label_text.config(text=f'Timer: {minutes} minutes')
    
    # Update the timer label every second
    timer_label(seconds)
    
def timer_label(seconds):
    # Create a label to show the remaining time
    remaining_time = seconds
    if remaining_time > 0:
        remaining_time = datetime.utcfromtimestamp(remaining_time).strftime('%H:%M:%S')
        timer_label_text.config(text=f'Timer: {remaining_time}')
        seconds -= 1
        root.after(1000, timer_label, seconds)
    else:
        timer_label_text.config(text='')

def delete_all_song_file():
    # Delete all files in the music folder
    for filename in os.listdir("assets/music/"):
        file_path = os.path.join("assets/music/", filename)
        os.remove(file_path)
        refresh_list()

def delete_all_playlists():
    # Delete all files in the playlists folder
    for filename in os.listdir("assets/playlists/"):
        file_path = os.path.join("assets/playlists/", filename)
        os.remove(file_path)

def normalize_audio_folder(target_volume=-20):
    pygame.mixer.music.stop()
    # Create a window to show the progress of the normalization
    window = Toplevel(root)
    window.title("Normalizing Audio")
    window.geometry("500x150")
    window.resizable(False, False)
    window.configure(bg="grey")

    window_label = Label(window, text="Normalizing audio... This may take a few mins!", bg="grey", fg="black")
    window_label.pack(pady=10)

    
    # Iterate through each file in the folder
    for filename in os.listdir("assets/music/"):
        if filename.endswith('.mp3'):
            file_path = os.path.join("assets/music/", filename)
            
            # Load the audio file
            audio = AudioSegment.from_file(file_path, format="mp3")
            
            # Calculate the necessary gain to achieve the target volume
            current_volume = audio.dBFS
            gain = target_volume - current_volume
            
            # Apply the gain to normalize the volume
            normalized_audio = audio + gain
            
            # Export the normalized audio back to the same file
            normalized_audio.export(file_path, format="mp3")
            
            
    # Close the window
    window.destroy()


def save_playlist():
    playlist_filename = filedialog.asksaveasfilename(defaultextension=".acorn", filetypes=[("Playlist Files", "*.acorn")])
    if playlist_filename:
        with open(playlist_filename, "w") as file:
            for song in song_box.get(0, END):
                file.write(song + "\n")

        # Move the saved playlist to the playlists folder
        playlist_folder = "assets/playlists"
        os.makedirs(playlist_folder, exist_ok=True)
        shutil.move(playlist_filename, os.path.join(playlist_folder, os.path.basename(playlist_filename)))


def load_playlist():
    playlist_filename = filedialog.askopenfilename(filetypes=[("Playlist Files", "*.acorn",)])
    if playlist_filename:
        with open(playlist_filename, "r") as file:
            songs = file.readlines()
            song_box.delete(0, END)
            for song in songs:
                song_box.insert(END, song.strip())
    pygame.mixer.music.stop()

def shuffle():
    # Clear the current playlist
    song_box.delete(0, END)
    # Loop thru the music directory and get names of songs
    songs = []
    for song in os.listdir('assets/music/'):
        if song.endswith('.mp3' or '.wav' or '.ogg'):
            songs.append(song)
    random.shuffle(songs)
    for song in songs:
        song_box.insert(END, song)
        
    
def end_of_song():
    print("End of song!")
    next_song()

def refresh_list():

            
    # Check the music directory for any webm files and convert them to mp3
    for song in os.listdir('assets/music/'):
        if song.endswith('.webm'):
            # Convert to mp3
            subprocess.run('ffmpeg -i "assets/music/' + song + '" "assets/music/' + re.sub(r'.webm', '.mp3', song) + '"', shell=True)
            # Delete the webm file
            os.remove("assets/music/" + song)
            
    # Clear the current playlist
    song_box.delete(0, END)
    
    # Loop thru the music directory and get names of songs
    for song in os.listdir('assets/music/'):
        if song.endswith('.mp3' or '.wav' or '.ogg'):
            # Add to playlist
            song_box.insert(END, song)
            
    # Define the path to the playlists folder
    playlist_folder = "assets/playlists"
    os.makedirs(playlist_folder, exist_ok=True)

    # Load the last saved playlist if available
    last_playlist_filename = os.path.join(playlist_folder, "last_playlist.acorn")
    if os.path.exists(last_playlist_filename):
        with open(last_playlist_filename, "r") as file:
            songs = file.readlines()
            for song in songs:
                song_box.insert(END, song.strip())

def add_song_file():
    song = filedialog.askopenfilename(initialdir='/', title="Choose A Song", filetypes=(("mp3 Files", "*.mp3"), ("wav Files", "*.wav"), ("ogg Files", "*.ogg"), ))
    shutil.copyfile(song, 'assets/music/' + re.sub(r'.*\/', '', song))
    # use regex to remove the path from song name
    song = re.sub(r'.*\/', '', song)
    
    # Add song to list box
    song_box.insert(END, song)
    
def add_multiple_songs_file():
    songs = filedialog.askopenfilenames(initialdir='music/', title="Choose Multiple Songs", filetypes=(("mp3 Files", "*.mp3"), ("wav Files", "*.wav"), ("ogg Files", "*.ogg"), ))
    
    #Loop thrugh songslist and do replace
    for song in songs:
        shutil.copyfile(song, 'assets/music/' + re.sub(r'.*\/', '', song))
        # use regex to remove the path from song name
        song = re.sub(r'.*\/', '', song)
        song_box.insert(END, song)
        
def add_song_youtube():
    # Create a new window with a text entry box
    window = Toplevel(root)
    window.title("Add Song From Youtube")
    window.geometry("500x150")
    window.resizable(False, False)
    window.configure(bg="grey")

    
    # Create a label for the text entry box
    label = Label(window, text="Enter a Youtube Video/Playlist link:", bg="grey", fg="black")
    label.pack(pady=10)

    # Create a text entry box
    entry = Entry(window, width=50, borderwidth=2)
    entry.pack(pady=10)
    
    # Create a progress label
    progress_label = Label(window, text="", bg="grey", fg="black")
    progress_label.pack()
    
    # Create a button to download the song from the link
    button = Button(window, text="Download", command=lambda: youtube_download(entry.get(), progress_label, window))
    button.pack(pady=10)




####
plpattern = r"^(https?:\/\/)?(www\.)?youtube\.com\/playlist\?list=[A-Za-z0-9_-]+(&[A-Za-z0-9_-]+=[A-Za-z0-9%_-]+)*$"
vipattern = r"^(https?:\/\/)?(www\.)?youtube\.com\/watch\?v=[A-Za-z0-9_-]+(&[A-Za-z0-9_-]+=[A-Za-z0-9%_-]+)*$"
idpattern = r"(?<=v=|\/watch\?v=|\/embed\/|youtu.be\/|\/v\/|\/e\/|\/watch\?v%3D|\/embed%\u200C\u200B2F|youtu.be%2F|\/v%2F|e%2F|watch\?v%3d|%2Fvideos%2F|embed%\u200C\u200B2f|youtu.be%2f|%2fv%2f)([^#\&\?\n]*)"


print(""" 
    /\                        
   /  \   ___ ___  _ __ _ __  
  / /\ \ / __/ _ \| '__| '_ \ 
 / ____ \ (_| (_) | |  | | | |
/_/    \_\___\___/|_|  |_| |_|
    Music Player/downloader
""")

def Download(link):
    options = {
        'format': 'bestaudio',
        'outtmpl': os.path.join("assets/music/", '%(title)s.%(ext)s'),
        'quiet': True
    }
    audio_downloader = YoutubeDL(options)
        
    audio_downloader.extract_info(link)
    title = get_title_from_link(link)
    print("Downloaded: " + title)
    
    try:
        subprocess.run('ffmpeg -i "assets/music/' + title + '.webm" "assets/music/' + title + '.mp3"', shell=True)
        os.remove("assets/music/" + title + ".webm")
        song_box.insert(END, title + ".mp3")
    except:
        print("ERROR! Could not convert file to mp3! If the youtube title contains special characters, this is expected. The file will be converted to mp3 after the other songs have been downloaded.")



def get_links_from_playlist(playlist_url):
    playlist = Playlist(playlist_url)
    links = playlist.video_urls
    return links

def get_title_from_link(link):
    if re.match(plpattern, link):
        playlist = Playlist(link)
        title = playlist.title()
    elif re.match(vipattern, link):
        youtubeObject = YouTube(link)
        title = youtubeObject.title
    else:
        title = "Unknown"
    return title
    
def get_id_from_link(link):
    if "youtube.com/watch?v=" in link:
        # Extract the video ID after the "v=" parameter
        video_id = link.split("v=")[1]
        # The video ID might be followed by other parameters; extract the ID until the first "&" character or the end of the string
        video_id = video_id.split("&")[0]
        return video_id
    else:
        raise ValueError("Invalid YouTube video URL. Please provide a valid YouTube video URL.")




def youtube_download(link, progress_label, window):
    print("BUTTON CLICKED")
    print(link)
    progress_label.config(text="Downloading... This window will frezze until the download is complete. Please wait...")
    window.update()  # Update the window to show the label change
    if re.match(plpattern, link):
        vidLinks = get_links_from_playlist(link)
        print("Playlist Detected!")
        for vidLink in vidLinks:
            print("Downloading: " + get_title_from_link(vidLink))
            Download(vidLink)
        print("Downloaded all videos in playlist!")

    elif re.match(vipattern, link):
        print("Video Detected!")
        print("Downloading: " + get_title_from_link(link))
        Download(link)
        print("Downloaded video!")
        
    refresh_list()
    progress_label.config(text="Download completed!")
    window.update()  # Update the window to show the final label change
    window.after(2000, window.destroy)  # Destroy the window after 2 seconds

####


        

#play
def play():
    # Set the song requested to play to global current_song
    
    song = song_box.get(ACTIVE)
    song = f'assets/music/{song}'
    
    pygame.mixer.music.load(song)
    pygame.mixer.music.play(loops=0)
    # Call the playtime function to get song length
    play_time()

    # Save the current playlist to a file
    with open("assets/playlists/last_playlist.acorn", "w") as file:
        for song in song_box.get(0, END):
            file.write(song + "\n")

#stop
def stop():
    pygame.mixer.music.stop()
    song_box.selection_clear(ACTIVE)
    
    #Clear status bar
    status_bar.config(text='')
    
#Play the next song
def next_song():
    #Get the current song tuple number
    next_one = song_box.curselection()
    #Add one to the current song number
    next_one = next_one[0]+1
    #Grab the song title from the playlist
    song = song_box.get(next_one)
    #Add directory structure
    song = f'assets/music/{song}'
    #Load and play song
    try:
        pygame.mixer.music.load(song)
        pygame.mixer.music.play(loops=0)
        #Clear active bar in playlist
        song_box.selection_clear(0, END)
        #Activate new song bar
        song_box.activate(next_one)
        #Set active bar to next song
        song_box.selection_set(next_one, last=None)
        if platform.system() == "Darwin":
            notify("Acorn", "Playing: " + song_box.get(ACTIVE))
        
    #If no more songs, play the first one if loop is on
    except:
        if loop_var.get() == 1:
            if shuffle_var.get() == 1:
                shuffle()
            song = song_box.get(0)
            #Add directory structure
            song = f'assets/music/{song}'
            #Load and play song
            pygame.mixer.music.load(song)
            pygame.mixer.music.play(loops=0)
            #Clear active bar in playlist
            song_box.selection_clear(0, END)
            #Activate new song bar
            song_box.activate(0)
            #Set active bar to next song
            song_box.selection_set(0, last=None)
            if platform.system() == "Darwin":
                notify("Acorn", "Playing: " + song_box.get(ACTIVE))
        else:
            print("END OF PLAYLIST!")
            if platform.system() == "Darwin":
                notify("Acorn", "End of playlist!")
            
    
    
#Play the previous song
def previous_song():
    #Get the current song tuple number
    previous_one = song_box.curselection()
    #Add one to the current song number
    previous_one = previous_one[0]-1
    #Grab the song title from the playlist
    song = song_box.get(previous_one)
    #Add directory structure
    song = f'assets/music/{song}'
    #Load and play song
    try:
        pygame.mixer.music.load(song)
        pygame.mixer.music.play(loops=0)
        #Clear active bar in playlist
        song_box.selection_clear(0, END)
        #Activate new song bar
        song_box.activate(previous_one)
        #Set active bar to next song
        song_box.selection_set(previous_one, last=None)
    #If no more songs, play the last one
    except:
        song = song_box.get(END)
        #Add directory structure
        song = f'assets/music/{song}'
        #Load and play song
        pygame.mixer.music.load(song)
        pygame.mixer.music.play(loops=0)
        #Clear active bar in playlist
        song_box.selection_clear(0, END)
        #Activate new song bar
        song_box.activate(END)
        #Set active bar to next song
        song_box.selection_set(END, last=None)
    

# Delete A song
def delete_song():
    pygame.mixer.music.stop()
    # Delete the song from the playlist
    song_box.delete(ANCHOR)

    
# Delete ALL songs
def delete_all_songs():
    song_box.delete(0, END)
    pygame.mixer.music.stop()
    last_playlist_filename = "assets/playlists/last_playlist.acorn"
    if os.path.exists(last_playlist_filename):
        os.remove(last_playlist_filename)
    


#GLOBAL PAUSE VAR
global paused
paused = False
#pause
def pause(is_paused):
    global paused
    paused = is_paused
    
    if paused:
        #unpause
        pygame.mixer.music.unpause()
        paused = False
    else:
        #pause
        pygame.mixer.music.pause()
        paused = True



#Playlist box
song_box = Listbox(root, bg="grey", fg="black", width=60, selectbackground="cyan", selectforeground="purple")
song_box.pack(pady=20)


#Player Control buttons
back_btn_icon = PhotoImage(file='assets/icons/icon_back.png')
forward_btn_icon = PhotoImage(file='assets/icons/icon_forward.png')
play_btn_icon = PhotoImage(file='assets/icons/icon_paused.png')
pause_btn_icon = PhotoImage(file='assets/icons/icon_playing.png')
stop_btn_icon = PhotoImage(file='assets/icons/icon_stop.png')

#Frame
controls_frame = Frame(root)
controls_frame.pack()

# checkBox Frame
checkBox_frame = Frame(root)
checkBox_frame.pack()

#Create buttons
back_button = Button(controls_frame, image=back_btn_icon, borderwidth=0, command=previous_song)
forward_button = Button(controls_frame, image=forward_btn_icon, borderwidth=0, command=next_song)
play_button = Button(controls_frame, image=play_btn_icon, borderwidth=0, command=play)
pause_button = Button(controls_frame, image=pause_btn_icon, borderwidth=0, command=lambda: pause(paused))
stop_button = Button(controls_frame, image=stop_btn_icon, borderwidth=0, command=stop)

back_button.grid(row=0, column=0, padx=10)
forward_button.grid(row=0, column=1, padx=10)
play_button.grid(row=0, column=2, padx=10)
pause_button.grid(row=0, column=3, padx=10)
stop_button.grid(row=0, column=4, padx=10)

# Create checkboxs

# Loop checkbox
loop_var = IntVar()
loop_checkbox = Checkbutton(checkBox_frame, text="Loop", variable=loop_var)
loop_checkbox.grid(row=0, column=0, padx=10)

# Shuffle checkbox
shuffle_var = IntVar()
shuffle_checkbox = Checkbutton(checkBox_frame, text="Shuffle", variable=shuffle_var)
shuffle_checkbox.grid(row=0, column=1, padx=10)


#Create menu
my_menu = Menu(root)
root.config(menu=my_menu)

#Add song Menu
add_song_menu = Menu(my_menu)
my_menu.add_cascade(label="Songs", menu=add_song_menu)
add_song_menu.add_command(label="Add Song From File", command=add_song_file)

#Add multiple songs
add_song_menu.add_command(label="Add Multiple Songs From File", command=add_multiple_songs_file)
add_song_menu.add_command(label="Add Song From Youtube", command=add_song_youtube)
add_song_menu.add_separator()  # Add a separator
add_song_menu.add_command(label="Normalize Audio Folder", command=normalize_audio_folder)
add_song_menu.add_command(label="Remove Silence On End", command=remove_end_silence)
add_song_menu.add_command(label="Refresh List", command=refresh_list)



#Add delete song menu
remove_song_menu = Menu(my_menu)
my_menu.add_cascade(label="Remove Songs", menu=remove_song_menu)
remove_song_menu.add_command(label="Delete Selected Song From Playlist", command=delete_song)
remove_song_menu.add_command(label="Delete ALL Songs From Playlist", command=delete_all_songs)
remove_song_menu.add_separator()  # Add a separator
remove_song_menu.add_command(label="DELETE ALL SONG FILES", command=delete_all_song_file)

#Add playlists menu
playlists_menu = Menu(my_menu)
my_menu.add_cascade(label="Playlists", menu=playlists_menu)
playlists_menu.add_command(label="Shuffle", command=shuffle)
playlists_menu.add_separator()  # Add a separator
playlists_menu.add_command(label="Save Playlist", command=save_playlist)
playlists_menu.add_command(label="Load Playlist", command=load_playlist)
remove_song_menu.add_separator()  # Add a separator
playlists_menu.add_command(label="Delete All Playlists", command=delete_all_playlists)

#Add timer menu
timer_menu = Menu(my_menu)
my_menu.add_cascade(label="Timer", menu=timer_menu)
timer_menu.add_command(label="Set Timer Time", command=set_timer)

#Add RPC menu
rpc_menu = Menu(my_menu)
my_menu.add_cascade(label="Discord RPC", menu=rpc_menu)
rpc_menu.add_command(label="Enable", command=start_rpc)
rpc_menu.add_command(label="Disable", command=stop_rpc)
rpc_menu.add_separator()  # Add a separator
rpc_menu.add_command(label="Megumin", command=megumin)
rpc_menu.add_command(label="No Megumin :(", command=no_megumin)



#Create status bar
status_bar = Label(root, text='', bd=1, relief=GROOVE, anchor=E)
status_bar.pack(fill=X, side=BOTTOM, ipady=2)
# Add another label to the status bar to show the timer but on the left side
timer_label_text = Label(status_bar, text='')
timer_label_text.pack(side=LEFT)


# Pause if spacebar is pressed
def spacebar(event):
    pause(paused)
root.bind("<space>", spacebar)



refresh_list()
start_rpc()
root.mainloop()