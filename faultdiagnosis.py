import sys
import os
from models.smalldiagnosismodel import SmallDiagnosisModel
from services.readerservice import ReaderService
from services.printservice import PrintService
from services.folservice import FOLService
from models.diagnosismodel import DiagnosisModel
from models.gptmodel import GPTModel
from utils import format_data, get_observations, are_lists_on_list
from config.config import PATH_EXAMPLES, TITLE, EQUATIONS, OBSERVATIONS, PRINT_TO_CONSOLE


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
                else:
                    variables[OBSERVATIONS] = observations
                    self._generate_single_row(variables, iterator)
                    iterator += 1

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
        print(f'GPT minimal conflicts:\n{formatted_gpt_minimal_conflicts}')
        print(f'GPT minimal diagnosis:\n{formatted_gpt_minimal_diagnosis}')
        print('------------------------')
        sys.stdout = self._disable_print

    def _generate_single_row(self, variables, iterator):
        model = DiagnosisModel()
        model.create(variables)
        fdt_all_minimal_conflicts = model.get_all_minimal_conflicts()
        fdt_all_minimal_diagnosis = model.get_all_minimal_diagnosis()
        fdt_minimal_conflicts = model.get_minimal_conflicts()
        fdt_minimal_diagnosis = model.get_minimal_diagnosis()

        small_model = SmallDiagnosisModel()
        small_model.create(variables)
        all_minimal_conflicts, all_minimal_diagnosis, minimal_conflicts, minimal_diagnosis = small_model.get_result()
        # mso_unknown = sorted(list(set(variables[UNKNOWN_VARIABLES]) - set(variables[KNOWN_VARIABLES])))
        # equations_gpt = format_equations_for_gpt(mso_unknown, rels)
        # obs_gpt = prepare_observations(variables)
        # gpt_input_data = f'equations = {equations_gpt}, data = {obs_gpt}'
        # gpt_minimal_conflicts, gpt_minimal_diagnosis = self._gpt_model.get_solution(gpt_input_data)

        gpt_minimal_conflicts, gpt_minimal_diagnosis = [], []

        formatted_equations = format_data(variables[EQUATIONS])
        formatted_observations = format_data(get_observations(variables))
        formatted_fdt_all_minimal_conflicts = format_data(fdt_all_minimal_conflicts)
        formatted_fdt_all_minimal_diagnosis = format_data(fdt_all_minimal_diagnosis)
        formatted_fdt_minimal_conflicts = format_data(fdt_minimal_conflicts)
        formatted_fdt_minimal_diagnosis = format_data(fdt_minimal_diagnosis)
        formatted_all_minimal_conflicts = format_data(all_minimal_conflicts)
        formatted_all_minimal_diagnosis = format_data(all_minimal_diagnosis)
        formatted_minimal_conflicts = format_data(minimal_conflicts)
        formatted_minimal_diagnosis = format_data(minimal_diagnosis)
        formatted_gpt_minimal_conflicts = format_data(gpt_minimal_conflicts)
        formatted_gpt_minimal_diagnosis = format_data(gpt_minimal_diagnosis)

        if PRINT_TO_CONSOLE:
            self._print_results_to_console(formatted_equations, formatted_observations,
                                           formatted_fdt_all_minimal_conflicts,
                                           formatted_fdt_all_minimal_diagnosis,
                                           formatted_fdt_minimal_conflicts,
                                           formatted_fdt_minimal_diagnosis,
                                           formatted_all_minimal_conflicts,
                                           formatted_all_minimal_diagnosis,
                                           formatted_minimal_conflicts,
                                           formatted_minimal_diagnosis,
                                           formatted_gpt_minimal_conflicts,
                                           formatted_gpt_minimal_diagnosis)

        row = [
            iterator, variables[TITLE],
            formatted_equations, formatted_observations,
            formatted_fdt_all_minimal_conflicts, formatted_fdt_all_minimal_diagnosis,
            formatted_fdt_minimal_conflicts, formatted_fdt_minimal_diagnosis,
            formatted_all_minimal_conflicts, formatted_all_minimal_diagnosis,
            formatted_minimal_conflicts, formatted_minimal_diagnosis,
            formatted_gpt_minimal_conflicts, formatted_gpt_minimal_diagnosis
        ]

        self._collected_data.append(row)
        separator_row = ['---------------'] * len(row)
        self._collected_data.append(separator_row)

    def _init_print_settings(self):
        self._enable_print = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        self._disable_print = sys.stdout
