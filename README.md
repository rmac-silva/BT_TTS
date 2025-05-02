# Introduction
A simple python script to generate TTS speech based on the Titanfall 2 character BT-7274. The TTS model was shared by [DJMalachite](https://github.com/DJMalachite) and obviously this project wouldn't be possible without his model, so thanks a lot for his work.

Also check out [piper](https://github.com/rhasspy/piper), which is used to generate the speech itself.

## Running
Requirements: Python

1. Download the code, it already comes pre-installed with piper
2. Write the text you want to be synthesized in voicelines.txt, each entry is a sentence.
3. Run main.py

Adittionally you can configure piper's settings in settings.cfg, but I wouldn't change anything, and would keep the default values.

## Performance
The model struggles with certain words, "illuminate", "automaton", "thousand" and has occasional weird pronunciations or weird speech patterns. There's no fix, you can try and tweak the voice lines, add commas or periods to fix speech issues.

### TODO
- Add a Helldivers 2 - Mission Control transcript
- Automate renaming of specific voice-lines, automatic HD2 ID assigning etc...
- UI?
