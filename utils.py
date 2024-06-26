from config import OBSERVATIONS, KNOWN_VARIABLES


def format_data(data):
    formatted_data = []
    for sublist in data:
        if isinstance(sublist, str):
            formatted_data.append(sublist)
        else:
            formatted_data.append(", ".join(sublist))
    return "\n".join(formatted_data)


def get_observations(data):
    return [f"{char} = {value}" for char, value in zip(data[KNOWN_VARIABLES], data[OBSERVATIONS])]
