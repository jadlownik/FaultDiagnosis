from reader import ExampleReader
from diagnosismodel import DiagnosisModel
from printservice import PrintService
from config import PATH_EXAMPLES, TITLE

reader = ExampleReader()
print_service = PrintService()
variables = reader.read(f'{PATH_EXAMPLES}example_1.txt')

if reader.varaibles_ok():
    model = DiagnosisModel()
    model.create(variables)
    title = variables[TITLE]
    all_minimal_conflicts = model.get_all_minimal_conflicts()
    all_minimal_diagnosis = model.get_all_minimal_diagnosis()
    minimal_conflicts = model.get_minimal_conflicts()
    minimal_diagnosis = model.get_minimal_diagnosis()
    gpt_minimal_conflicts = []
    gpt_minimal_diagnosis = []

    print_service.print_table(title,
                              all_minimal_conflicts, all_minimal_diagnosis,
                              minimal_conflicts, minimal_diagnosis,
                              gpt_minimal_conflicts, gpt_minimal_diagnosis)
