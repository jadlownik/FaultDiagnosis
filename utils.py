from config.config import OBSERVATIONS, KNOWN_VARIABLES


def format_data(data):
    formatted_data = []
    for sublist in data:
        if isinstance(sublist, str):
            formatted_data.append(sublist)
        else:
            formatted_data.append(', '.join(sublist))
    return '\n'.join(formatted_data)


def get_observations(data):
    return [f'{variable} = {value}' for variable, value in
            zip(data[KNOWN_VARIABLES], data[OBSERVATIONS])]


def are_lists_on_list(data):
    return isinstance(data, list) \
           and all(isinstance(elem, list) for elem in data)
           

def equations_format_for_gpt_mso(unknown, equations):
    processed_equations = []

    for index, equation in enumerate(equations):
        _, eq_part = equation.split(': ')
        used_unknowns = [var for var in unknown if var in eq_part]
        processed_equation = (index, eq_part, used_unknowns)
        processed_equations.append(processed_equation)

    return processed_equations
