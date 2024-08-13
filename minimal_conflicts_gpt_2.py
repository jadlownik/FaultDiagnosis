from sympy import symbols, Eq, Not, And, Or, Xor, Add, Mul
from itertools import product


class EquationParser:
    def __init__(self, mso, equations, data):
        self.mso = mso
        self.equations = equations
        self.data = data
        self.parsed_equations = self._parse_equations()

    def _parse_equations(self):
        parsed = {}
        for name, equation in self.equations.items():
            left_side, right_side = map(str.strip, equation.split('='))
            symbols_dict = {var: symbols(var) for var in left_side.split() + right_side.split() if var.isidentifier()}

            # Replace observed data in the symbols_dict
            for key in self.data:
                if key in symbols_dict:
                    symbols_dict[key] = self.data[key]

            # Build the equation based on the operator present in left_side
            if '*' in left_side:
                left_expression = Mul(*[symbols_dict[var.strip()] for var in left_side.split('*')])
            elif '+' in left_side:
                left_expression = Add(*[symbols_dict[var.strip()] for var in left_side.split('+')])
            elif '~&' in left_side:
                left_expression = Not(And(*[symbols_dict[var.strip()] for var in left_side.split('~&')]))
            elif '~|' in left_side:
                left_expression = Not(Or(*[symbols_dict[var.strip()] for var in left_side.split('~|')]))
            elif '~^' in left_side:
                left_expression = Not(Xor(*[symbols_dict[var.strip()] for var in left_side.split('~^')]))
            elif '&' in left_side:
                left_expression = And(*[symbols_dict[var.strip()] for var in left_side.split('&')])
            elif '|' in left_side:
                left_expression = Or(*[symbols_dict[var.strip()] for var in left_side.split('|')])
            elif '^' in left_side:
                left_expression = Xor(*[symbols_dict[var.strip()] for var in left_side.split('^')])
            else:
                left_expression = symbols_dict[left_side.strip()]

            right_expr = symbols_dict[right_side.strip()]
            parsed[name] = Eq(left_expression, right_expr)

        return parsed

    def _is_contradictory(self, equations):
        is_logical = any(char in eq for eq in self.equations.values() for char in ['~', '&', '|', '^'])
        if is_logical:
            variables = {var for eq in equations for var in eq.free_symbols}
            for combination in product([True, False], repeat=len(variables)):
                assignment = dict(zip(variables, combination))
                if all(eq.subs(assignment) for eq in equations):
                    return False
            return True
        else:
            from sympy import solve
            solutions = solve([eq.lhs - eq.rhs for eq in equations], dict=True)
            return len(solutions) == 0

    def get_minimal_conflicts(self):
        minimal_conflicts = []
        for group in self.mso:
            group_equations = [self.parsed_equations[name] for name in group if name in self.parsed_equations]
            if self._is_contradictory(group_equations):
                minimal_conflicts.append(sorted(group))

        return sorted(minimal_conflicts, key=lambda x: (len(x), x))
