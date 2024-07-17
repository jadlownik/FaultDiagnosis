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
