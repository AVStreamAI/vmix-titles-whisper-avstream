import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pyaudio
import wave
from faster_whisper import WhisperModel
import os
import re
import time

NEON_GREEN = '\033[92m'
RESET_COLOR = '\033[0m'

# Function to initialize the Google Sheets client
def init_google_sheets_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('PATH_TO_YOUR_JSON_KEYFILE', scope)
    client = gspread.authorize(creds)
    return client

# Function to update a specific cell in Google Sheets
def update_google_sheet(client, sheet_id, cell, text):
    sheet = client.open_by_key(sheet_id).sheet1
    try:
        sheet.update_acell(cell, text)
    except Exception as e:
        print(f"Failed to update sheet: {e}")

def transcribe_chunk(model, file_path):
    segments, info = model.transcribe(file_path, beam_size=5) #BeamSize 1 = fast, 10 = precise
    transcription = ' '.join(segment.text for segment in segments)
    return transcription

def record_chunk(p, stream, file_path, chunk_length=5): #audio length in seconds
    frames = []
    for _ in range(0, int(32000 / 2048 * chunk_length)):
        data = stream.read(2048)
        frames.append(data)
    wf = wave.open(file_path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(32000)
    wf.writeframes(b''.join(frames))
    wf.close()

def choose_audio_device(p):
    device_count = p.get_device_count()
    print("Available audio devices:")
    for i in range(device_count):
        dev = p.get_device_info_by_index(i)
        print(f"{i}: {dev['name']} (Channels: {dev['maxInputChannels']})")
    dev_index = int(input("Please select an audio device by index: "))
    return dev_index

def main2():
    # Initialize the Google Sheets client
    gs_client = init_google_sheets_client()
    sheet_id = "YOUR_GOOGLE_SHEET_ID"  # Replace with your Google Sheet ID
    cell_to_update = "A1"  # Example cell, adjust as needed
    column_b_counter = 1
    # Choose your model settings
    model_size = "large-v3" #tiny, small, medium, large-v3
    model = WhisperModel(model_size, device="cuda", compute_type="float32") #cpu, int8

    p = pyaudio.PyAudio()

    device_index = choose_audio_device(p)

    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True,
                    frames_per_buffer=1024, input_device_index=device_index)

    accumulated_transcription = ""  # Initialize an empty string to accumulate transcriptions

    try:
        while True:
            chunk_file = "temp_chunk.wav"
            record_chunk(p, stream, chunk_file)
            transcription = transcribe_chunk(model, chunk_file)
            print(NEON_GREEN + transcription + RESET_COLOR)
            os.remove(chunk_file)

            # Update the Google Sheet with just the latest transcription in A1

            update_google_sheet(gs_client, sheet_id, cell_to_update, transcription)

            # Log each transcription chunk in column B, cell by cell
            b_cell_to_update = f"B{column_b_counter}"
            update_google_sheet(gs_client, sheet_id, b_cell_to_update, transcription)
            column_b_counter += 1  # Increment the counter for the next cell in column B

            # Check and filter out undesired transcriptions more robustly
            clean_transcription = re.sub(r'\b(Thank you\.?|you\.?)\b', '', transcription, flags=re.IGNORECASE).strip()
            if clean_transcription:  # If there's anything meaningful left after cleaning
                accumulated_transcription += f" {clean_transcription}"  # Append it

    except KeyboardInterrupt:

        print("Stopping...")
        # Debug print before any substitution
        print(f"Accumulated before cleaning: '{accumulated_transcription}'")
        # Apply the substitution
        final_transcription = re.sub(r'\bThank you\.?|\byou\.?\b', '', accumulated_transcription,
                                     flags=re.IGNORECASE).strip()
        # Debug print after substitution
        print(f"Final Transcription: '{final_transcription}'")
        print("LOG:" + final_transcription)
        # Save the final transcription to a .txt file
        with open('transcription_log.txt', 'w') as log_file: #name of txt file in project folder after stopping script. Remember to copy information before next launch
            log_file.write(final_transcription)
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    main2()
