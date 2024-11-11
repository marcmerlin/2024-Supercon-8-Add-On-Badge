# You can test the code for syntax before upload with pylint

import time
import neopixel

counter = 0
overlay = [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ]

############################################################
#
# Neopixels

print("Neopixel init.")

# port 1 on branch 5
NP_pin = gpio51
NP_count = 12
np = neopixel.NeoPixel(NP_pin, NP_count)
# normally neopixel object has a brightness method, but
# this one does not seem to.
brightness = 0.25

# neopixel Boot init
for i in range(2 * NP_count):
    for j in range(NP_count):
        np[j] = (0, 0, 0)
    np[i % NP_count] = (255, 255, 255)
    np.write()
    time.sleep_ms(25)

    # clear
    for i in range(NP_count):
        np[i] = (0, 0, 0)
    np.write()

def np_dim(value):
    return(int(value * brightness))

wheel_white_idx = 0
def wheel(pos):
    global wheel_white_idx

    wheel_white_idx +=1
    # be off by one on purpose to cycle the white pixel
    if wheel_white_idx > NP_count:
        wheel_white_idx = 0

    if (wheel_white_idx == 0): return(0, 0, 0)

    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return(np_dim(r), np_dim(g), np_dim(b))
 
print("Neopixel init done.")


############################################################
#
# Duck SAO

duck_id = 0x6c
# https://taunoerik.art/2023/08/05/programming-ch32v003/
duck_bus = None
duck_counter = 0
while not duck_bus:
    try:
        duck_bus =  which_bus_has_device_id(duck_id)[0]
    except:
        pass
    time.sleep_ms(100)
    duck_counter = duck_counter + 1
    if duck_counter > 10:
        break
if not duck_bus:
    print(f"Warning: Duck not found!")
else:
    print("Duck found, sending color init.")
    # https://github.com/astuder/duckglow
    duck_bus.writeto_mem(duck_id, 0xF0, bytes([0x01]))
    duck_bus.writeto_mem(duck_id, 0xF1, bytes([0x01]))
    duck_bus.writeto_mem(duck_id, 0xF2, bytes([0x01]))
    duck_bus.writeto_mem(duck_id, 0xEC, bytes([0xff]))
    duck_bus.writeto_mem(duck_id, 0xEE, bytes([0xff]))
    duck_bus.writeto_mem(duck_id, 0xED, bytes([0xff]))
    duck_bus.writeto_mem(duck_id, 0xF4, bytes([0x10]))
    duck_bus.writeto_mem(duck_id, 0xF5, bytes([0x25]))
    duck_bus.writeto_mem(duck_id, 0xF6, bytes([0x33]))


############################################################

# code to run often during petal updates

