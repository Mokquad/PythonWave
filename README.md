# PythonWave

## Installation

To enable MIDI exporting, you must install the external project dependencies. Clone this repository and run:

```bash
pip install -r requirements.txt
```

## Usage


### Save with a specified filename:
```bash
python main.py --save-as my_song.wav
```

### Export to MIDI:
```bash
python main.py --midi
```

### Export to MIDI with a specified filename:
```bash
python main.py --midi midi.mid
```

### Adjust Tempo (BPM):
```bash
python main.py --bpm 137
```

### Example:
```bash
python main.py -s my_song.wav -m midi.mid -b 137
```
