import time

class Agent:

    def __init__(self, sensors, actuators, behaviour):
        self.sensors = sensors
        self.actuators = actuators
        self.behaviour = behaviour

    def inject_actuators(self, behaviour):
        behaviour.actuators = self.actuators

    def wake_up(self):

        self.inject_actuators(self.behaviour)

        time.sleep(2)

        while True:
            senses = {}
            for name, sensor in self.sensors.items():
                senses[name] = sensor.pull()

            actions = self.behaviour.action(**senses)
            if actions:
                for key, value in actions.items():
                    # self.actuators[key].push(value)
                    pass
