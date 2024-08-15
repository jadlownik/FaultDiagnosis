from config.config import OBSERVATIONS, KNOWN_VARIABLES, EQUATIONS


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
    return {eq.split(': ', 1)[0].strip(): eq.split(': ', 1)[1].strip() for eq in variables[EQUATIONS]}


def prepare_observations_for_gpt(variables):
    is_logical = any(char in equation for equation in variables[EQUATIONS] for char in ['~', '&', '|', '^'])
    return {variable: (True if value == 1 else False) if is_logical else value for variable, value in
            zip(variables[KNOWN_VARIABLES], variables[OBSERVATIONS])}
