import pygame
import re
import sys
import time
import random
import argparse
import screeninfo
import os
from record_data import RecordData

on_windows = os.name == 'nt'

if on_windows:
    import winsound

parser = argparse.ArgumentParser(description="eeg experiment with pygame visualisation")
parser.add_argument("-t", "--trials"       , help="number of trials"        , default=72   , type=int)
parser.add_argument("-f", "--Fs"           , help="sampling frequency"      , required=True, type=int)
parser.add_argument("-a", "--age"          , help="age of the subject"      , required=True, type=int)
parser.add_argument("-g", "--gender"       , help="gender of the subject"   , required=True)
parser.add_argument("-w", "--with_feedback", help="with additional feedback", type=bool)


args = vars(parser.parse_args())

root_dir  = os.path.join(os.path.dirname(__file__), "..")
image_dir = os.path.join(root_dir, "images")
sound_dir = os.path.join(root_dir, "sounds")


def get_screen_width_and_height():
    monitor_info = screeninfo.get_monitors()[0]
    if not monitor_info:
        sys.exit("couldn't find monitor")
    m = re.match("monitor\((\d+)x(\d+)\+\d+\+\d+\)", str(monitor_info))

    screen_width, screen_height = int(m.group(1)), int(m.group(2))
    return screen_width, screen_height


screen_width, screen_height = get_screen_width_and_height()

black   = (0,   0, 0)
green   = (0, 255, 0)
radius  = 100
mid_pos = (screen_width // 2, screen_height // 2)

pygame.init()
pygame.mixer.init()
pygame.mixer.music.load(os.path.join(sound_dir, "beep.mp3"))

screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
screen.fill(black)

red_arrow       = pygame.image.load(os.path.join(image_dir, "red_arrow.png"))
red_arrow_left  = pygame.transform.rotate(red_arrow, 270)
red_arrow_right = pygame.transform.rotate(red_arrow, 90)

red_arrow_width, red_arrow_height = red_arrow_left.get_size()
red_arrow_right_pos = (screen_width - red_arrow_width, (screen_height - red_arrow_height) // 2)
red_arrow_left_pos  = (0                             , (screen_height - red_arrow_height) // 2)

happy_smiley = pygame.image.load(os.path.join(image_dir, "happy_smiley.png"))
sad_smiley   = pygame.image.load(os.path.join(image_dir, "sad_smiley.png"))

smiley_width, smiley_height = happy_smiley.get_size()
smiley_mid_pos = ((screen_width - smiley_width) // 2, (screen_height - smiley_height) // 2)


def play_beep():
    pygame.mixer.music.play()


def run_trial(record_data, cue_pos_choices, with_feedback=False):
    screen.fill(black)
    pygame.display.update()
    time.sleep(3)

    pygame.draw.circle(screen, green, mid_pos, radius)
    pygame.display.update()
    time.sleep(1)

    # ensure that each cue pos will be equally chosen
    cue_pos = random.choice(list(cue_pos_choices.keys()))
    cue_pos_choices[cue_pos] -= 1
    if cue_pos_choices[cue_pos] == 0:
        del cue_pos_choices[cue_pos]

    if cue_pos == "left":
        screen.blit(red_arrow_left, red_arrow_left_pos)
        record_data.add_trial(1)
    elif cue_pos == "right":
        screen.blit(red_arrow_right, red_arrow_right_pos)
        record_data.add_trial(2)
    elif cue_pos == "both":
        screen.blit(red_arrow_right, red_arrow_right_pos)
        screen.blit(red_arrow_left, red_arrow_left_pos)
        record_data.add_trial(3)
    pygame.display.update()
    time.sleep(0.5)

    if on_windows:
        winsound.Beep(2500, 500)
        time.sleep(3)
    else:
        play_beep()
        time.sleep(4)

    screen.fill(black)
    pygame.display.update()

    if on_windows:
        winsound.Beep(2500, 500)
        time.sleep(1.5)
    else:
        play_beep()
        time.sleep(2)

    if with_feedback:
        one_or_zero = random.choice([0, 1])
        smiley = [sad_smiley, happy_smiley][one_or_zero]
        record_data.add_feedback(one_or_zero)

        screen.blit(smiley, smiley_mid_pos)
        pygame.display.update()
        time.sleep(3)


def run_session(trial_count, Fs, age, gender="male", with_feedback=False):
    if trial_count % 3:
        raise ValueError("'trials' must be devisable by 3")

    trial_count_for_each_cue_pos = trial_count // 3
    cue_pos_choices = {
        "left"  : trial_count_for_each_cue_pos,
        "right" : trial_count_for_each_cue_pos,
        "both"  : trial_count_for_each_cue_pos
    }

    record_data = RecordData(Fs, age, gender, with_feedback)
    record_data.start_recording()

    for trial in range(trial_count):
        run_trial(record_data, cue_pos_choices, with_feedback=with_feedback)

    record_data.stop_recording_and_dump()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    run_session(args['trials'], args["Fs"], args["age"],
                gender=args["gender"], with_feedback=args["with_feedback"])
