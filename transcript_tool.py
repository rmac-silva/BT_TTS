import os
import sys

# Windows-only audio playback
try:
    import winsound
except ImportError:
    winsound = None

# Try to import whisper, provide instructions if missing
try:
    import whisper
except ImportError:
    print("Error: 'openai-whisper' library not found.")
    print("Please install it and ffmpeg to use this script:")
    print("  pip install openai-whisper")
    print("Also ensure ffmpeg is installed on your system.")
    sys.exit(1)

def save_to_csv(file_path, wav_name, text):
    """Appends the transcription result using 'wavID | transcribed text' format."""
    file_exists = os.path.isfile(file_path)
    with open(file_path, mode='a', encoding='utf-8') as f:
        if not file_exists:
            f.write("wavID | transcribed text\n")
        # Ensure no newlines in the text to keep the format clean
        clean_text = text.replace('\n', ' ').replace('\r', '')
        f.write(f"{wav_name} | {clean_text}\n")

def main():
    # Look for input_wavs in the root folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_folder = os.path.abspath(os.path.join(script_dir, "input_wavs"))
    output_csv = os.path.join(script_dir, "transcribed_voicelines.csv")
    
    if not os.path.exists(input_folder):
        os.makedirs(input_folder)
        print(f"Created folder: {input_folder}")
        print("Please place your .wav files there and run the script again.")
        return

    # Load model
    print("Loading Whisper model ('base')... This might take a moment on first run.")
    # 'base' is a good balance between speed and accuracy for a free local run
    model = whisper.load_model("base")
    
    # Filter for wav files
    wav_files = [f for f in os.listdir(input_folder) if f.lower().endswith(".wav")]
    
    if not wav_files:
        print(f"No .wav files found in {input_folder}.")
        print(f"Path searched: {input_folder}")
        return

    print(f"Found {len(wav_files)} files. Starting transcription...\n")
    print("-" * 50)
    print("Instructions: Review the transcription and press Enter to keep it.")
    print("Otherwise, type the correct version. Type 'skip' to skip or 'quit' to exit.")
    print("-" * 50)

    for wav_file in wav_files:
        file_path = os.path.join(input_folder, wav_file)
        
        try:
            # Transcribe
            print(f"\nProcessing: {wav_file}")
            result = model.transcribe(file_path)
            transcription = result['text'].strip()
            
            # Start loop playback
            if winsound:
                winsound.PlaySound(file_path, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)

            print(f"Whisper thought: \"{transcription}\"")
            user_input = input("Correction >> ").strip()
            
            # Stop playback
            if winsound:
                winsound.PlaySound(None, 0)

            if user_input.lower() == 'quit':
                print("Exited by user.")
                break
            if user_input.lower() == 'skip':
                print("Skipped.")
                continue
                
            final_text = user_input if user_input else transcription
            save_to_csv(output_csv, wav_file, final_text)
            print(f"Saved: {final_text}")
            
        except Exception as e:
            print(f"Error processing {wav_file}: {e}")

    print("\nTranscription session finished.")
    print(f"Results saved to: {output_csv}")

if __name__ == "__main__":
    main()
