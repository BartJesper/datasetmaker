# Music Dataset Maker
A Python script that uses [Fluidsynth](https://www.fluidsynth.org/), PrettyMidi and Soundfile to generate datasets with varying parameters. The purpose of the script is to make generating your own music datasets for training artificial intelligence models. The generated music consists of notes and chords within randomly generated major or minor keys.

**Be Aware:** The script has been tested to work with Python version 3.9.

## How to use?
First you need to make sure Fluidsynth is installed on your machine. If Fluidsynth isn't installed, the samples won't generate and the execution will fail.
After installing Fluidsynth you can use the following command to install both pretty_midi and soundfont:
```bash
pip install -r requirements.txt
```

Now that all requirements are installed you can run the following command:
```bash
python main.py <total_amount> <path (optional)> 
```
Where the total amount is the amount of samples for a single dataset split 80%, 10% and 10% between train, validation and test respectively. The path will be the directory the "datasets" map is placed in.
