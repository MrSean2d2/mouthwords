#! /usr/bin/env python3

# TODO Implement writing and reading from JSON files to avoid having to run the lengthy 
# speech recognition process more often than necessary

# TODO Add a check for framerate problems or somehow support differing framerates in videos

from vosk import Model, KaldiRecognizer, SetLogLevel
import sys
import os
import wave
import subprocess
import json
import argparse
from moviepy.editor import VideoFileClip, concatenate_videoclips

parser = argparse.ArgumentParser()
parser.add_argument("wordfile", help="Text file of words to search for")
parser.add_argument("files", nargs="+", help="MPEG4 files to search through - THESE MUST BE THE SAME FRAMERATE!")
args = parser.parse_args()
words = []
words_immutable = []
total_found_words = []
if args.wordfile:
        with open(args.wordfile, "r") as wordfilestring:
            for line in wordfilestring:
                for lyric in line.split():
                    words.append(lyric)
                    words_immutable.append(lyric)
elif args.word:
    words.append(args.word)
    words_immutable.append(args.word)

def cut_and_paste(dataList):
    clips = []
    for data in dataList:
        start = data["start"] - 0.01
        end = data["end"] + 0.01
        clip = VideoFileClip(data["file"]).subclip(start, end)
        clips.append(clip)

    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile(f"output.mp4", audio=True)
    for clip in clips:
        clip.close()

        


def search(dataList, speechFile):
    word_data = []
    for data in dataList:
        if "result" in data:
            for i in data["result"]:
                for word in words:
                    if i["word"] == word:
                        print(f"{word}: File: {speechFile} Start (s): {i['start']}")
                        print(f"{word}: File: {speechFile} End (s): {i['end']}")
                        i.update({"file": speechFile})
                        words.remove(word)
                        word_data.append(i)
                        break
            
    print(word_data)
    return word_data
            

def speech_recog_and_search(fileIn):
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
            datalist.append(json.loads(rec.Result()))

    datalist.append(json.loads(rec.FinalResult()))
    found_words = search(datalist, fileIn)
    return found_words


for file in args.files:
    print(f"Searching for words in {file}\nThis may take a while, please be patient...")
    found_words = speech_recog_and_search(file)
    total_found_words.extend(found_words)


if total_found_words == []:
    print(f"{sys.argv[0]} did not find any words!", file=sys.stderr)
else:
    total_found_words.sort(key=lambda i: words_immutable.index(i["word"]))
    print(total_found_words)
    cut_and_paste(total_found_words)

