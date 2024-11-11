from machine import I2C, Pin
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
n = np.n
rainbow_index = 0

# neopixel Boot init
for i in range(4 * n):
    for j in range(n):
        np[j] = (0, 0, 0)
    np[i % n] = (255, 255, 255)
    np.write()
    time.sleep_ms(25)

    # clear
    for i in range(n):
        np[i] = (0, 0, 0)
    np.write()


def wheel(pos):
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
    return (r, g, b)
 

def rainbow_cycle():
    global rainbow_index

    rainbow_index = rainbow_index + 11
    j = rainbow_index
    for i in range(NP_count):
        pixel_index = (i * 256 // NP_count) + j
        np[i] = wheel(pixel_index & 255)
    np.write()

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

#bootLED.off()


############################################################
#
# Main code

red = 0
green = 0
blue = 0

new_red = red
new_green = green
new_blue = blue

sleep_time = 40

while True:
    if not buttonA.value():
        if not red:
            new_red = 1
            print("red Pushed")
    else:
        if red:
            new_red = 0
            print("red released")

    if not buttonB.value():
        if not green:
            new_green = 1
            print("green Pushed")
    else:
        if green:
            new_green = 0
            print("green released")

    if not buttonC.value():
        if not blue:
            new_blue = 1
            print("blue Pushed")
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


    ## see what's going on with the touch wheel
    if touchwheel_bus:
        tw = touchwheel_read(touchwheel_bus)

        if tw > 0:
            tw = (128 - tw) % 256 
            petal = int(tw/32) + 1
            sleep_time = petal * 30

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

        for j in range(7):
            rainbow_cycle()

            which_leds = (1 << j)
            for i in range(1,9):
                which_leds2 = which_leds
                which_leds2 += overlay[i]
                #print (str(i) + ": " + str(which_leds2))
                petal_bus.writeto_mem(PETAL_ADDRESS, i, bytes([which_leds2]))
            time.sleep_ms(sleep_time)
        else:
            rainbow_cycle()

    red = new_red
    green = new_green
    blue = new_blue
