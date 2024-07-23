from sympy import symbols

# Define the symbolic variables used in the equations
x01, x02, x03, f, g = symbols('x01 x02 x03 f g')

def preprocess_equation(equation):
    # Remove labels such as 'M1:', 'M2:', etc.
    return equation.split(": ")[1]

def substitute_data(equation, data_values):
    for data in data_values:
        var, value = data.split(' = ')
        equation = equation.replace(var.strip(), value.strip())
    return equation

def evaluate_equation(equation):
    lhs, rhs = equation.split('=')
    lhs_expr = eval(lhs.strip())
    rhs_expr = eval(rhs.strip())
    return lhs_expr, rhs_expr

def check_system_consistency(equations, data):
    evaluated_results = []
    for eq in equations:
        preprocessed_eq = preprocess_equation(eq)
        substituted_eq = substitute_data(preprocessed_eq, data)
        lhs, rhs = evaluate_equation(substituted_eq)
        evaluated_results.append(lhs == rhs)
    return all(evaluated_results)

def find_minimal_conflicts(equations, mso, data):
    minimal_conflicts = []
    for indices in mso:
        eq_subset = [equations[i] for i in indices]
        if not check_system_consistency(eq_subset, data):
            conflict_labels = [equations[i].split(":")[0].strip() for i in indices]
            minimal_conflicts.append(conflict_labels)
    return minimal_conflicts

equations_part2 = [
    'M1: a * c = x01',
    'M2: b * d = x02',
    'M3: c * e = x03',
    'A1: x01 + x02 = f',
    'A2: x02 + x03 = g '
]

data = ['a = 2', 'b = 2', 'c = 3', 'd = 3', 'e = 2', 'f = 12', 'g = 12']

mso = [[0, 1, 3], [1, 2, 4], [0, 2, 3, 4]]

minimal_conflicts = find_minimal_conflicts(equations_part2, mso, data)
minimal_conflicts