import pyaudio
import wave
import sys
import time

def record_audio(output_file="test_audio.wav", duration=5, sample_rate=44100):
    """
    Record audio from the microphone.
    
    Args:
        output_file: Path to save the WAV file
        duration: Recording duration in seconds
        sample_rate: Sample rate in Hz
    """
    # Configure audio recording
    chunk = 1024
    format = pyaudio.paInt16
    channels = 1
    
    # Initialize PyAudio
    p = pyaudio.PyAudio()
    
    print(f"Recording {duration} seconds of audio...")
    print("Speak into your microphone!")
    
    # Open stream
    stream = p.open(format=format,
                   channels=channels,
                   rate=sample_rate,
                   input=True,
                   frames_per_buffer=chunk)
    
    # Record audio
    frames = []
    for i in range(0, int(sample_rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)
        # Print progress
        sys.stdout.write(f"\rRecording: {i * chunk / sample_rate:.1f}s / {duration}s")
        sys.stdout.flush()
    print("\nDone recording!")
    
    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    # Save the recorded data as a WAV file
    with wave.open(output_file, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(format))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))
    
    print(f"Audio saved to {output_file}")

if __name__ == "__main__":
    record_audio() 