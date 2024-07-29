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


def prepare_observations(variables, observations, is_logical):
    return {variable: (True if value == 1 else False) if is_logical else value for variable, value in
            zip(variables, observations)}


def prepare_equations(equations):
    new_equations = {}
    for equation in equations:
        eq_name, eq_content = equation.split(': ', 1)
        new_equations[eq_name.strip()] = eq_content.strip()
    return new_equations


def are_lists_on_list(data):
    return isinstance(data, list) and all(isinstance(elem, list) for elem in data)


def format_equations_for_gpt(unknown, equations):
    processed_equations = []
    for equation in equations:
        symbol, eq_part = equation.split(': ')
        used_unknowns = [var for var in unknown if var in eq_part]
        processed_equation = (symbol, eq_part, used_unknowns)
        processed_equations.append(processed_equation)
    return processed_equations
