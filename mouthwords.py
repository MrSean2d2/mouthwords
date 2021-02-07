#! /usr/bin/env python3


# mouthwords - a script to put words in other people's mouths

# Copyright © 2021 Sean Reitsma

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
def compile_words(args):
    with open(args.searchfile, "r") as wordfilestring:
        for line in wordfilestring:
            for word in line.lower().split():
                words.append(word)
                words_immutable.append(word)


def words_from_list(datalist):
    export_list = []
    for data in datalist:
        if "result" in data:
            for i in data["result"]:
                word = Word(i["conf"], i["start"], i["end"], i["word"], i["file"])
                export_list.append(word)

    return export_list


def cut_and_paste(datalist):
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
    for x, input_word in enumerate(words):
        for word in wordlist:
            if input_word == word.word:
                found_word = Word(word.conf, word.start, word.end, word.word, word.file)
                words[x] = found_word.uuid
                word_data.append(found_word)
                break
            return word_data


def speech_recog(fileIn):
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

    words = words_from_list(datalist)

    with open(os.path.splitext(fileIn)[0] + ".json", "w") as output_json:
        output_json.write(json.dumps(datalist))

    return words


def check_and_sort(words_in):
    if total_found_words == []:
        print(f"{sys.argv[0]} did not find any words!", file=sys.stderr)
    else:
        total_found_words.sort(key=lambda i: words.index(i.uuid))


def write(args):
    if args.searchfile:
        compile_words(args)

    for file in args.files:
        transcript = speech_recog(file)
        if args.searchfile:
            found_words = search(transcript)
            total_found_words.extend(found_words)

    if args.searchfile:
        check_and_sort(total_found_words)
        cut_and_paste(total_found_words)


def read(args):
    compile_words(args)
    print(words)
    for file in args.files:
        with open(file, "r") as input_json:
            input_words = words_from_list(json.loads(input_json.read()))

        found_words = search(input_words)
        total_found_words.extend(found_words)
    print(words)
    check_and_sort(total_found_words)
    cut_and_paste(total_found_words)


def main():
    parser = argparse.ArgumentParser(description="A script to put words in other people's mouths")
    subparsers = parser.add_subparsers(title="subcommands", help="Run '<command> -h' for specific help")
    parser_w = subparsers.add_parser("write", help="Write transcript to JSON file(s)")
    parser_w.add_argument("-s", "--searchfile", nargs=1, help="Search through a text file and create a video output of concatenated words")
    parser_w.add_argument("files", nargs="+", help="MPEG4 files to transcribe/search")
    parser_w.set_defaults(func=write)
    parser_r = subparsers.add_parser("read", help="Read JSON transcript(s)")
    parser_r.add_argument("searchfile", help="Text file of words to search for")
    parser_r.add_argument("files", nargs="+", help="JSON transcripts to search through")
    parser_r.set_defaults(func=read)
    args = parser.parse_args()
    try:
        args.func(args)
    except AttributeError as e:
        print(e)
        args = parser.parse_args(["-h"])

if __name__ == "__main__":
    main()
