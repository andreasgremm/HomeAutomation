import time

import RPi.GPIO as GPIO


class Buzzer(object):
    def __init__(self, buzzer_pin):
        GPIO.setmode(GPIO.BCM)
        self.buzzer_pin = buzzer_pin
        GPIO.setup(self.buzzer_pin, GPIO.OUT)
        GPIO.output(self.buzzer_pin, False)

    def __del__(self):
        class_name = self.__class__.__name__
        GPIO.cleanup()
        print(class_name, "finished")

    def buzz(
        self, pitch, duration
    ):  # create the function 'buzz' and feed it the pitch and duration)

        if pitch == 0:
            time.sleep(duration)
            return
        period = duration
        delay = period
        GPIO.output(self.buzzer_pin, True)
        time.sleep(delay)
        GPIO.output(self.buzzer_pin, False)
        time.sleep(delay)

    def play(self, tune):
        x = 0

        #  print("Playing tune ",tune)
        if tune == 1:
            pitches = [
                262,
                294,
                330,
                349,
                392,
                440,
                494,
                523,
                587,
                659,
                698,
                784,
                880,
                988,
                1047,
            ]
            duration = 0.1
            for p in pitches:
                self.buzz(
                    p, duration
                )  # feed the pitch and duration to the function, 'buzz'
                time.sleep(duration * 0.5)
            for p in reversed(pitches):
                self.buzz(p, duration)
                time.sleep(duration * 0.5)

        elif tune == 2:
            pitches = [262, 330, 392, 523, 1047]
            duration = [0.2, 0.2, 0.2, 0.2, 0.2, 0, 5]
            for p in pitches:
                self.buzz(
                    p, duration[x]
                )  # feed the pitch and duration to the function, 'buzz'
                time.sleep(duration[x] * 0.5)
                x += 1
        elif tune == 3:
            pitches = [
                392,
                294,
                0,
                392,
                294,
                0,
                392,
                0,
                392,
                392,
                392,
                0,
                1047,
                262,
            ]
            duration = [
                0.2,
                0.2,
                0.2,
                0.2,
                0.2,
                0.2,
                0.1,
                0.1,
                0.1,
                0.1,
                0.1,
                0.1,
                0.8,
                0.4,
            ]
            for p in pitches:
                self.buzz(
                    p, duration[x]
                )  # feed the pitch and duration to the func$
                time.sleep(duration[x] * 0.5)
                x += 1

        elif tune == 4:
            pitches = [1047, 988, 659]
            duration = [0.1, 0.1, 0.2]
            for p in pitches:
                self.buzz(
                    p, duration[x]
                )  # feed the pitch and duration to the func$
                time.sleep(duration[x] * 0.5)
                x += 1

        elif tune == 5:
            pitches = [1047, 988, 523]
            duration = [0.1, 0.1, 0.2]
            for p in pitches:
                self.buzz(
                    p, duration[x]
                )  # feed the pitch and duration to the func$
                time.sleep(duration[x] * 0.5)
                x += 1

        elif tune == 6:
            pitches = [1047, 988, 523, 1047, 1047, 1047, 1047, 1047, 1047]
            duration = [0.2, 0.2, 0.2, 0.5, 0.5, 0.5, 0.2, 0.2, 0.2]
            for p in pitches:
                self.buzz(
                    p, duration[x]
                )  # feed the pitch and duration to the func$
                time.sleep(duration[x] * 0.5)
                x += 1
