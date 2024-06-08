#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, request, render_template, jsonify
import os
from flask_cors import CORS
from vosk import Model, KaldiRecognizer
import json
import wave
import requests
import zipfile
import time
from pydub import AudioSegment

class SpeechToTextService:
    def __init__(self, model_path="model", modelType = "BIG"):
        self.app = Flask(__name__)
        CORS(self.app)

        self.modelType = modelType
        self.model_path = model_path

        self.wakeUpMessage = "clear"
        self.SINGLE_STREAM_AUDIO = "singleStream.wav"
        self.CUMULATED_STREAM_AUDIO = "cumulatedStreams.wav"

        self.resettingStream()

        #Yes, there are better ways of reseting
        #after audio record button toggled off.
        
        #Also this is for the edge case where 
        #where user has no two second delay in switch off 
        self.timeSinceLastSend = 0
        self.TIME_WAIT_TOLERANCE = 6

        self.model = self.getModel(model_path)
        self.setup_routes()

    def getModel(self, path):
        model_path = path

        if self.modelType == "BIG" :
            model_url = "http://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip"
            extracted_folder_name = 'vosk-model-en-us-0.22'  # This is the name of the folder inside the zip file
        elif self.modelType == "SMALL" :
            model_url = "http://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
            extracted_folder_name = 'vosk-model-small-en-us-0.15'  # This is the name of the folder inside the zip file
        else : 
            raise("Incorrect model type provided")

        if not os.path.exists(model_path):
            print("Downloading the model...")
            r = requests.get(model_url)
            r.raise_for_status()
            with open("{}.zip".format(model_path), "wb") as f:
                f.write(r.content)

            with zipfile.ZipFile("{}.zip".format(model_path), "r") as zip_ref:
                zip_ref.extractall("")

            os.remove("model.zip")  # Clean up the zip file
            os.rename(os.path.join(extracted_folder_name), model_path)

        return Model(model_path)
    
    def append_wav(self, destination, source):
        """
        Appends the existing 'audio.wav' file's data to a different file specified by destination
        using Pydub.
        """
        # Using Pydub to handle the combination of two audio files
        try:
            source_sound = AudioSegment.from_wav(source)
            # If the append file exists and is not empty, we read it, otherwise we create an empty segment
            if os.path.exists(destination) and os.path.getsize(destination) > 0:
                append_sound = AudioSegment.from_wav(destination)
            else:
                append_sound = AudioSegment.silent(duration=0)  # Creating an empty audio segment

            # Combining the two audio segments
            combined_sounds = append_sound + source_sound

            # Exporting the combined audio segments
            combined_sounds.export(destination, format="wav")
            print(f"Appended data from {source} to {destination}.")
        except Exception as e:
            print(f"An error occurred while appending the WAV files: {e}")

    def index(self):
        if request.method == "POST":
            if 'file' not in request.files:
                print('No file part')
                return jsonify(user='server', message='No file part')

            # Given a file, then save the file.
            f = request.files['file']

            with open(self.SINGLE_STREAM_AUDIO, 'wb') as audio:
                f.save(audio)
            
            print('file uploaded successfully')
            singleStreamText = self.processAudio(self.SINGLE_STREAM_AUDIO)
            print("Transcript: ", singleStreamText)

            if time.time() > self.timeSinceLastSend + self.TIME_WAIT_TOLERANCE:
                print("time reset")
                self.resettingStream()

            #For some reason it hears "the" when no one is talking.
            #The or transcript == "" is just for clarity
            if (singleStreamText == "the" or singleStreamText == ""):
                print("reset")
                self.resettingStream()
            else:
                self.append_wav(self.CUMULATED_STREAM_AUDIO, self.SINGLE_STREAM_AUDIO)

                if self.awake :
                    self.timeSinceLastSend = time.time()
                    text = self.processAudio(self.CUMULATED_STREAM_AUDIO)
                    print(text)
                    return jsonify(user='thehuman', 
                            message= text)

                elif self.wakeUpMessage.lower() in singleStreamText.lower() :
                    self.awake = True
                    self.timeSinceLastSend = time.time()

                    startIndex = (str(singleStreamText).find(self.wakeUpMessage)+ 
                                len(self.wakeUpMessage) + 1)
                    
                    mess = singleStreamText[startIndex:]

                    # Will trigger some visual que to show listening
                    # self.append_wav("new.wav")
                    return jsonify(user='human', message=mess)
            
            #Nothing will apear for server
            return jsonify(user='bad', message="")

        return jsonify(user='server', message='GET request received')
    
    # Delete the audio file, and set awake to false
    def resettingStream(self):
        # If the system was awake, cumulating audio, or if just started
        if (not hasattr(self, "awake") or self.awake):
            # Check if file exists
            if os.path.exists(self.CUMULATED_STREAM_AUDIO):
                # Delete the file
                os.remove(self.CUMULATED_STREAM_AUDIO)
                print(f"The file {self.CUMULATED_STREAM_AUDIO} has been deleted.")
            else:
                print("The file does not exist.")

            self.awake = False
    
    # Audio to text occurs here
    def processAudio(self, audioPath):
        wf = wave.open(audioPath, "rb")
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            print("Audio file must be WAV format mono PCM.")
            return jsonify(user='server', message='Invalid audio file')
        rec = KaldiRecognizer(self.model, wf.getframerate())

        transcript = ""

        # Calculate the number of frames to read based on a time interval, e.g., 0.1 seconds
        time_interval = 0.1  # Time interval in seconds
        num_frames = int(wf.getframerate() * time_interval)

        while True:
            data = wf.readframes(num_frames)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                transcript += result.get('text') + " "

        transcript += json.loads(rec.FinalResult()).get('text')
        return transcript

    def setup_routes(self):
        self.app.route("/chat", methods=['POST', 'GET'])(self.index)

    def run(self, debug=True):
        # context = ('security/cert.pem', 'security/key.pem')
        self.app.run(host="0.0.0.0", port=2020, debug=debug, ssl_context=('security/cert.pem', 'security/key.pem'))

if __name__ == "__main__":
    service = SpeechToTextService()
    service.run(debug=False)
