from config import KNOWN_VARIABLES, FAULTS, UNKNOWN_VARIABLES, \
                    EQUATIONS, OBSERVATIONS, PATH_EXAMPLES
import os


class ExampleReader():
    _variables = None

    def get_all_examples(folder_path):
        examples = [f for f in os.listdir(PATH_EXAMPLES) if f.endswith('.txt')]
        return examples

    def read(self, path):
        self._variables = {}
        with open(path, 'r') as file:
            content = file.read()
            exec(content, {}, self._variables)
        return self._variables

    def variables_ok(self):
        return KNOWN_VARIABLES in self._variables and \
               FAULTS in self._variables and \
               UNKNOWN_VARIABLES in self._variables and \
               EQUATIONS in self._variables and \
               OBSERVATIONS in self._variables
