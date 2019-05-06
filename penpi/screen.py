#!/usr/bin/env python3
"""Summary

Attributes:
    A_pin (int): Description
    B_pin (int): Description
    bottom (TYPE): Description
    buttons (dict): Description
    C_pin (int): Description
    commands (TYPE): Description
    D_pin (int): Description
    DC (int): Description
    disp (TYPE): Description
    draw (TYPE): Description
    font (TYPE): Description
    gpio_buttons (TYPE): Description
    height (TYPE): Description
    image (TYPE): Description
    L_pin (int): Description
    logo (TYPE): Description
    padding (int): Description
    R_pin (int): Description
    RST (int): Description
    script_dir (TYPE): Description
    selection (int): Description
    selection_offset (int): Description
    SPI_DEVICE (int): Description
    SPI_PORT (int): Description
    top (TYPE): Description
    U_pin (int): Description
    width (TYPE): Description
    x (int): Description
"""

import time

import RPi.GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
import json
import os
from pathlib import Path

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess
import logging

script_dir = Path(os.path.dirname(os.path.realpath(__file__)))

logo = Image.open('/opt/penpi/logo.ppm').convert('1')
# Input pins:
L_pin = 27 
R_pin = 23 
C_pin = 4 
U_pin = 17 
D_pin = 22 

A_pin = 5 
B_pin = 6 

GPIO.setmode(GPIO.BCM) 

