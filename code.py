# Example code for the CRCibernetica RP2040 MacroPad
# Keycodes https://docs.circuitpython.org/projects/hid/en/latest/api.html#adafruit_hid.keycode.Keycode
# Consumer Control Codes https://docs.circuitpython.org/projects/hid/en/latest/api.html#adafruit_hid.consumer_control_code.ConsumerControlCode
# Mouse Codes https://docs.circuitpython.org/projects/hid/en/latest/api.html#adafruit_hid.mouse.Mouse

import board
import digitalio
import rotaryio
import neopixel
import keypad
from adafruit_hid.keycode import Keycode as K
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode as C
from adafruit_hid.mouse import Mouse
import usb_hid
from rainbowio import colorwheel

sw_rot_pin = board.GP23
rot_a_pin = board.GP24
rot_b_pin = board.GP25

cc = ConsumerControl(usb_hid.devices)
kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(kbd)
m = Mouse(usb_hid.devices)
encoder = rotaryio.IncrementalEncoder(rot_b_pin, rot_a_pin, divisor=4)

key_pins = (
            sw_rot_pin, board.GP1, board.GP11, board.GP21,
                        board.GP2, board.GP10, board.GP20,
                        board.GP4, board.GP8,  board.GP19,
                        board.GP5, board.GP7,  board.GP18
            )

keys = keypad.Keys(key_pins, value_when_pressed=False, pull=True)

OFF = (0,0,0)
pixels = neopixel.NeoPixel(board.GP28, 1, brightness=0.1)
pixels[0] = OFF

# Combine keycodes (Left Shift + Windows Key + s == Windows Screenshot)
screenshot = (K.LEFT_SHIFT, K.LEFT_GUI, K.S,)
# Use a text string or ascii_art
text_string = 'Hello World'
ascii_art = '''
           ___
     |     | |
    / \    | |
   |--o|===|-|
   |---|   | |
  /     \  | |
 |       | | |
 |       |=| |
 |       | | |
 |_______| |_|
  |@| |@|  | |
___________|_|_
'''

# Rotary Encoding mapping for the 3 layers
# Counter clockwise and clockwise
# direct commands can also be sent
encoder_map = {
    0:[(C.VOLUME_DECREMENT,), (C.VOLUME_INCREMENT,)],
    1:[(C.BRIGHTNESS_DECREMENT,), (C.BRIGHTNESS_INCREMENT,)],
    2:['m.move(wheel=-1)', 'm.move(wheel=1)']
    }

# Keymapping for the encoder button and 12 keys
# Three layers have been defined as an example
# Clicking on the encoder button switches through the layers
# The K.LEFT_ALT was chosen for the encoder button because it has no effect
# Perhaps a higher number Function Key could be used as well
keymap = {
    0:[
        (K.LEFT_ALT,), (K.KEYPAD_SEVEN,),   (K.KEYPAD_EIGHT,),   (K.KEYPAD_NINE,),
                       (K.KEYPAD_FOUR,),    (K.KEYPAD_FIVE,),    (K.KEYPAD_SIX,),
                       (K.KEYPAD_ONE,),     (K.KEYPAD_TWO,),     (K.KEYPAD_THREE,),
                       (K.KEYPAD_ZERO,),    screenshot,          (K.KEYPAD_ENTER,),
        ],
    1:[
        (K.LEFT_ALT,), ascii_art,  (K.TWO,),   (K.THREE,),
                       (K.FOUR,),  (K.FIVE,),  (K.SIX,),
                       (K.SEVEN,), (K.EIGHT,), (K.NINE,),
                       (K.ZERO,),  (K.ONE,),   (K.TWO,),
        ],
    2:[
        (K.LEFT_ALT,), text_string,(K.TWO,),   (K.THREE,),
                       (K.FOUR,),  (K.FIVE,),  (K.SIX,),
                       (K.SEVEN,), (K.EIGHT,), (K.NINE,),
                       (K.ZERO,),  (K.ONE,),   (K.TWO,),
        ],
    }

# Layer colors 0-2
layer_colors = [0, 75, 150]

layer = 0
last_position = 0

while True:
    pixels[0] = colorwheel(layer_colors[layer])

    event = keys.events.get()
    if event:
        if event.pressed and event.key_number == 0: # Encoder button clicked
            layer += 1
            if layer > 2:
                layer = 0
        elif event.pressed: # Any other key pressed
            k = keymap[layer][event.key_number]
            if isinstance(k, str):
                layout.write(k)
            else:
                kbd.send(*k)
 
    position = encoder.position
    if position != last_position: # Checks if the rotary encoder has moved
        if last_position - position > 0 and layer == 2:
            exec(encoder_map[2][0])
        elif last_position - position < 0 and layer == 2:
            exec(encoder_map[2][1])
        elif last_position - position < 0:
            cc.send(*encoder_map[layer][0])
        elif last_position - position > 0:
            cc.send(*encoder_map[layer][1])
        last_position = position