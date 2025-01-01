import time
from tlc5916_driver import LEDController

data_out_pin = 11
clock_pin = 12
latch_pin = 13
oe_pin = 15
num_leds = 40
pwm_freq = 200
pwm_load = 100

tlc5916_driver = LEDController(
    data_out_pin,
    clock_pin,
    latch_pin,
    oe_pin,
    num_leds,
    pwm_freq,
    pwm_load,
)

try:
    while True:
        for lednum in range(num_leds):
            # loops through all 40 leds and turns them on individually for a second
            tlc5916_driver.change_state_led(lednum)
            time.sleep(0.1)
            tlc5916_driver.change_state_led(lednum)
except KeyboardInterrupt:
    tlc5916_driver.clear_leds()
