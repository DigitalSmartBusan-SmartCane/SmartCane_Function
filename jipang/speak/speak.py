from gtts import gTTS
import os

def speak_text(text):
    tts = gTTS(text=text, lang='ko')
    tts.save("output.mp3")
    os.system("mpg321 output.mp3")

if __name__ == "__main__":
    text_to_speak = "최영주 스트레스 받지마"
    speak_text(text_to_speak)
