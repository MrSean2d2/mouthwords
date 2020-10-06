#! /usr/bin/env python3

from vosk import Model, KaldiRecognizer, SetLogLevel
import sys
import os
import wave
import subprocess
import json
import argparse
from moviepy.editor import VideoFileClip, concatenate_videoclips

def cut_and_paste(dataList):
    clips = []
    for data in dataList:
        clip = VideoFileClip(data["file"]).subclip(data["start"], data["end"])
        clips.append(clip)

    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile(f"{sys.argv[0]}_output.mp4", audio=True)
    for clip in clips:
        clip.close()

        


def search(dataList, speechFile):
    words = []
    word_data = []
    if args.wordfile:
        with open(args.wordfile, "r") as wordfilestring:
            for line in wordfilestring:
                for lyric in line.split():
                    words.append(lyric)
        print(words)
    elif args.word:
        words.append(args.word)
        print(words)
    for word in words:
        print(f"Searching for {word}")
        for data in dataList:
            for i in data["result"]:
                if i["word"] == word:
                    print(f"{word}: File: {speechFile} Start (s): {i['start']}")
                    print(f"{word}: File: {speechFile} End (s): {i['end']}")
                    i.update({"file": speechFile})
                    word_data.append(i)
                    break
            break

    return word_data
            

def speech_recog_and_search(fileIn):
    datalist = []
    SetLogLevel(-1)

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
            stuff = json.loads(rec.Result())
            datalist.append(stuff)
        else:
            pass
    found_words = search(datalist, fileIn)
    return found_words


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-wf", "--wordfile", help="A text file containing words you want to search for")
    group.add_argument("-w", "--word", help="The word you want to search for")
    parser.add_argument("files", nargs="+", help="MPEG4 files to search through")
    global args
    args = parser.parse_args()
    total_found_words = []
    for file in args.files:
        found_words = speech_recog_and_search(file)
        total_found_words.extend(found_words)
    print(total_found_words)
    cut_and_paste(total_found_words)
    

main()
