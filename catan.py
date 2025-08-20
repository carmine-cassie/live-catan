import time
import random
import sys
import os

players = ["Player 1", "Player 2", "Player 3", "Player 4"]

while True:
    d1 = random.randint(1, 6)
    d2 = random.randint(1, 6)
    print(f"{d1}+{d2}={d1+d2}")

    if d1+d2 == 7:
        print(f"{players[random.randint(0, len(players) - 1)]} places the robber...")

    os.system("paplay bell.wav")

    if d1+d2 == 7:
        input()
    else:
        time.sleep(16)
