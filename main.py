from reader import ExampleReader
from diagnosismodel import DiagnosisModel
from config import PATH_EXAMPLES
import logging

_reader = ExampleReader()
_variables = _reader.read(f'{PATH_EXAMPLES}\example_1.txt')

if _reader.varaibles_ok():
    _model = DiagnosisModel()
    _model.create(_variables)
    v = _model.get_minimal_conflicts_for_observations()
    print(v)
else:
    logging.warning(f'Read variables are wrong. \n Variables: \{_variables}')
