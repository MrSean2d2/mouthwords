#! /usr/bin/env python3


# mouthwords - a script to put words in other people's mouths

# Copyright © 2020 Sean Reitsma

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# TODO Add a check for framerate problems or somehow support differing framerates in videos (Issue #1)


from vosk import Model, KaldiRecognizer, SetLogLevel
import sys
import os
import wave
import subprocess
import json
import argparse
from moviepy.editor import VideoFileClip, concatenate_videoclips
import uuid

parser = argparse.ArgumentParser(description="A script to put words in other people's mouths", usage="%(prog)s [OPTIONS] [WORDFILE] [FILES...]")
group = parser.add_mutually_exclusive_group()

group.add_argument("-w", "--writejson", help="Write transcript to a JSON file", action="store_true")
group.add_argument("-r", "--readjson", help="Read from JSON transcript", action="store_true")
parser.add_argument("wordfile", help="Text file of words to search for")
parser.add_argument("files", nargs="+", help="MPEG4 files (all with the same fps!) or JSON transcripts to search through")
args = parser.parse_args()
words = []
words_immutable = []
total_found_words = []

class Word:
   
    def __init__(self, conf, start, end, word, fileIn):
        self.conf = conf
        self.start = start
        self.end = end
        self.word = word
        self.file = fileIn
        self.uuid = uuid.uuid4()



    # TODO method to write json from object data

        
with open(args.wordfile, "r") as wordfilestring:
    for line in wordfilestring:
        for word in line.split():
            words.append(word)
            words_immutable.append(word)

def wordsFromList(datalist):
    export_list = []
    for data in datalist:
        if "result" in data:
            for i in data["result"]:
                word = Word(i["conf"], i["start"], i["end"], i["word"], i["file"])
                export_list.append(word)

    return export_list



def cutAndPaste(datalist):
    clips = []
    for data in datalist:
        start = data.start - 0.01
        end = data.end + 0.01
        clip = VideoFileClip(data.file).subclip(start, end)
        clips.append(clip)

    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile(f"output.mp4", audio=True)
    for clip in clips:
        clip.close()

        


def search(wordlist):
    word_data = []
    for i in wordlist:
        for x, input_word in enumerate(words):
            if i.word == input_word:
                print(f"{input_word}: File: {i.file} Start (s): {i.start}")
                print(f"{input_word}: File: {i.file} End (s): {i.end}")
                words[x] = i.uuid
                word_data.append(i)
                break
            
    return word_data
            

def speechRecogAndSearch(fileIn):
    datalist = []
    SetLogLevel(0)

    if not os.path.exists("model"):
        print("Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
        exit(1)


    sample_rate=16000
    model = Model("model")
    rec = KaldiRecognizer(model, sample_rate)
    try:
        process = subprocess.Popen(['ffmpeg', '-loglevel', 'quiet', '-i',
                                    fileIn,
                                    '-ar', str(sample_rate) , '-ac', '1', '-f', 's16le', '-'],
                                    stdout=subprocess.PIPE)
    except IndexError:
        raise
    

    
    while True:
        data = process.stdout.read(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result = rec.Result()
            datalist.append(json.loads(result))

    finalResult = rec.FinalResult()
    datalist.append(json.loads(finalResult))
    print(fileIn)
    for entry in datalist:
        if "result" in entry:
            for word in entry["result"]:
                word.update({"file": fileIn})
    words = wordsFromList(datalist)
    if args.writejson:
        with open(os.path.splitext(fileIn)[0] + ".json", "w") as output_json:
            output_json.write(json.dumps(datalist))

    
    found_words = search(words)
    return found_words


for file in args.files:
    print(f"Searching for words in {file}\nThis may take a while, please be patient...")
    if args.readjson:
        with open(file, "r") as input_json:
            input_words = wordsFromList(json.loads(input_json.read()))
            found_words = search(input_words)

    else:
        found_words = speechRecogAndSearch(file)
    total_found_words.extend(found_words)


if total_found_words == []:
    print(f"{sys.argv[0]} did not find any words!", file=sys.stderr)
else:
    total_found_words.sort(key=lambda i: words.index(i.uuid))
    cutAndPaste(total_found_words)
