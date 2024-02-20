import pygame
import pydub
import pydub.playback
import time
from io import BytesIO
import wave
import contextlib
import os

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()


def convert_to_wav(file_path):
    # Import audio file
    with open(file_path, "rb") as file_handle:
        audio = pydub.AudioSegment.from_file(file_handle)
        # Export file as .wav
        output_file = BytesIO()
        audio.export(output_file, format="wav")
        output_file.seek(0)

        return output_file


def comment(song):
    print(f"Now playing:", song)
    print("Press 'p' to pause, 'r' to resume")
    print("Press 'e' to exit the current song")
    print("Press 't' to show the time, 'b' to set the playback time")
    print("Type value from 0.0 to 1.0 to set the volume ")


def play_song(cursong, type):
    pygame.mixer.init()
    if type == 1:
        pygame.mixer.music.load(cursong)
        pygame.mixer.music.play(0)
    if (type > 1) and (type % 2 == 0):
        pygame.mixer.music.pause()
    if (type > 1) and (type % 2 == 1):
        pygame.mixer.music.unpause()


def stop_song():
    pygame.mixer.music.stop()


def mtime():
    minute = int((pygame.mixer.music.get_pos() / 1000) / 60)
    second = int((pygame.mixer.music.get_pos() / 1000) - minute * 60)
    time = f"{minute}:{second}"
    return time


# def control(query):
#     if query == 'p':
#
#         # Pausing the music
#         pygame.mixer.music.pause()
#         return "PAUSE"
#     elif query == 'r':
#
#         # Resuming the music
#         pygame.mixer.music.unpause()
#         return "UNPAUSE"
#
#
#     elif data.checkfloat.is_float( query ):
#
#         # Change the volume
#         pygame.mixer.music.set_volume( float( query ) )
#
#
#     elif query == 't':
#
#         # Show the time
#         print( mtime() )
#
#
#     elif query == 'b':
#
#         # Backward&Forward playback time
#         print( "Set minute:" )
#         m = int( input() )
#         print( "Set second:" )
#         n = int( input() )
#         skiptime = int( (m * 60 + n) )
#         pygame.mixer.music.rewind()
#         pygame.mixer.music.set_pos( (skiptime) )
#
#     elif query == 'e':
#         # Stop the mixer
#         pygame.mixer.music.stop()
def audio_dur(file_handle):
    wav_file = wave.open(file_handle, 'rb')
    num_frames = wav_file.getnframes()
    framerate = wav_file.getframerate()

    duration_seconds = num_frames / float(framerate)
    if (isinstance(file_handle, str) == True):
        with open(file_handle) as f:
            f.seek(0)
    else:
        file_handle.seek(0)

    wav_file.close()

    return int(duration_seconds)
