from alibx.behaviours.behaviour import Behaviour

import time


class StateMachineBehaviour(Behaviour):

    def __init__(self, *state_machine):

        self.STATE_MACHINE_RULES = {}
        self.RETURN_VALUE = None
        self.DONE = False
        self.LOG = False

        self.__init_machine___(state_machine)

        self.STATE = state_machine[0][0]
        self.LAST_STEP = time.time()

    def set_log(self, log=True):
        self.LOG = log

    def __init_machine___(self, states):
        for i in range(0, len(states)):
            state_params = states[i]
            state_name = state_params[0]
            next_state_name = states[(i + 1) % len(states)][0]

            if len(state_params) < 2:
                state_jumps = next_state_name
            elif isinstance(state_params[1], dict) and len(state_params[1]) == 0:
                state_jumps = {None: next_state_name}
            else:
                state_jumps = state_params[1]

            self.STATE_MACHINE_RULES[state_name] = state_jumps

    def set_state(self, state):
        self.STATE = str(state).toLowerCase()

    def done(self, return_value=None):
        self.DONE = True
        self.RETURN_VALUE = return_value

    def on_action(self, **senses):
        return True

    def action(self, **senses):
        self.DONE = False

        if not self.on_action(**senses):
            return

        if self.LOG:
            print('Calling state: ' + str(self.STATE))

        if isinstance(self.STATE, str):
            if self.STATE not in self.STATE_MACHINE_RULES:
                raise BaseException("State Machine Reached Unknown State: " + str(self.STATE))
            ret = getattr(self, self.STATE)(**senses)
        else:
            self.inject_actuators(self.STATE)
            ret = self.STATE.action(**senses)

        # Jump next state
        rules = self.STATE_MACHINE_RULES[self.STATE]
        if not isinstance(rules, dict):
            self.STATE = rules
        elif self.DONE:
            self.STATE = rules[self.RETURN_VALUE]

        self.LAST_STEP = time.time()
        return ret
