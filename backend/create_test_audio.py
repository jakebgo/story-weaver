import wave
import numpy as np

def create_test_audio(duration=10, sample_rate=44100):
    """
    Create a test WAV file that simulates speech-like audio.
    
    Args:
        duration: Duration in seconds
        sample_rate: Sample rate in Hz
        
    Returns:
        Path to the created WAV file
    """
    # Generate time array
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Create multiple frequency components that vary over time (simulating speech)
    audio_data = np.zeros_like(t)
    
    # Add some "speech-like" components
    # First segment (0-3s): Lower pitch
    mask1 = (t >= 0) & (t < 3)
    base_freq1 = 120 + 20 * np.sin(2 * np.pi * 0.5 * t[mask1])
    audio_data[mask1] += 0.5 * np.sin(2 * np.pi * base_freq1 * t[mask1])
    for i in range(2, 5):
        audio_data[mask1] += 0.3/i * np.sin(2 * np.pi * base_freq1 * i * t[mask1])
    
    # Second segment (4-7s): Higher pitch
    mask2 = (t >= 4) & (t < 7)
    base_freq2 = 180 + 30 * np.sin(2 * np.pi * 0.7 * t[mask2])
    audio_data[mask2] += 0.5 * np.sin(2 * np.pi * base_freq2 * t[mask2])
    for i in range(2, 5):
        audio_data[mask2] += 0.3/i * np.sin(2 * np.pi * base_freq2 * i * t[mask2])
    
    # Third segment (8-10s): Mixed pitch
    mask3 = (t >= 8)
    base_freq3 = 150 + 40 * np.sin(2 * np.pi * 1.0 * t[mask3])
    audio_data[mask3] += 0.5 * np.sin(2 * np.pi * base_freq3 * t[mask3])
    for i in range(2, 5):
        audio_data[mask3] += 0.3/i * np.sin(2 * np.pi * base_freq3 * i * t[mask3])
    
    # Add some amplitude modulation (simulating speech patterns)
    am = 0.5 + 0.5 * np.sin(2 * np.pi * 3 * t)  # 3 Hz modulation
    audio_data *= am
    
    # Add some noise
    noise = np.random.normal(0, 0.05, len(t))
    audio_data += noise
    
    # Normalize and convert to 16-bit PCM
    audio_data = audio_data / np.max(np.abs(audio_data))
    audio_data = (audio_data * 32767).astype(np.int16)
    
    # Create WAV file
    output_path = "test_audio.wav"
    with wave.open(output_path, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes per sample
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
    
    print(f"Created test audio file: {output_path}")
    return output_path

if __name__ == "__main__":
    create_test_audio() 