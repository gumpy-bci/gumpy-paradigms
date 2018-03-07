from math import pi, sin, cos
import random
import sys
import argparse

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor

from record_data import RecordData

class MyApp(ShowBase):
    def __init__(self, trial_count, Fs, age, gender="male"):
        ShowBase.__init__(self)

        if trial_count % 3:
            raise ValueError("'trials' must be devisable by 3")

        trial_count_for_each_cue_pos = trial_count // 3

        # Generating position list
        self.pos_choices = ["fist", "pinch_2", "pinch_3"]

        self.cue_pos_choices = [x for pair in zip(self.pos_choices*trial_count_for_each_cue_pos) for x in pair]

        print(self.cue_pos_choices)

        # Randomizing the positions
        random.shuffle(self.cue_pos_choices)

        #Add of a position to avoid data loss
        self.cue_pos_choices.append('end')




        self.record_data = RecordData(Fs, age, gender, with_feedback=False)
        self.record_data.start_recording()


        # Load the environment model.
        #self.scene = self.loader.loadModel("models/environment")
        # Reparent the model to render.
        #self.scene.reparentTo(self.render)
        # Apply scale and position transforms on the model.
        #self.scene.setScale(0.25, 0.25, 0.25)
        #self.scene.setPos(-8, 42, 0)


        # Add the spinCameraTask procedure to the task manager.
        self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")

        # Add the run_trial procedure to the task manager
        self.taskMgr.add(self.run_trial, "run_trial_task")

        # Load and transform the panda actor.
        self.pandaActor = Actor("models/Hand")

        scale = 10
        self.pandaActor.setScale(scale, scale, scale)
        self.pandaActor.reparentTo(self.render)

        self.pandaActor.setPos(7.9, 1.5, -14.5)

        #self.camera.setPos(0, 0, 0)
        #self.camera.setHpr(225, 0, 0)

        #base.disableMouse()
        #base.useDrive()
        #base.oobe()

    # Define a procedure to move the camera.
    def spinCameraTask(self, task):
        angleDegrees = 205#20 * task.time * 6.0
        theta = 20
        angleRadians = angleDegrees * (pi / 180.0)
        thetaRad = theta * (pi / 180.0)
        self.camera.setPos(3.5*sin(angleRadians), -3.5*cos(angleRadians), -3.5*sin(thetaRad))
        self.camera.setHpr(angleDegrees, theta, 0)

        return task.cont

    def run_trial(self, task):
        if task.time < 10.0:
            return task.cont

        try:
            pos = self.cue_pos_choices.pop(0)
        except IndexError:
            self.record_data.stop_recording_and_dump()
            base.destroy()
            sys.exit()
            return task.done

        if pos is not 'end':

            self.pandaActor.play(pos)
            self.record_data.add_trial(self.pos_choices.index(pos))

            print(self.cue_pos_choices)

        return task.again


parser = argparse.ArgumentParser(description="eeg experiment with pygame visualisation")
parser.add_argument("-t", "--trials"       , help="number of trials"        , default=72   , type=int)
parser.add_argument("-f", "--Fs"           , help="sampling frequency"      , required=True, type=int)
parser.add_argument("-a", "--age"          , help="age of the subject"      , required=True, type=int)
parser.add_argument("-g", "--gender"       , help="gender of the subject"   , required=True)
parser.add_argument("-w", "--with_feedback", help="with additional feedback", type=bool)


args = vars(parser.parse_args())

app = MyApp(args['trials'], args["Fs"], args["age"],
            gender=args["gender"])
app.run()
