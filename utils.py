from config.config import OBSERVATIONS, KNOWN_VARIABLES, ALL_VARIABLES, EQUATIONS
import re


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
    is_logical = any(char in equation for equation in variables[EQUATIONS] for char in ['~', '&', '|', '^'])
    if is_logical:
        return prepare_logical_equations_for_gpt(variables)
    return prepare_arithmetic_equations_for_gpt(variables)


def prepare_logical_equations(variables):
    unknowns = sorted(list(set(variables[ALL_VARIABLES]) - set(variables[KNOWN_VARIABLES])))
    processed_equations = []
    for equation in variables[EQUATIONS]:
        symbol, eq_part = equation.split(': ')
        used_unknowns = [var for var in unknowns if var in eq_part]
        pattern = re.compile(r'(\S+):\s*(.+?)\s*=\s*(\S+)')
        match = pattern.match(equation.replace(' ', ''))
        if match:
            left_side = match.group(2).strip()
            variables = left_side.split('~^') if '~^' in left_side else \
                left_side.split('~&') if '~&' in left_side else \
                left_side.split('~|') if '~|' in left_side else \
                left_side.split('&') if '&' in left_side else \
                left_side.split('|') if '|' in left_side else \
                left_side.split('^') if '^' in left_side else \
                left_side.split('~')
            result = match.group(3)
            if '~^' in left_side:
                left_side = f'XNOR({', '.join(variables)})'
            elif '~&' in left_side:
                left_side = f'NAND({', '.join(variables)})'
            elif '~|' in left_side:
                left_side = f'NOR({', '.join(variables)})'
            elif '&' in left_side:
                left_side = f'AND({', '.join(variables)})'
            elif '|' in left_side:
                left_side = f'OR({', '.join(variables)})'
            elif '^' in left_side:
                left_side = f'XOR({', '.join(variables)})'
            elif '~' in left_side:
                left_side = f'NOT({', '.join(variables)})'
        eq = f'{left_side} - {result}'
        processed_equation = (symbol, eq, used_unknowns)
        processed_equations.append(processed_equation)
    return processed_equations


def prepare_logical_equations_for_gpt(variables):
    equations = prepare_logical_equations(variables)
    temp_dict = {}
    for label, expression, _ in equations:
        operation, output_var = expression.split(' - ')
        if output_var not in variables[KNOWN_VARIABLES]:
            temp_dict[output_var] = label

    transformed_equations = []

    for label, expression, inputs in equations:
        operation, output_var = expression.split(' - ')
        new_inputs = []

        match = re.match(r'^[^\(]+\(([^)]+)\)$', operation)
        if match:
            content = match.group(1)
            values = [val.strip() for val in content.split(',')]
            for val in values:
                if val in variables[KNOWN_VARIABLES]:
                    new_inputs.append(val)
                if val in temp_dict.keys():
                    new_inputs.append(temp_dict[val])

        new_expression = operation
        for temp_var, label_name in temp_dict.items():
            new_expression = new_expression.replace(temp_var, label_name)

        if output_var not in inputs:
            new_expression += f" == {output_var}"
            new_inputs.append(output_var)

        transformed_equations.append((label, new_expression, new_inputs))

    return transformed_equations


def prepare_arithmetic_equations_for_gpt(variables):
    unknowns = sorted(list(set(variables[ALL_VARIABLES]) - set(variables[KNOWN_VARIABLES])))
    processed_equations = []
    for equation in variables[EQUATIONS]:
        symbol, eq_part = equation.split(': ')
        used_unknowns = [var for var in unknowns if var in eq_part]
        eq = eq_part.replace('=', '-')
        processed_equation = (symbol, eq, used_unknowns)
        processed_equations.append(processed_equation)
    return processed_equations


def prepare_observations_for_gpt(variables):
    is_logical = any(char in equation for equation in variables[EQUATIONS] for char in ['~', '&', '|', '^'])
    return {variable: (True if value == 1 else False) if is_logical else value for variable, value in
            zip(variables[KNOWN_VARIABLES], variables[OBSERVATIONS])}