GPIO.setup(A_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(L_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(R_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(B_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(U_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(D_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(C_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Raspberry Pi pin configuration:
RST = 24
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

# 128x64 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)


# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)


# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0


# Load default font.
font = ImageFont.load_default()



commands = None
with open(str(script_dir / "config.json")) as handle:
    commands = json.loads(handle.read())


selection_offset = 0
selection = 0

def render():
    """Summary
    """
    global selection_offset
    global selection

    cur_index = selection

    draw.rectangle((0,0,width,height), outline=0, fill=0)
    
    if selection < selection_offset:
        selection_offset = selection
    elif selection-selection_offset >= 6:
        selection_offset = selection - 5

    y = 0
    for i in range(0,6):
        cmd_index = selection_offset+i

        if cmd_index >= len(commands):
            break

        cmd_title = commands[cmd_index]["name"]

        if cmd_index == cur_index:
            draw.rectangle((0,y,256,y+10), outline=0, fill=255)
            draw.text((0, y), "{}. {}".format(cmd_index+1,cmd_title),  font=font, fill=0)
        else:
            draw.text((0, y), "{}. {}".format(cmd_index+1,cmd_title),  font=font, fill=255)
        y += 10
    

        pos = selection_offset + i

    disp.image(image)
    disp.display()




class Button():

    """Summary
    
    Attributes:
        callbacks (list): Description
        DOWN (TYPE): Description
        UP (TYPE): Description
    """
    
    DOWN = GPIO.LOW
    UP = GPIO.HIGH

    def __init__(self, gpio):
        """Summary
        
        Args:
            gpio (TYPE): Description
        """
        GPIO.add_event_detect(gpio, GPIO.BOTH, callback=lambda b: Button.edge_detected(self), bouncetime=200)

        self.__gpio = gpio
        self.callbacks = []

        self.__state = Button.UP
        self.__pressed = False
        self.__released = False
        self.__edge = False

    def update(self):
        """Summary
        """
        self.check_edge()


        if self.__pressed or self.__released:
            # State changed

            for cb_state, cb_func in self.callbacks:
                if cb_state == self.__state:
                    cb_func(self, self.__state)

            self.clear()


    def addOnPress(self, func):
        """Summary
        
        Args:
            func (TYPE): Description
        """
        self.callbacks.append((Button.DOWN, func))

    def addOnRelease(self, func):
        """Summary
        
        Args:
            func (TYPE): Description
        """
        self.callbacks.append((Button.UP, func))
    
    def clear(self):
        """Summary
        """
        self.__state = Button.UP
        self.__pressed = False
        self.__released = False

    def check_edge(self):
        """Summary
        """
        pass

    def edge_detected(self):
        """Summary
        """
        self.__state = Button.DOWN if self.__state else Button.UP

        if self.__state == Button.UP:
            self.__released = True
        else:
            self.__pressed = True

            

    @property
    def pressed(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        self.check_edge()
        return self.__pressed
    
    @property
    def released(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        self.check_edge()
        return self.__released
    
    @property
    def down(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        self.check_edge()
        return GPIO.input(self.__gpio) == GPIO.LOW

    @property
    def up(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        self.check_edge()
        return GPIO.input(self.__gpio) == GPIO.HIGH

    @property
    def gpio(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        self.check_edge()
        return self.__gpio

    def __repr__(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        return "<Button {}>".format(self.__gpio)

def onPress(button, state):
    """Summary
    
    Args:
        button (TYPE): Description
        state (TYPE): Description
    """
    global selection

    print(button,state)

    if state == Button.DOWN:
        if button.gpio == D_pin:
            selection += 1
        elif button.gpio == U_pin:
            selection -= 1
        elif button.gpio == A_pin:
            executeCommand()

    selection %= len(commands)

    render()      

# Create buttons
gpio_buttons = [A_pin,L_pin,R_pin,B_pin,U_pin,D_pin,C_pin]

buttons = {}

for gpio in gpio_buttons:
    butt = Button(gpio)

    butt.addOnPress(onPress)
    butt.addOnRelease(onPress)
    buttons[gpio] = butt



def executeCommand():
    """Summary
    
    Returns:
        TYPE: Description
    """
    cmd = commands[selection]["command"]
    if not cmd:
        return
    
    if isinstance(cmd, str):
        cmd = ["sh","-c", cmd]

    draw.rectangle((0,0,width,height), outline=0, fill=0)
    draw.text((32, 22), "Executing...",  font=font, fill=255)
    disp.image(image)
    disp.display()

    try:
        output = subprocess.check_output(cmd, universal_newlines=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print("ERROR:", e.output)
        output = e.output

    print(output)

    
    buttons[A_pin].clear()
    buttons[D_pin].clear()
    buttons[U_pin].clear()
    buttons[L_pin].clear()
    buttons[R_pin].clear()
    
    render_output = True
    output_pos = (0,0)
    move_step = 8
    while True:
        if buttons[A_pin].pressed:
            buttons[A_pin].clear()
            break

        if buttons[D_pin].down:
            render_output = True
            output_pos = (output_pos[0],output_pos[1]-move_step)
        elif buttons[U_pin].down:
            render_output = True
            output_pos = (output_pos[0],output_pos[1]+move_step)
    

        if buttons[L_pin].down:
            render_output = True
            output_pos = (output_pos[0]+move_step,output_pos[1])
        elif buttons[R_pin].down:
            render_output = True
            output_pos = (output_pos[0]-move_step,output_pos[1])


        if render_output:
            draw.rectangle((0,0,width,height), outline=0, fill=0)
            draw.multiline_text(output_pos, output,  font=font, fill=255, spacing=-2)
            disp.image(image)
            disp.display()
        
        time.sleep(0.1)

    while not buttons[A_pin].released:
        time.sleep(0.1)

    buttons[A_pin].clear()
    buttons[D_pin].clear()
    buttons[U_pin].clear()
    buttons[L_pin].clear()
    buttons[R_pin].clear()
class Screen():
    def run():
        """Summary
        """
        try:
            disp.image(logo)
            disp.display()


            while not buttons[A_pin].released:
                time.sleep(0.1)
                
            refreshed = False
            start_time = time.time()
            while 1:
                if not refreshed:
                    refreshed = True
                    render()

                for b_gpio, b in buttons.items():
                    b.update()


                time.sleep(.005) 

        except KeyboardInterrupt: 
            GPIO.cleanup()
