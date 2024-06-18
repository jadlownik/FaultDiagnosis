from config import KNOWN_VARIABLES, FAULTS, UNKNOWN_VARIABLES, EQUATIONS, OBSERVATIONS


class ExampleReader():
    _variables = None

    def read(self, path):
        self._variables = {}
        with open(path, 'r') as file:
            content = file.read()
            exec(content, {}, self._variables)
        return self._variables

    def varaibles_ok(self):
        return KNOWN_VARIABLES in self._variables and \
               FAULTS in self._variables and \
               UNKNOWN_VARIABLES in self._variables and \
               EQUATIONS in self._variables and \
               OBSERVATIONS in self._variables
