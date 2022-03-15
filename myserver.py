from flask import Flask, render_template
import json

from vosk import Model, KaldiRecognizer
import wave
import re

app = Flask(__name__)
app.secret_key = 'secret key'

@app.route('/', methods=['POST', 'GET'])
def start():
    return render_template('home.html')

@app.route('/translate', methods=['POST'])
def api():

    vosk_model = Model("vosk-model-small-ru-0.22")
    vosk_audio = 'static/revolver.wav'

    wf = wave.open(vosk_audio, "rb")
    rcgn_fr = wf.getframerate() * wf.getnchannels()
    rec = KaldiRecognizer(vosk_model, rcgn_fr)
    result = ''
    last_n = False
    # read_block_size = 4000
    read_block_size = wf.getnframes()
    while True:
        data = wf.readframes(read_block_size)
        if len(data) == 0:
            break

        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())

            if res['text'] != '':
                result = result + " " + res['text']
                if read_block_size < 200000:
                    print(res['text'] + " \n")

                last_n = False
            elif not last_n:
                result += '\n'
                last_n = True

    res = json.loads(rec.FinalResult())
    result = result + " " + res['text']
    
    return '\n'.join(line.strip() for line in re.findall(r'.{1,150}(?:\s+|$)', result))
