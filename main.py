from reader import ExampleReader
from diagnosismodel import DiagnosisModel
from printservice import PrintService
from config import PATH_EXAMPLES, TITLE

reader = ExampleReader()
print_service = PrintService()
variables = reader.read(f'{PATH_EXAMPLES}\example_1.txt')

if reader.varaibles_ok():
    model = DiagnosisModel()
    model.create(variables)
    all_minimal_conflicts = model.get_all_minimal_conflicts()
    all_minimal_diagnosis = model.get_all_minimal_diagnosis()
    residuals = model._get_residuals()
    print(f'Solution for {variables[TITLE]}:')
    print_service.print_list(all_minimal_conflicts, 'All minimal conflicts:')
    print_service.print_list(all_minimal_diagnosis, 'All minimal diagnosis:')
    print_service.print_list(residuals, 'Residuals:')
