import tempfile
from io import BytesIO
from scipy.signal import fftconvolve
from scipy.io import wavfile
import numpy as np
import wave
import os


def choose_reverb_mode(mode):
    script_directory = os.path.dirname(os.path.abspath(__file__))
    relative_path = f'../data/impulse_response_file/{mode}.wav'
    absolute_path = os.path.normpath(os.path.join(script_directory, relative_path))
    return absolute_path


def add_second(input_file, second=2):
    with wave.open(input_file, 'rb') as input_wav:
        # Get the parameters
        params = input_wav.getparams()
        frames = input_wav.readframes(params.nframes)
        audio_data = np.frombuffer(frames, dtype=np.int16)

        # Calculate number of frames to add seconds
        frames_to_add = int(params.framerate * second)

        # Create array of zeros to add to the beginning of the wav data
        zeros_to_add = np.zeros(frames_to_add, dtype=np.int16)
        new_audio_data = np.concatenate((zeros_to_add, audio_data))

        params = params._replace(nframes=len(new_audio_data))

        output_buffer = BytesIO()

        with wave.open(output_buffer, 'wb') as output_wav:
            output_wav.setparams(params)
            output_wav.writeframes(new_audio_data.tobytes())

        output_buffer.seek(0)

        return output_buffer


def apply_reverb(input_file, mode, reverb_amount, wet_dry_ratio):
    if reverb_amount == 0 or mode == 'None':
        return input_file
    wet_dry_ratio = wet_dry_ratio / 100
    reverb_amount = reverb_amount / 100
    impulse_response_file = choose_reverb_mode(mode)
    input_file2 = add_second(input_file, 2)
    rate, data = wavfile.read(input_file2)
    _, ir = wavfile.read(impulse_response_file)
    data = data.astype(np.float32)
    ir = ir.astype(np.float32)
    adjusted_ir = ir * reverb_amount

    reverbed = fftconvolve(data, adjusted_ir, mode='same')

    # Adjust wet/dry mix
    dry = data * (1 - wet_dry_ratio)
    wet = reverbed * wet_dry_ratio
    mixed = dry + wet

    # Change to 16-bit range + convert to int16
    mixed = (mixed / np.abs(mixed).max() * 32767).astype(np.int16)

    # Use a temporary directory to avoid deletion issues
    temp_dir = tempfile.mkdtemp()
    output_file = os.path.join(temp_dir, "output.wav")

    wavfile.write(output_file, rate, mixed)

    return output_file
