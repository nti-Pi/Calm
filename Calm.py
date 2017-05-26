# Nikhil Tony Idiculla, 2017
# All rights reserved.
#
# Contact me:
#   EMAIL:  nikhilidiculla@gmail.com
#   GITHUB: https://github.com/nti-Pi

import sys

from pyglet import app
from pyglet import clock
from pyglet import window
from pyglet import text
from pyglet import event
from pyglet import image

from pyglet.window import key
from pyglet.gl import glClearColor, glClear, GL_COLOR_BUFFER_BIT

fs = True
if len(sys.argv) > 1:
    if sys.argv[1] == '--windowed' or sys.argv[1] == '-w':
        fs = False

    else:
        print('WARNING: Invalid command line flags. Only accepts "-w" OR "--windowed"',
              file=sys.stderr)

CalmWindow = window.Window(fullscreen=fs)


Color_Mauve = (163, 149, 154)
Color_Tan = (206, 174, 157)
Color_DeepBlue = (103, 108, 143)
Color_MistGray = (179, 180, 177)
Color_Coral = (248, 152, 152)
Color_Green = (195, 210, 205)
Color_Teal = (19, 171, 172)

Cycle_Colors = [
    Color_Mauve,
    Color_Tan,
    Color_DeepBlue,
    Color_MistGray,
    Color_Coral,
    Color_Green,
    Color_Teal
]

Cycle_ColorIndex = 0
Cycle_CurrColor = Cycle_Colors[Cycle_ColorIndex]
Cycle_NextColor = Cycle_Colors[Cycle_ColorIndex + 1 % len(Cycle_Colors)]

Cycle_DisplayColor = Cycle_CurrColor

Title = text.Label(text='Calm.',
                   font_size=108, font_name='Georgia',
                   color=(0, 0, 0, 128),
                   x=CalmWindow.width // 2, y=0.5 * CalmWindow.height,
                   anchor_x='center', anchor_y='bottom',
                   bold=True)

Instructions = text.Label(text='Hit Escape to exit.',
                          font_size=36, font_name='Georgia',
                          color=(0, 0, 0, 128),
                          x=CalmWindow.width // 2, y=0.4 * CalmWindow.height,
                          anchor_x='center', anchor_y='bottom')


def interpolate_color(color_a, color_b, x):
    return (
        color_a[0] * (1 - x) + color_b[0] * x,
        color_a[1] * (1 - x) + color_b[1] * x,
        color_a[2] * (1 - x) + color_b[2] * x
    )


def increment_color():
    global Cycle_ColorIndex
    global Cycle_Colors
    global Cycle_CurrColor
    global Cycle_NextColor

    Cycle_ColorIndex = (Cycle_ColorIndex + 1) % len(Cycle_Colors)
    Cycle_CurrColor = Cycle_NextColor
    Cycle_NextColor = Cycle_Colors[(Cycle_ColorIndex + 2) % len(Cycle_Colors)]


class BaseState(object):
    Timer = 0

    def __new__(cls):
        raise Exception('Cannot instantiate a state class.')

    @staticmethod
    def activate(left_over_time):
        pass

    @staticmethod
    def de_activate():
        pass

    @staticmethod
    def execute(dt):
        pass


class StartState(BaseState):
    Duration = 1

    @staticmethod
    def activate(left_over_time):
        clock.schedule(StartState.execute)

    @staticmethod
    def execute(dt):
        global Cycle_DisplayColor

        StartState.Timer += dt

        if StartState.Timer >= StartState.Duration:
            StartState.de_activate()
            TransitionState.activate(StartState.Timer - StartState.Duration)

        else:
            Cycle_DisplayColor = interpolate_color((0, 0, 0), Cycle_CurrColor, StartState.Timer / StartState.Duration)

    @staticmethod
    def de_activate():
        clock.unschedule(StartState.execute)


class HoldState(BaseState):
    Duration = 8

    @staticmethod
    def activate(left_over_time):
        global Cycle_DisplayColor

        clock.schedule(HoldState.execute)

        # Carrying any remaining time over to the hold timer:
        HoldState.Timer = left_over_time

        # Setting the new current color:
        increment_color()
        Cycle_DisplayColor = Cycle_CurrColor

    @staticmethod
    def execute(dt):
        HoldState.Timer += dt

        if HoldState.Timer >= HoldState.Duration:
            HoldState.de_activate()

            left_over = HoldState.Timer - HoldState.Duration
            HoldState.Timer = 0
            TransitionState.activate(left_over)

    @staticmethod
    def de_activate():
        clock.unschedule(HoldState.execute)


class TransitionState(BaseState):
    Duration = 2

    @staticmethod
    def activate(left_over_time):
        clock.schedule(TransitionState.execute)

        # Carrying any remaining time over to the transition timer:
        TransitionState.Timer = left_over_time

    @staticmethod
    def execute(dt):
        global Cycle_DisplayColor

        TransitionState.Timer += dt

        if TransitionState.Timer >= TransitionState.Duration:
            TransitionState.de_activate()

            left_over = TransitionState.Timer - TransitionState.Duration
            TransitionState.Timer = 0

            HoldState.activate(left_over)

        else:
            Cycle_DisplayColor = interpolate_color(Cycle_CurrColor, Cycle_NextColor,
                                                   TransitionState.Timer / TransitionState.Duration)

    @staticmethod
    def de_activate():
        clock.unschedule(TransitionState.execute)


@CalmWindow.event
def on_draw():
    glClearColor(Cycle_DisplayColor[0] / 255,
                 Cycle_DisplayColor[1] / 255,
                 Cycle_DisplayColor[2] / 255,
                 1.0)

    glClear(GL_COLOR_BUFFER_BIT)

    CalmWindow.clear()

    Title.draw()
    Instructions.draw()

    return event.EVENT_HANDLED


@CalmWindow.event
def on_key_press(symbol, modifiers):
    global Cycle_CurrColor

    if symbol == key.ESCAPE:
        # HACK
        Cycle_CurrColor = Cycle_DisplayColor

        clock.unschedule(TransitionState.execute)
        clock.unschedule(HoldState.execute)

        dim_duration = 0.5
        dim_timer = 0.0

        def dim(dt):
            global Cycle_DisplayColor
            nonlocal dim_timer

            dim_timer += dt

            if dim_timer >= dim_duration:
                app.exit()

            else:
                Cycle_DisplayColor = interpolate_color(Cycle_CurrColor, (0, 0, 0), dim_timer / dim_duration)

        clock.schedule(dim)

    return event.EVENT_HANDLED


if __name__ == '__main__':
    # Setting the cursor:
    image = image.load('cursor.png')
    cursor = window.ImageMouseCursor(image, 16, 16)
    CalmWindow.set_mouse_cursor(cursor)

    StartState.activate(0)
    app.run()
