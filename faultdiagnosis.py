import sys
import os
from models.smalldiagnosismodel import SmallDiagnosisModel
from services.readerservice import ReaderService
from services.printservice import PrintService
from services.folservice import FOLService
from models.diagnosismodel import DiagnosisModel
from models.gptmodel import GPTModel
from utils import format_data, get_observations, are_lists_on_list, \
    prepare_equations_for_gpt, prepare_observations_for_gpt
from config.config import PATH_EXAMPLES, TITLE, EQUATIONS, OBSERVATIONS, ACTUAL_PART
from enums import PartEnum


class FaultDiagnosis:
    _collected_data = []
    _enable_print = None
    _disable_print = None

    def __init__(self):
        self._reader_service = ReaderService()
        self._print_service = PrintService()
        self._fol_service = FOLService()
        self._gpt_model = GPTModel()
        self._init_print_settings()

    def start(self):
        examples = self._reader_service.get_all_examples()
        iterator = 1
        for example in examples:
            variables = self._reader_service.read(f'{PATH_EXAMPLES}{example}')

            if self._reader_service.variables_ok():
                observations = variables[OBSERVATIONS]
                variables.pop(OBSERVATIONS)

                if are_lists_on_list(observations):
                    for observation in observations:
                        variables[OBSERVATIONS] = observation
                        self._generate_single_row(variables, iterator)
                        iterator += 1
                        if ACTUAL_PART == PartEnum.MSO.value:
                            break
                else:
                    variables[OBSERVATIONS] = observations
                    self._generate_single_row(variables, iterator)
                    iterator += 1
        self._print_service.save_to_csv(self._collected_data, 'results\\results.csv')
        self._print_service.save_table_to_file(self._collected_data, 'results\\results.txt')

    def _print_results_to_console(self,
                                  formatted_equations,
                                  formatted_observations,
                                  formatted_fdt_all_minimal_conflicts,
                                  formatted_fdt_all_minimal_diagnosis,
                                  formatted_fdt_minimal_conflicts,
                                  formatted_fdt_minimal_diagnosis,
                                  formatted_all_minimal_conflicts,
                                  formatted_all_minimal_diagnosis,
                                  formatted_minimal_conflicts,
                                  formatted_minimal_diagnosis,
                                  formatted_gpt_minimal_conflicts,
                                  formatted_gpt_minimal_diagnosis):
        sys.stdout = self._enable_print
        print(f'Equations:\n{formatted_equations}')
        print(f'Observations:\n{formatted_observations}')
        print(f'All minimal conflicts FDT:\n{formatted_fdt_all_minimal_conflicts}')
        print(f'All minimal diagnosis FDT:\n{formatted_fdt_all_minimal_diagnosis}')
        print(f'Minimal conflicts FDT:\n{formatted_fdt_minimal_conflicts}')
        print(f'Minimal diagnosis FDT:\n{formatted_fdt_minimal_diagnosis}')
        print(f'All minimal conflicts:\n{formatted_all_minimal_conflicts}')
        print(f'All minimal diagnosis:\n{formatted_all_minimal_diagnosis}')
        print(f'Minimal conflicts:\n{formatted_minimal_conflicts}')
        print(f'Minimal diagnosis:\n{formatted_minimal_diagnosis}')
        print(f'GPT MSO:\n{formatted_gpt_minimal_conflicts}')
        print(f'GPT minimal conflicts:\n{formatted_gpt_minimal_conflicts}')
        print(f'GPT minimal diagnosis:\n{formatted_gpt_minimal_diagnosis}')
        print('------------------------')
        sys.stdout = self._disable_print

    def _generate_single_row(self, variables, iterator):
        if not any(char in equation for equation in variables[EQUATIONS] for char in ['~', '&', '|', '^']):
            model = DiagnosisModel()
            model.create(variables)
            all_minimal_conflicts = model.get_all_minimal_conflicts()
            all_minimal_diagnosis = model.get_all_minimal_diagnosis()
            minimal_conflicts = model.get_minimal_conflicts()
            minimal_diagnosis = model.get_minimal_diagnosis()
        else:
            small_model = SmallDiagnosisModel()
            small_model.create(variables)
            all_minimal_conflicts, all_minimal_diagnosis, minimal_conflicts, minimal_diagnosis = small_model.get_result()

        gpt_equations = prepare_equations_for_gpt(variables)
        gpt_observations = prepare_observations_for_gpt(variables)
        if ACTUAL_PART == PartEnum.MSO.value or ACTUAL_PART == PartEnum.ALL.value:
            gpt_input_data = f'equations = {gpt_equations}, data = {gpt_observations}'
        elif ACTUAL_PART == PartEnum.MINIMAL_CONFLICTS.value:
            gpt_input_data = f'mso = {all_minimal_conflicts}, equations = {gpt_equations}, data = {gpt_observations}'
        elif ACTUAL_PART == PartEnum.MINIMAL_DIAGNOSES.value:
            gpt_input_data = f'minimal_conflicts = {minimal_conflicts}'
        gpt_mso, gpt_minimal_conflicts, gpt_minimal_diagnosis = self._gpt_model.get_solution(gpt_input_data)

        formatted_equations = format_data(variables[EQUATIONS])
        formatted_observations = format_data(get_observations(variables))
        formatted_all_minimal_conflicts = format_data(all_minimal_conflicts)
        formatted_all_minimal_diagnosis = format_data(all_minimal_diagnosis)
        formatted_minimal_conflicts = format_data(minimal_conflicts)
        formatted_minimal_diagnosis = format_data(minimal_diagnosis)
        formatted_gpt_mso = format_data(gpt_mso)
        formatted_gpt_minimal_conflicts = format_data(gpt_minimal_conflicts)
        formatted_gpt_minimal_diagnosis = format_data(gpt_minimal_diagnosis)

        row = [
            iterator, variables[TITLE],
            formatted_equations, formatted_observations,
            formatted_all_minimal_conflicts, formatted_all_minimal_diagnosis,
            formatted_minimal_conflicts, formatted_minimal_diagnosis,
            formatted_gpt_mso, formatted_gpt_minimal_conflicts, formatted_gpt_minimal_diagnosis
        ]

        self._collected_data.append(row)

    def _init_print_settings(self):
        self._enable_print = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        self._disable_print = sys.stdout
