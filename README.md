# mouthwords
A python script to put words in other peoples mouths.
This project aims to automate the process to recreate [this concept](https://youtu.be/slGYJfPtW7c).
Thanks to the flexibility of [Vosk](https://github.com/alphacep/vosk-api), it is possible to use mouthwords
with any language you have a model for, you can even train your own if you know how to do that sort of thing.
Currently Vosk looks for the model in the same directory as the script when you run it, and you have to download
and unzip it yourself — I haven't included one in the repository because the script is model independant.

---

# Dependencies
- A working python3 environment
- [Vosk API](https://github.com/alphacep/vosk-api) and the model you want to use for transcription, see <https://alphacephei.com/vosk/models>
- [MoviePy](https://github.com/Zulko/moviepy)
- ffmpeg (required by Vosk and MoviePy, they should pull this in automatically depending how you install them)

Both these projects are available on [PyPI](https://pypi.org/), and installable via `pip`
but if you are on Linux® be sure to check if there is a package in your distro's repositories.

---

# Usage

'''

usage: mouthwords.py [OPTIONS] [WORDFILE] [FILES...]

A script to put words in other people's mouths

positional arguments:
  wordfile         Text file of words to search for
  files            MPEG4 files (all with the same fps!) or JSON transcripts to search through

optional arguments:
  -h, --help       show this help message and exit
  -w, --writejson  Write transcript to a JSON file
  -r, --readjson   Read from JSON transcript

'''

When using .mp4 files make sure they are all the same framerate otherwise when MoviePy concatenates the clips
you end up with funky video.

The `--writejson` option will run voice recognition on the .mp4 files passed to mouthwords, it will then write the transcript to
a .json file, and search through 
the transcript to find the words in WORDFILE, and create a video with clips containing the words specified concatenated together.
I'm considering adding a `--no-output` option, so that it only writes a transcript and doesn't create a video.

The `--readjson` option will search through a .json file created by the `--writejson` command for the words in WORDFILE, and create
a video with the words specified concatenated together.

WORDFILE should be a plain text file with the words you want in the order you want them, seperated by spaces, and with no punctuation.
The model used by Vosk will also determine what language the words can be, for example, if you are using the en_us model then the contents
of WORDFILE should be in US english, not British english etc.
