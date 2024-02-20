import os
import pathlib
def choose_dir():
    if not os.path.exists("Location.txt"):
        with open("Location.txt", 'w') as file:
            file.write(input("Choose your music directory:"))
    if os.path.exists("Location.txt"):
        if os.path.getsize("Location.txt") == 0:
            with open("Location.txt", 'w') as file:
                file.write(input("Choose your music directory:"))
    with open("Location.txt", 'r+') as f:
        flog = f.read()
        mfdir = flog[1:-1]
    return  mfdir
def num_of_files(mfdir):
    initcount = 0
    for path in pathlib.Path(mfdir).iterdir():
        if path.is_file():
            initcount+=1

    return f"{initcount} audio files found !"

def list_of_songs(songlist):
    for x in range(len(songlist)):
        print(f"{x + 1}.", songlist[x])
    song = songlist[int(input("Enter the song file (by number):")) - 1]
    return  song
def get_audio_files(directory):
    return [file for file in os.listdir(directory) if file.endswith(('.mp3', '.wav', '.ogg','.flac'))]