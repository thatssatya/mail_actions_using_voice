from playsound import playsound
from gtts import gTTS 
from constants import LANGUAGE, MICROPHONE_NAME
from login_credentials import EMAIL_ID, PASSWORD
import os
import speech_recognition as sr

def isLoginCredentialsPresent():
    if EMAIL_ID != "" and PASSWORD != "":
        return True
    return False

def SpeakText(command, langinp=LANGUAGE):
    """
    Text to Speech using GTTS

    Args:
        command (str): Text to speak
        langinp (str, optional): Output language. Defaults to "en".
    """
    if langinp == "":
        langinp = "en"
    tts = gTTS(text=command, lang=langinp)
    tts.save("~tempfile01.mp3")
    playsound("~tempfile01.mp3")
    print(command)
    os.remove("~tempfile01.mp3")


def speech_to_text():
    """
    Speech to text

    Returns:
        str: Returns transcripted text
    """
    r = sr.Recognizer()
    device_id = 0

    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        if name == MICROPHONE_NAME:
            device_id = index
            break

    try:
        with sr.Microphone(device_index = device_id) as source2:
            r.adjust_for_ambient_noise(source2, duration=0.2)
            audio2 = r.listen(source2)
            MyText = r.recognize_google(audio2)
            print("You said: " + MyText)
            return MyText

    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))
        return None

    except sr.UnknownValueError:
        print("unknown error occured")
        return None

def sayChoice():
    while True:
        choice = speech_to_text()
        choice = choice.replace(' ', '')

        if choice == "1" or choice.lower() == "one":
                return 1
        elif (
            choice == "2"
            or choice.lower() == "too"
            or choice.lower() == "two"
            or choice.lower() == "to"
            or choice.lower() == "tu"
        ):
            return 2
        elif choice == "3" or choice.lower() == "tree" or choice.lower() == "three":
            return 3
        elif choice == "4" or choice.lower() == "four" or choice.lower() == "for":
            return 4
        elif choice == "5" or choice.lower() == "five":
            return 5
        else:
            SpeakText("Wrong choice. Please say only the number, try again...")
            continue

def confirmChoice():

    while True:
        confirmation = speech_to_text()
        confirmation = confirmation.replace(' ', '').lower()

        if confirmation == 'yes' or confirmation == 'no':
            return confirmation
        else:
            SpeakText('Please say only yes or no, try again...')


def clean(text):
    """
    clean text for creating a folder
    """
    return "".join(c if c.isalnum() else "_" for c in text)
