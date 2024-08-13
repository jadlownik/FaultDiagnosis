from sympy import symbols, And, Or, Not, Xor, solve, Eq
from itertools import product


class MinimalConflictFinder:
    def __init__(self, mso, equations, data):
        self.mso = mso
        self.equations = equations
        self.data = data
        self.parsed_equations = self._define_equations(equations, data)

    def _define_equations(self, equations, data):
        parsed = {}
        for name, equation in equations.items():
            # Split the equation to left and right sides
            left_side, right_side = equation.split('=')
            left_side = left_side.strip()
            right_side = right_side.strip()

            # Create symbols for all variables in the equation
            symbols_dict = {var: symbols(var) for var in left_side.split() if var.isidentifier()}
            symbols_dict.update({var: symbols(var) for var in right_side.split() if var.isidentifier()})

            # Replace observed data in the symbols
            for var, value in data.items():
                if var in symbols_dict:
                    symbols_dict[var] = value

            # Build the equation
            if '~&' in left_side:
                parsed_expression = Not(And(*(symbols_dict[var] for var in left_side.split() if var in symbols_dict)))
                parsed_expression = Eq(parsed_expression, symbols_dict[right_side])  # Convert to equality
            elif '~|' in left_side:
                parsed_expression = Not(Or(*(symbols_dict[var] for var in left_side.split() if var in symbols_dict)))
                parsed_expression = Eq(parsed_expression, symbols_dict[right_side])  # Convert to equality
            elif '~^' in left_side:
                parsed_expression = Not(Xor(*(symbols_dict[var] for var in left_side.split() if var in symbols_dict)))
                parsed_expression = Eq(parsed_expression, symbols_dict[right_side])  # Convert to equality
            elif '^' in left_side:
                parsed_expression = Or(*(symbols_dict[var] for var in left_side.split() if var in symbols_dict))
                parsed_expression = Eq(parsed_expression, symbols_dict[right_side])  # Convert to equality
            elif '~' in left_side:
                parsed_expression = Not(*(symbols_dict[var] for var in left_side.split() if var in symbols_dict))
                parsed_expression = Eq(parsed_expression, symbols_dict[right_side])  # Convert to equality
            elif '&' in left_side:
                parsed_expression = And(*(symbols_dict[var] for var in left_side.split() if var in symbols_dict))
                parsed_expression = Eq(parsed_expression, symbols_dict[right_side])  # Convert to equality
            elif '|' in left_side:
                parsed_expression = Or(*(symbols_dict[var] for var in left_side.split() if var in symbols_dict))
                parsed_expression = Eq(parsed_expression, symbols_dict[right_side])  # Convert to equality
            else:
                # Handle different operations in arithmetic expressions
                if '+' in left_side:
                    left_terms = left_side.split('+')
                    left_expr = sum(symbols_dict[var.strip()] for var in left_terms if var.strip() in symbols_dict)
                elif '*' in left_side:
                    left_terms = left_side.split('*')
                    left_expr = 1
                    for var in left_terms:
                        v = symbols_dict.get(var.strip())
                        if v:
                            left_expr *= v
                else:
                    left_expr = symbols_dict[left_side]  # For a single term case

                right_expr = symbols_dict[right_side]
                parsed_expression = Eq(left_expr, right_expr)  # Create an equality for arithmetic

            parsed[name] = parsed_expression

        return parsed

    def _is_contradictory(self, equations):
        # Check if equations are logical or arithmetic
        is_logical = any(char in equation for equation in self.equations.values() for char in ['~', '&', '|', '^'])

        if is_logical:
            # Get all variables involved in the equations
            variables = {var for eq in equations.values() for var in eq.free_symbols}
            # Generate all True/False combinations for the variables
            for combination in product([True, False], repeat=len(variables)):
                assignment = dict(zip(variables, combination))
                if all(Eq(eq.subs(assignment), True) for eq in equations.values()):
                    return False
            return True

        else:
            # For arithmetic equations, we will solve them to check for contradictions
            eqs = list(equations.values())
            sol = solve(eqs, dict=True)
            return len(sol) == 0

    def _get_minimal_conflicts(self):
        minimal_conflicts = []

        for group in self.mso:
            # Gather equations for the current group
            group_equations = {name: self.parsed_equations[name] for name in group if name in self.parsed_equations}

            if self._is_contradictory(group_equations):
                minimal_conflicts.append(sorted(group))

        return sorted(minimal_conflicts, key=lambda x: (len(x), x))
