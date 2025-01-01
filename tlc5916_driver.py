import RPi.GPIO as GPIO


class LEDController:
    def __init__(
        self,
        data_out_pin=11,
        clock_pin=12,
        latch_pin=13,
        oe_pin=15,
        num_leds=40,
        pwm_freq=200,
        pwm_load=100,
    ):
        self.DataOutPin = data_out_pin
        self.ClockPin = clock_pin
        self.LatchPin = latch_pin
        self.OEPin = oe_pin
        self.num_leds = num_leds
        self.pwm_freq = pwm_freq
        self.pwm_load = pwm_load
        self.led_array = [0] * self.num_leds
        self._setup_gpio()
        self.pwm = GPIO.PWM(oe_pin, pwm_freq)
        self.pwm.start(self.pwm_load)
        self.set_pwm(100)
        self.clear_leds()

    def _setup_gpio(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.OEPin, GPIO.OUT)
        GPIO.setup(self.LatchPin, GPIO.OUT)
        GPIO.setup(self.ClockPin, GPIO.OUT)
        GPIO.setup(self.DataOutPin, GPIO.OUT)
        GPIO.output(self.OEPin, True)
        GPIO.output(self.LatchPin, False)
        GPIO.output(self.ClockPin, False)

    def clear_leds(self):
        self.led_array = [0] * self.num_leds
        for _ in self.led_array:
            GPIO.output(self.ClockPin, False)
            GPIO.output(self.DataOutPin, False)
            GPIO.output(self.ClockPin, True)
        GPIO.output(self.LatchPin, True)
        GPIO.output(self.LatchPin, False)

    def set_pwm(self, new_pwm):
        self.pwm.ChangeDutyCycle(self.pwm_load - new_pwm)

    def change_state_led(self, led_num):
        if 0 <= led_num < self.num_leds:
            self.led_array[led_num] = ~self.led_array[led_num]
            for state in self.led_array:
                GPIO.output(self.ClockPin, False)
                GPIO.output(self.DataOutPin, bool(state))
                GPIO.output(self.ClockPin, True)
            GPIO.output(self.LatchPin, True)
            GPIO.output(self.LatchPin, False)
        else:
            raise ValueError("LED number out of range.")
