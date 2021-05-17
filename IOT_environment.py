import random
from datetime import datetime

class Measurement:
    def __init__(self, time, temperature, humidity):
        self.time = time
        self.temperature = temperature
        self.humidity = humidity

    def get_time_of_measurement(self):
        return self.time

    def get_temperature(self):
        return self.temperature

    def get_humidity(self):
        return self.humidity

    def to_string(self):
        return str(
            "\nTIME_OF_MEASUREMENT: " + str(self.get_time_of_measurement()) + 
            "\nTEMPERATURE: " + str(self.get_temperature()) + 
            "\nHUMIDITY: " + str(self.get_humidity())
            )
            
    def __str__(self):
        return "measure(time: " + str(self.get_time_of_measurement()) + ", temp: " + str(self.get_temperature()) + ", hum: " + str(self.get_humidity()) + ")"


class Environment:
    def get_current_measurement(self):
        random_temperature = random.randrange(-15,45)
        random_humidity = random.randrange(0,100)
        return Measurement(str(datetime.now()), random_temperature, random_humidity)