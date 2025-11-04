import os
import time
import random
import shutil
import numpy as np
from rich.console import Console
from rich.live import Live
from rich.text import Text

console = Console()

FLAME_CHARS  = [" ", "░", "▒", "▓", "█"]
FLAME_COLORS = ["#1a0d00", "#802b00", "#cc5500", "#ff7b00", "#ffd966"]

REFRESH = 0.1
SPARK_CHANCE = 0.91   
DECAY = 0.98
RISE = 2              
COLUMN_VAR = 0.2     

def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")

def main():
    clear_terminal()
    width, height = shutil.get_terminal_size()
    height = int(height * 1.1)
    heat = np.zeros((height, width))

    with Live("", refresh_per_second=int(1 / REFRESH), screen=False) as live:
        while True:
            heat[:-RISE] = heat[RISE:]
            heat[-RISE:] = 0

            base_noise = np.clip(
                np.random.rand(RISE, width) +
                np.roll(np.random.rand(RISE, width), 1, axis=1) * COLUMN_VAR,
                0, 1
            )
            mask = (np.random.rand(RISE, width) < SPARK_CHANCE).astype(float)
            heat[-RISE:] = base_noise * mask

            heat *= DECAY
            heat = (heat + np.roll(heat, 1, axis=1) + np.roll(heat, -1, axis=1)) / 3

            text = Text()
            for y in range(height):
                for x in range(width):
                    v = max(0.0, min(1.0, heat[y, x]))
                    ci = min(len(FLAME_COLORS) - 1, int(v * len(FLAME_COLORS)))
                    ch = min(len(FLAME_CHARS) - 1, int(v * len(FLAME_CHARS)))
                    text.append(FLAME_CHARS[ch], style=FLAME_COLORS[ci])
                text.append("\n")

            live.update(text)
            time.sleep(REFRESH)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
