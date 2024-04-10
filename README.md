Create venv

pip install gspread oauth2client pyaudio wave faster_whisper

Go to the Google Cloud Console. 

Create a new project or select an existing one. 

Navigate to the "APIs & Services > Dashboard" section. 

Enable the "Google Sheets API" and "Google Drive API" for your project. 

Go to "Credentials" and create a new service account. 

After creating the service account, click on it and go to the "Keys" section. 

Add a new key, select JSON, and download the JSON file. This file contains your credentials.

Add PATH to JSON into line 16

Copy your Google Sheets ID from URL

Add it to line 63

Choose model_size in line 67

If you have nVidia card and dont have cuda drivers, here is a link. https://disk.yandex.ru/d/XpuULF_F9jxScA Download and copy in C:\Windows\System32

Choose your audio input

Enjoy

video tutorial: [https://www.youtube.com/watch?v=lomedInrlE4](https://www.youtube.com/watch?v=lomedInrlE4)

tg: [https://t.me/avstream](https://t.me/avstream)

Code uses [@openai Whisper model](https://github.com/openai/whisper) and [Faster-whisper](https://github.com/SYSTRAN/faster-whisper)
