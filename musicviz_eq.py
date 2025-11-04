import numpy as np
import sounddevice as sd
from rich.console import Console
from rich.live import Live
import shutil, time

SAMPLE_RATE = 44100
BLOCK_SIZE = 2048
BANDS = 64   # make it wide
REFRESH = 1/30

console = Console()
queue = []

# change this to your "loopback" device number from `python -m sounddevice`
DEVICE_INDEX = 4  # example: 5
CHANNELS = 1  # or 1 if your loopback device shows (1 in, 0 out)


def audio_callback(indata, frames, time_info, status):
    if status:
        console.log(status)
    mono = np.mean(indata, axis=1)
    queue.append(mono)

def main():
    width = shutil.get_terminal_size().columns
    with sd.InputStream(
        device=DEVICE_INDEX,
        channels=CHANNELS,
        samplerate=SAMPLE_RATE,
        blocksize=BLOCK_SIZE,
        dtype="float32",
        callback=audio_callback
    ):
        with Live("", refresh_per_second=30, screen=False) as live:
            while True:
                if queue:
                    audio = queue.pop(0)
                    fft = np.abs(np.fft.rfft(audio))
                    bands = np.logspace(1, np.log10(len(fft)), num=BANDS, dtype=int)
                    values = [np.mean(fft[bands[i-1]:bands[i]]) for i in range(1, len(bands))]
                    values = np.log10(np.array(values) + 1) * 8
                    values = np.clip(values, 0, 25).astype(int)

                    # horizontal equalizer bars
                    lines = []
                    max_h = np.max(values)
                    for row in range(max_h, 0, -1):
                        line = "".join("█" if v >= row else " " for v in values)
                        lines.append(line[:width])
                    live.update("\n".join(lines))
                time.sleep(REFRESH)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
