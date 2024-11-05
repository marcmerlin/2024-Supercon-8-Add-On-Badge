from machine import I2C, Pin
import time

counter = 0
overlay = [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ]


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
    print("F - Duck found, sending color init.")
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
            ## see what's going on with the touch wheel
            if touchwheel_bus:
                tw = touchwheel_read(touchwheel_bus)

                if tw > 0:
                    tw = (128 - tw) % 256 
                    petal = int(tw/32) + 1
                else: 
                    petal = 2
                sleep_time = petal * 30

            which_leds = (1 << j)
            for i in range(1,9):
                which_leds2 = which_leds
                which_leds2 += overlay[i]
                #print (str(i) + ": " + str(which_leds2))
                petal_bus.writeto_mem(PETAL_ADDRESS, i, bytes([which_leds2]))
            time.sleep_ms(sleep_time)

    red = new_red
    green = new_green
    blue = new_blue
