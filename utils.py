from config.config import OBSERVATIONS, KNOWN_VARIABLES, ALL_VARIABLES, EQUATIONS


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
    return isinstance(data, list) and all(isinstance(elem, list) for elem in data)


def prepare_equations_for_gpt(variables):
    unknowns = sorted(list(set(variables[ALL_VARIABLES]) - set(variables[KNOWN_VARIABLES])))
    processed_equations = []
    for equation in variables[EQUATIONS]:
        symbol, eq_part = equation.split(': ')
        used_unknowns = [var for var in unknowns if var in eq_part]
        processed_equation = (symbol, eq_part, used_unknowns)
        processed_equations.append(processed_equation)
    return processed_equations


def prepare_observations_for_gpt(variables):
    is_logical = any(char in equation for equation in variables[EQUATIONS] for char in ['~', '&', '|', '^'])
    return {variable: (True if value == 1 else False) if is_logical else value for variable, value in
            zip(variables[KNOWN_VARIABLES], variables[OBSERVATIONS])}
