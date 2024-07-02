from reader import ExampleReader
from diagnosismodel import DiagnosisModel
from printservice import PrintService
from utils import format_data, get_observations, are_lists_on_list
from config import PATH_EXAMPLES, TITLE, EQUATIONS, OBSERVATIONS

iterator = 1
collected_data = []

reader = ExampleReader()
print_service = PrintService()


def generate_single_row(variables):
    model = DiagnosisModel()
    model.create(variables)

    lp = iterator
    title = variables[TITLE]
    rels = variables[EQUATIONS]
    obs = get_observations(variables)
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
    separator_row = ["---------------"] * len(row)
    collected_data.append(separator_row)


if __name__ == '__main__':
    examples = reader.get_all_examples()

    for example in examples:
        variables = reader.read(f'{PATH_EXAMPLES}{example}')

        if reader.variables_ok():
            observations = variables[OBSERVATIONS]
            variables.pop(OBSERVATIONS)

            if are_lists_on_list(observations):
                for observation in observations:
                    variables[OBSERVATIONS] = observation
                    generate_single_row(variables)
                    iterator += 1
            else:
                variables[OBSERVATIONS] = observations
                generate_single_row(variables)
                iterator += 1

    # print_service.print_table(collected_data)
    print_service.save_table_to_file(collected_data, "results.txt")
