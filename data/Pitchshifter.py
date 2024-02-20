import wave
import subprocess
import tempfile
import os
from io import BytesIO
import data.Reverb


def get_wav_sample_rate(file_handle):
    file_handle.seek(0)
    with wave.open(file_handle, 'rb') as wav_file:
        sample_rate = wav_file.getframerate()
    return sample_rate


def start_pitching(cursong):
    print("Set the semitone (-12->12):")
    semitone = int(input())
    print("Set the tempo (50->300):")
    tempo = int(input())
    pitchsong = pitch_shift_ffmpeg_rubberband(cursong, semitone, tempo, 0)  # set semitones to 0 is original
    return pitchsong


def pitch_shift_ffmpeg_tempomix(input_file, semitones):
    pitch_multiplier = 2 ** (semitones / 12)
    input_data = input_file.read()
    sr = get_wav_sample_rate(input_file)

    ffmpeg_cmd = 'ffmpeg -i pipe:0 -af "asetrate={}*{},aresample={},atempo=1/{}" -f wav -'.format(pitch_multiplier, sr,
                                                                                                  sr, pitch_multiplier,
                                                                                                  pitch_multiplier)
    with subprocess.Popen(
            ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    ) as process:
        stdout_data, stderr_data = process.communicate(input_data)
        if process.returncode != 0:
            print("", stderr_data.decode())
            return None

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        temp_file.write(stdout_data)

    return temp_file.name


def pitch_shift_ffmpeg_rubberband(input_file, semitones, tempo, mode):
    pitch_multiplier = 2 ** (semitones / 12)
    temp_fd, temp_path = tempfile.mkstemp(suffix=".wav")
    os.close(temp_fd)
    try:
        with open(temp_path, "wb") as temp_file:
            temp_file.write(input_file.read())

        # RunRubber Band
        cmd = [
            "ffmpeg",
            "-i", temp_path,
            "-af", f"rubberband=pitch={pitch_multiplier}:tempo={tempo / 100}:pitchq=consistency:transients=smooth",
            # Custom tempo(1 means 100% speed of default....eg:2 is 200% speed )
            temp_path + "_output1.wav"
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        with open(temp_path + "_output1.wav", "rb") as processed_file:
            processed_content = BytesIO(processed_file.read())

        return data.Reverb.apply_reverb(processed_content, mode, 10, 5)




    except Exception as e:

        print(f"Error: {e}")
        return None

    finally:
        # Clean temp files
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if os.path.exists(temp_path + "_output.wav"):
            os.remove(temp_path + "_output.wav")
