# mouthwords
A python script that automates the video editing required to put words in other peoples mouths.
This project aims to automate the process to recreate [this concept](https://youtu.be/slGYJfPtW7c).
Thanks to the flexibility of [Vosk](https://github.com/alphacep/vosk-api), it is possible to use mouthwords
with any language you have a model for, you can even train your own if you know how to do that sort of thing.
Currently Vosk looks for the model in the same directory as the script when you run it, and you have to download
and unzip it yourself — I haven't included one in the repository because the script is model independant.

---

## Dependencies
- A working python3 environment
- [Vosk API](https://github.com/alphacep/vosk-api) and the model you want to use for transcription, see <https://alphacephei.com/vosk/models>
- [MoviePy](https://github.com/Zulko/moviepy)
- ffmpeg (required by Vosk and MoviePy, they should pull this in automatically depending how you install them)

Both these projects are available on [PyPI](https://pypi.org/), and installable via `pip`
but if you are on Linux® be sure to check if there is a package in your distro's repositories.

---

## Installation
Work in progress; there is currently no real way to install this project other than cloning this
Git repository, installing dependencies, and using the script in the working directory. At some point
I will package this properly, but for now the necessary steps are below:

```sh
git clone https://github.com/MrSean2d2/mouthwords.git

cd mouthwords

wget http://alphacephei.com/vosk/models/vosk-model-small-en-us-0.4.zip

unzip vosk-model-small-en-us-0.4.zip

mv vosk-model-small-en-us-0.4.zip model
```
You can then run the script with `./mouthwords` in the current directory or
add the file to your $PATH

## Usage

```

usage: mouthwords.py write [-h] [-s SEARCHFILE] files [files ...]

positional arguments:
  files                 MPEG4 files to transcribe/search

optional arguments:
  -h, --help            show this help message and exit
  -s SEARCHFILE, --searchfile SEARCHFILE
                        Search through a text file and create a video output of concatenated words

usage: mouthwords.py read [-h] searchfile files [files ...]

positional arguments:
  searchfile  Text file of words to search for
  files       JSON transcripts to search through

optional arguments:
  -h, --help  show this help message and exit
```

When using .mp4 files make sure they are all the same framerate otherwise when MoviePy concatenates the clips
you end up with funky video.

The `write` command will run voice recognition on the .mp4 files passed to mouthwords, it will then write the transcript to
a .json file, and if `--searchfile` is passed it will search through the contents of the transcript, and create a video 
with clips containing the words specified concatenated together.

The `read` option will search through a .json file created by the `write` command for the words in `searchfile`, and create
a video with the words specified concatenated together.

`searchfile` should be a plain text file with the words you want in the order you want them, seperated by spaces, and with no punctuation.
The model used by Vosk will also determine what language the words can be, for example, if you are using the en_us model then the contents
of `searchfile` should be in US english, not British english etc.