rainbow_index = 0
def rainbow_cycle():
    global rainbow_index

    rainbow_index = rainbow_index + 11
    j = rainbow_index
    for i in range(NP_count):
        pixel_index = (i * 256 // NP_count) + j
        np[i] = wheel(pixel_index & 255)
    np.write()




sleep_time = 40
red = 0
green = 0
blue = 0
new_red = red
new_green = green
new_blue = blue

# This gets called in between petal updates for faster response
def update_input():
    global red, green, blue, new_red, new_green, new_blue
    global brightness

    if not buttonA.value():
        if not red:
            new_red = 1
            print("red Pushed, Setting brightness to 10%")
            brightness = 0.1
    else:
        if red:
            new_red = 0
            print("red released")

    if not buttonB.value():
        if not green:
            new_green = 1
            print("green Pushed, Setting brightness to 30%")
            brightness = 0.3
    else:
        if green:
            new_green = 0
            print("green released")

    if not buttonC.value():
        if not blue:
            new_blue = 1
            print("blue Pushed, Setting brightness to 75%")
            brightness = 0.75
    else:
        if blue:
            new_blue = 0
            print("blue released")

    if duck_bus:
        if red != new_red:
            if new_red:
                # turn off blue and green
                print("red pushed to duck")
                duck_bus.writeto_mem(duck_id, 0xF0, bytes([0x80]))
                duck_bus.writeto_mem(duck_id, 0xED, bytes([0x02]))
                duck_bus.writeto_mem(duck_id, 0xEE, bytes([0x02]))
            else:
                print("duck back from red to all")
                duck_bus.writeto_mem(duck_id, 0xF0, bytes([0x00]))
                duck_bus.writeto_mem(duck_id, 0xED, bytes([0xFF]))
                duck_bus.writeto_mem(duck_id, 0xEE, bytes([0xFF]))

        if green != new_green:
            if new_green:
                # turn off green and blue
                print("green pushed to duck")
                duck_bus.writeto_mem(duck_id, 0xF1, bytes([0x80]))
                duck_bus.writeto_mem(duck_id, 0xEC, bytes([0x02]))
                duck_bus.writeto_mem(duck_id, 0xEE, bytes([0x02]))
            else:
                print("duck back from green to all")
                duck_bus.writeto_mem(duck_id, 0xF1, bytes([0x00]))
                duck_bus.writeto_mem(duck_id, 0xEC, bytes([0xFF]))
                duck_bus.writeto_mem(duck_id, 0xEE, bytes([0xFF]))

        if blue != new_blue:
            if new_blue:
                # turn off red and green
                print("blue pushed to duck")
                duck_bus.writeto_mem(duck_id, 0xF2, bytes([0x80]))
                duck_bus.writeto_mem(duck_id, 0xEC, bytes([0x02]))
                duck_bus.writeto_mem(duck_id, 0xED, bytes([0x02]))
            else:
                print("duck back from blue to all")
                duck_bus.writeto_mem(duck_id, 0xF2, bytes([0x00]))
                duck_bus.writeto_mem(duck_id, 0xEC, bytes([0xFF]))
                duck_bus.writeto_mem(duck_id, 0xED, bytes([0xFF]))

    global sleep_time
    ## see what's going on with the touch wheel
    if touchwheel_bus:
        tw = touchwheel_read(touchwheel_bus)

        # 1 can be a false reading, ignore it
        if tw > 1:
            tw2 = (256 - tw + 90) % 256
            sleep_time = int(tw2/3) + 1
            #print("Got wheel %d -> %d, updating sleep_time to %d" % (tw, tw2,  sleep_time))


petal_update_idx = 0
petal_update_dir = 1

def petal_cycle():
    global petal_update_idx, petal_update_dir

    if petal_bus:
        if new_red:
            overlay[3] = 0x80
        else:
            overlay[3] = 0

        if new_green:
            if counter % 3 == 0:
                overlay[4] = 0x80
            else:
                overlay[4] = 0
        else:
            overlay[4] = 0

        if new_blue:
            if counter % 3 == 0:
                overlay[2] = 0x80
            else:
                overlay[2] = 0
        else:
            overlay[2] = 0

        # each petal has 7 LEDs and the 8th one is the RGB in the center (0x80)
        which_leds = (1 << petal_update_idx)

        # Go through 8 petals:
        for i in range(1,9):
            which_leds2 = which_leds
            which_leds2 += overlay[i]
            #print (str(i) + ": " + str(which_leds2))
            petal_bus.writeto_mem(PETAL_ADDRESS, i, bytes([which_leds2]))

        petal_update_idx += petal_update_dir
        # 7 leds per petal from 0 to 6
        if petal_update_idx == 6: petal_update_dir = -1
        if petal_update_idx == 0: petal_update_dir = 1


#bootLED.off()

############################################################
#
# Main code


rainbow_call = 0
petal_call = 0

while True:
    update_input()
    time.sleep_ms(1)
    rainbow_call += 1
    if (rainbow_call % sleep_time == 0): rainbow_cycle()

    petal_call += 1
    if (petal_call % sleep_time*2 == 0): petal_cycle()

    red = new_red
    green = new_green
    blue = new_blue
