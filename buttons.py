import gpiod
import requests
import time

FLASK_URL = "http://127.0.0.1:5000"

PREV_PIN = 17
PLAY_PIN = 27
NEXT_PIN = 22

CLK_PIN = 5
DT_PIN = 6
SW_PIN = 13

def handle_button(pin):
    if pin == PREV_PIN:
        requests.post(f"{FLASK_URL}/api/previous")
        print("Previous")
    elif pin == PLAY_PIN:
        requests.post(f"{FLASK_URL}/api/playpause")
        print("Play/Pause")
    elif pin == NEXT_PIN:
        requests.post(f"{FLASK_URL}/api/next")
        print("Next")

def get_volume():
    try:
        res = requests.get(f"{FLASK_URL}/api/playback")
        data = res.json()
        return data.get("volume", 50)
    except Exception:
        return 50

with gpiod.request_lines(
    '/dev/gpiochip0',
    consumer="buttons",
    config={
        (PREV_PIN, PLAY_PIN, NEXT_PIN, CLK_PIN, DT_PIN, SW_PIN): gpiod.LineSettings(
            direction=gpiod.line.Direction.INPUT,
            bias=gpiod.line.Bias.PULL_UP,
        )
    }
) as request:
    print("Button listener running...")

    last_buttons = {PREV_PIN: 1, PLAY_PIN: 1, NEXT_PIN: 1, SW_PIN: 1}
    last_clk = request.get_value(CLK_PIN)
    volume = get_volume()

    while True:
        # Handle buttons
        for pin in [PREV_PIN, PLAY_PIN, NEXT_PIN]:
            val = request.get_value(pin)
            int_val = 0 if val == gpiod.line.Value.INACTIVE else 1
            if int_val == 0 and last_buttons[pin] == 1:
                handle_button(pin)
                time.sleep(0.3)
            last_buttons[pin] = int_val

        # Handle rotary encoder
        clk = request.get_value(CLK_PIN)
        dt = request.get_value(DT_PIN)

        clk_val = 0 if clk == gpiod.line.Value.INACTIVE else 1
        dt_val = 0 if dt == gpiod.line.Value.INACTIVE else 1
        last_clk_val = 0 if last_clk == gpiod.line.Value.INACTIVE else 1

        if clk_val != last_clk_val:
            time.sleep(0.005)  # wait for bounce to settle

            # re-read after settling
            clk = request.get_value(CLK_PIN)
            dt = request.get_value(DT_PIN)
            clk_val = 0 if clk == gpiod.line.Value.INACTIVE else 1
            dt_val = 0 if dt == gpiod.line.Value.INACTIVE else 1

            if clk_val == 0:  # only act on falling edge
                if dt_val == 1:
                    volume = min(100, volume + 5)  # clockwise
                    print(f"Volume up: {volume}")
                else:
                    volume = max(0, volume - 5)   # counter-clockwise
                    print(f"Volume down: {volume}")
                try:
                    requests.post(f"{FLASK_URL}/api/volume", json={"volume": volume})
                except Exception:
                    pass
                time.sleep(0.1)  # debounce delay after action

        last_clk = clk
        time.sleep(0.001)