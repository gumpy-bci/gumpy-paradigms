import pygame
import re
import sys
import time
import screeninfo
import os
import numpy as np
import argparse
import random
from record_data import RecordData

parser = argparse.ArgumentParser(description="eeg experiment with pygame visualisation")
parser.add_argument("-t", "--trials"       , help="number of trials"        , default=48   , type=int)
parser.add_argument("-f", "--Fs"           , help="sampling frequency"      , default=512  , type=int)
parser.add_argument("-a", "--age"          , help="age of the subject"      , required=True, type=int)
parser.add_argument("-g", "--gender"       , help="gender of the subject"   , required=True)
parser.add_argument("-w", "--with_feedback", help="with additional feedback", type=bool)

args = vars(parser.parse_args())

TRAVELING_TIME = 8.0

ROOT_DIR  = os.path.join(os.path.dirname(__file__), "..")
IMAGE_DIR = os.path.join(ROOT_DIR, "images")

ON_WINDOWS = os.name == 'nt'
if ON_WINDOWS:
    import winsound


def get_screen_width_and_height():
    monitor_info = screeninfo.get_monitors()[0]
    if not monitor_info:
        sys.exit("couldn't find monitor")
    m = re.match("monitor\((\d+)x(\d+)\+\d+\+\d+\)", str(monitor_info))

    SCREEN_WIDTH, SCREEN_HEIGHT = int(m.group(1)), int(m.group(2))
    return SCREEN_WIDTH, SCREEN_HEIGHT


SCREEN_WIDTH, SCREEN_HEIGHT = get_screen_width_and_height()

CENTER_X = SCREEN_WIDTH // 2
CENTER_Y = SCREEN_HEIGHT // 2

BLACK  = (  0,   0, 0)
YELLOW = (255, 255, 0)
GREEN  = (  0, 255, 0)
RED    = (255, 0  , 0)

pygame.init()
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
# SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
SCREEN.fill(BLACK)

CLOCK = pygame.time.Clock()


class Circle():
    def __init__(self, x, y, radius=50, color=YELLOW):
        self.x      = x
        self.y      = y
        self.color  = color
        self.radius = radius

        self.initial_color  = color

        self.rect = pygame.draw.circle(SCREEN, color, [x, y], radius)

    def reset(self):
        self.color = self.initial_color

    def update(self, dt):
        self.rect = pygame.draw.circle(SCREEN, self.color, [self.x, self.y], self.radius)

    def get_coords(self):
        return self.x, self.y


class Cursor():
    def __init__(self, color=GREEN, radius=25):
        self.initial_color = color
        self.radius        = radius
        self.x             = 0
        self.y             = 0

        self.target_x = 0
        self.target_y = 0

        self.changed_state = time.time()

        self.change_state("reseted")

        self.reset()

    def reset(self):
        self.color = self.initial_color
        self.change_state("reseted")
        self.x     = CENTER_X
        self.y     = CENTER_Y
        self.update(0)

    def update(self, dt):
        if self.state == "moving":
            self.move(dt)
        if self.state == "reached_destination":
            self.color = RED

        self.rect = pygame.draw.rect(
            SCREEN, self.color, [
                self.x - self.radius, self.y - self.radius,
                self.radius * 2, self.radius * 2
            ],
        )

    def change_state(self, state):
        self.changed_state = time.time()
        self.state = state

    def move_to(self, x, y):
        self.change_state("moving")
        self.target_x = x
        self.target_y = y

    def move(self, dt):
        if self.target_x == self.x and self.target_y == self.y:
            self.change_state("reached_destination")

        distance_x = self.target_x - self.x
        distance_y = self.target_y - self.y

        time_left = TRAVELING_TIME + self.changed_state - time.time()

        vel_x = distance_x / time_left
        vel_y = distance_y / time_left

        if distance_x != 0:
            self.x += int(round(dt * vel_x))
        if distance_y != 0:
            self.y += int(round(dt * vel_y))

        new_distance_x = self.target_x - self.x
        if np.sign(new_distance_x) != np.sign(distance_x) or time_left <= 0:
            self.x = self.target_x

        new_distance_y = self.target_y - self.y
        if np.sign(new_distance_y) != np.sign(distance_y) or time_left <= 0:
            self.y = self.target_y


def spawn_circles(radius=400):
    return [
        # top
        Circle(CENTER_X - radius, CENTER_Y - radius),
        Circle(CENTER_X + radius, CENTER_Y - radius),

        # center
        Circle(CENTER_X - radius, CENTER_Y),
        Circle(CENTER_X + radius, CENTER_Y),

        # bottom
        Circle(CENTER_X - radius, CENTER_Y + radius),
        Circle(CENTER_X + radius, CENTER_Y + radius)
    ]


class GreenArrow():
    def __init__(self):
        self.image = pygame.image.load(os.path.join(IMAGE_DIR, "green_arrow.png"))

    def draw(self, point_to_x, point_to_y):
        angle = (np.arctan2(point_to_x - CENTER_X, point_to_y - CENTER_Y) + np.pi) / np.pi * 180.0

        rotated_arrow = pygame.transform.rotate(self.image, angle)

        width, height = rotated_arrow.get_size()
        SCREEN.blit(rotated_arrow, [CENTER_X - width // 2, CENTER_Y - height // 2])


cursor = Cursor()

circles = spawn_circles()
game_objects = circles + [cursor]

green_arrow = GreenArrow()


def render():
    dt = CLOCK.tick(60.0) / 1000.0
    SCREEN.fill(BLACK)

    for game_object in game_objects:
        game_object.update(dt)

    pygame.display.update()


def run_trial(record_data, cue_pos_choices):
    render()
    time.sleep(2)

    # ensure that each cue pos will be equally chosen
    i_random = random.choice(list(cue_pos_choices.keys()))
    cue_pos_choices[i_random] -= 1
    if cue_pos_choices[i_random] == 0:
        del cue_pos_choices[i_random]

    random_circle = circles[i_random]
    random_circle.color = GREEN
    render()

    x, y = random_circle.get_coords()
    cursor.move_to(x, y)

    record_data.add_trial(i_random)

    if ON_WINDOWS:
        winsound.Beep(1000, 70)

    while cursor.state == "moving":
        render()

    green_arrow.draw(x, y)
    pygame.display.update()

    time.sleep(3)

    if ON_WINDOWS:
        winsound.Beep(1000, 70)

    for game_object in game_objects:
        game_object.reset()

    render()
    time.sleep(2)


def run_session():
    n_trials = args['trials']

    if n_trials % 3:
        raise ValueError("'trials' must be devisable by 6")

    n_trials_for_each_cue_pos = n_trials // 6

    cue_pos_choices = {
        0 : n_trials_for_each_cue_pos,
        1 : n_trials_for_each_cue_pos,
        2 : n_trials_for_each_cue_pos,
        3 : n_trials_for_each_cue_pos,
        4 : n_trials_for_each_cue_pos,
        5 : n_trials_for_each_cue_pos
    }

    record_data = RecordData(args['Fs'], args['age'], args['gender'], args['with_feedback'])
    record_data.start_recording()

    for i_trial in range(n_trials):
        run_trial(record_data, cue_pos_choices)

    record_data.stop_recording_and_dump()
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    run_session()
