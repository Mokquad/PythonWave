# PythonWave (Beta)

## Installation

To enable MIDI exporting, you must install the external project dependencies. Clone this repository and run:

```bash
pip install -r requirements.txt
```

## Usage


### Change the output audio filename:
```bash
main.py --save-as my_song.wav
```

### Export to MIDI:
```bash
main.py --midi
```

### Change the output MIDI filename:
```bash
main.py --midi midi.mid
```

### Adjust Tempo (BPM):
```bash
main.py --bpm 137
```

### Example:
```bash
python main.py -s my_song.wav -m midi.mid -b 137
```
