from reader import ExampleReader
from diagnosismodel import DiagnosisModel
from printservice import PrintService
from utils import format_data, get_observations
from config import PATH_EXAMPLES, TITLE, EQUATIONS, OBSERVATIONS

iterator = 1
collected_data = []

reader = ExampleReader()
print_service = PrintService()

examples = reader.get_all_examples()

for example in examples:
    variables = reader.read(f'{PATH_EXAMPLES}{example}')
    if reader.variables_ok():
        observations = variables[OBSERVATIONS]
        variables.pop(OBSERVATIONS)
        for observation in range(len(observations)):
            current_variables = variables.copy()
            current_variables[OBSERVATIONS] = observations[observation]

            model = DiagnosisModel()
            model.create(current_variables)

            lp = iterator
            title = current_variables[TITLE]
            rels = current_variables[EQUATIONS]
            obs = get_observations(current_variables)
            all_minimal_conflicts = model.get_all_minimal_conflicts()
            all_minimal_diagnosis = model.get_all_minimal_diagnosis()
            minimal_conflicts = model.get_minimal_conflicts()
            minimal_diagnosis = model.get_minimal_diagnosis()
            gpt_minimal_conflicts = []
            gpt_minimal_diagnosis = []

            formatted_equations = format_data(rels)
            formatted_observations = format_data(obs)
            formatted_all_minimal_conflicts = format_data(all_minimal_conflicts)
            formatted_all_minimal_diagnosis = format_data(all_minimal_diagnosis)
            formatted_minimal_conflicts = format_data(minimal_conflicts)
            formatted_minimal_diagnosis = format_data(minimal_diagnosis)
            formatted_gpt_minimal_conflicts = format_data(gpt_minimal_conflicts)
            formatted_gpt_minimal_diagnosis = format_data(gpt_minimal_diagnosis)

            row = [
                lp, title,
                formatted_equations, formatted_observations,
                formatted_all_minimal_conflicts, formatted_all_minimal_diagnosis,
                formatted_minimal_conflicts, formatted_minimal_diagnosis,
                formatted_gpt_minimal_conflicts, formatted_gpt_minimal_diagnosis
            ]

            collected_data.append(row)
            iterator += 1

            separator_row = ["---------------"] * len(row)
            collected_data.append(separator_row)

print_service.print_table(collected_data)
