import serial
from tlc5916_driver import LEDController
import random
from datetime import datetime
import asyncio

ser = serial.Serial("/dev/ttyUSB0", 115200, timeout=None)
ser.reset_input_buffer()
data_out_pin = 11
clock_pin = 12
latch_pin = 13
oe_pin = 15
num_leds = 40
pwm_freq = 200
pwm_load = 100

macArray = [
    {"Last_seen": datetime.now().timestamp(), "MAC": "", "LED_num": ind}
    for ind in range(num_leds)
]

tlc5916_driver = LEDController(
    data_out_pin,
    clock_pin,
    latch_pin,
    oe_pin,
    num_leds,
    pwm_freq,
    pwm_load,
)

DEBUG = True


def log(s):
    if DEBUG:
        print(s)


async def blinkLed(lednum):
    tlc5916_driver.change_state_led(lednum)
    await asyncio.sleep(3)
    tlc5916_driver.change_state_led(lednum)
    return


async def handleNewMAC(macIn):
    if not any(x["MAC"] == "" for x in macArray):
        log(f"""No room for MAC: {macIn}""")
        # There is no more room
        return
    else:
        log(f"""Saving new MAC: {macIn}""")
        # Get free LEDs
        freeLeds = [x for x in macArray if x["MAC"] == ""]
        # Assign LED randomly
        randInd = random.randint(0, len(freeLeds) - 1)
        ledToAssign = freeLeds[randInd]["LED_num"]
        macArray[ledToAssign] = {
            "Last_seen": datetime.now().timestamp(),
            "MAC": macIn,
            "LED_num": ledToAssign,
        }
        await blinkLed(ledToAssign)
    return


async def handleSeenBefore(macIn):
    freeLeds = [x for x in macArray if x["MAC"] == ""]
    log(f"free leds: {len(freeLeds)}")

    MACobj = list(filter(lambda x: x["MAC"] == macIn, macArray))[0]
    log(f"Seen before MAC: {macIn}")
    await blinkLed(MACobj["LED_num"])
    return


async def handleRemoveStaleMAC():
    for ind, MACobj in enumerate(macArray):
        if (
            datetime.now().timestamp() - MACobj["Last_seen"] > 60
            and MACobj["MAC"] != ""
        ):
            log(f"""removing old MAC: {MACobj["MAC"]}""")
            macArray[ind] = {
                "Last_seen": datetime.now().timestamp(),
                "MAC": "",
                "LED_num": ind,
            }


async def main():
    while True:
        line = ser.read_until()
        line1 = line.decode("utf-8").strip("\r\n").split(",")

        # Uncomment this if statment to skip over management packets
        # if "MGMT" in line1[0]:
        #     continue

        log(line1)
        try:
            macIn = line1[-2].split("=")[1]
        except:
            continue
        """
        If haven't seen this MAC before:
            There is no more room:
                continue
            There is more room:
                assign LED number
                update last seen
                Blink LED

        If seen before, update last seen:
            Blink LED

        For every assigned LED:
            If last seen > 1 min:
                unassign LED
        """
        if not any(x["MAC"] == macIn for x in macArray):
            asyncio.create_task(handleNewMAC(macIn))
        else:
            asyncio.create_task(handleSeenBefore(macIn))

        asyncio.create_task(handleRemoveStaleMAC())
        await asyncio.sleep(0.05)


try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
finally:
    tlc5916_driver.clear_leds()
