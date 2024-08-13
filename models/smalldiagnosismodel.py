from typing import Set, List, Tuple
from sympy import symbols, Eq, solve, Not, Xor, Nand, Nor
from itertools import product, combinations


class SmallDiagnosisModel:
    def create(self, variables):
        self._equations = {eq.split(': ', 1)[0].strip(): eq.split(': ', 1)[1].strip() for eq in variables['r']}
        self._unknowns = set(variables['x']) - set(variables['z'])
        self._is_logical = any(char in equation for equation in self._equations.values() for char in ['~', '&', '|', '^'])
        self._observations = {variable: (True if value == 1 else False) if self._is_logical else value for variable, value
                              in zip(variables['x'], variables['o'])}
        self._equation_to_variables = {eq_name: set(v.strip() for v in eq_content.replace('=', ' ').split() if v.strip()
                                       not in ['*', '+', '~&', '~|', '~^', '~', '&', '|', '^', '='])
                                       for eq_name, eq_content in self._equations.items()}

    def get_result(self) -> Tuple[List[List[str]], List[List[str]]]:
        all_conflicts = self._find_mso()
        all_diagnoses = self._get_diagnosis(all_conflicts)
        minimal_conflicts = self._get_minimal_conflicts(all_conflicts)
        minimal_diagnoses = self._get_diagnosis(minimal_conflicts)
        return all_conflicts, all_diagnoses, minimal_conflicts, minimal_diagnoses

    def _structural_redundancy(self, equations: Set[str]) -> int:
        if len(equations) == 0: return 0
        variables = set.union(*(self._equation_to_variables[eq] for eq in equations))
        return len(equations) - (len(variables.intersection(self._unknowns)) if len(self._unknowns) > 0 else 0)

    def _is_pso(self, equations: Set[str]) -> bool:
        return self._structural_redundancy(equations) > 0

    def _find_mso(self) -> List[Set[str]]:
        mso = []
        eq_names = list(self._equations.keys())
        for i in range(1, len(eq_names) + 1):
            for combo in combinations(eq_names, i):
                eq_set = set(combo)
                if self._structural_redundancy(eq_set) == 1 and all(not self._is_pso(set(c)) for c in combinations(combo, len(combo) - 1)):
                    mso.append(sorted(eq_set))
        return sorted(mso, key=lambda x: (len(x), x))

    def _get_minimal_conflicts(self, mso: List[Set[str]]) -> List[List[str]]:
        minimal_conflicts = []
        for group in mso:
            eq_list = [self._define_equations()[eq].subs(self._observations) for eq in group]
            if self._is_logical:
                if self._is_contradictory(eq_list):
                    minimal_conflicts.append(sorted(group))
            else:
                solution = solve(eq_list, dict=True)
                if (len(eq_list) == 1 and not bool(eq_list[0])) \
                   or (len(eq_list) != 1 and (not solution or any(any(not eq.subs(sol) for eq in eq_list) for sol in solution))):
                    minimal_conflicts.append(sorted(group))
        return sorted(minimal_conflicts, key=lambda x: (len(x), x))

    def _define_equations(self):
        symbols_dict = {f'x{i:02d}': symbols(f'x{i:02d}') for i in range(1, len(self._equations) + 1)}
        symbols_dict.update({k: symbols(k) for k in self._observations})

        def parse_equation(eq_str):
            left, right = map(str.strip, eq_str.split('='))
            operators = {'~&': Nand, '~|': Nor, '~^': lambda a, b: Not(Xor(a, b))}
            for op, func in operators.items():
                if op in left:
                    a, b = map(str.strip, left.split(op))
                    return Eq(func(symbols_dict[a], symbols_dict[b]), symbols_dict[right])
            return Eq(eval(left, {**globals(), **symbols_dict}), eval(right, {**globals(), **symbols_dict}))
        return {eq_name: parse_equation(eq_str) for eq_name, eq_str in self._equations.items()}

    def _is_contradictory(self, equations):
        symbols = {s for eq in equations for s in eq.free_symbols}
        return not any(
            all(eq.lhs.subs(assignment) == eq.rhs.subs(assignment) if isinstance(eq, Eq) else bool(eq.subs(assignment))
                for eq in equations)
            for assignment in (dict(zip(symbols, values)) for values in product([True, False], repeat=len(symbols)))
        )

    def _get_diagnosis(self, minimal_conflicts: List[List[str]]) -> List[List[str]]:
        diagnosis_collection = [set()]
        for conflict in minimal_conflicts:
            current_diagnoses = list(diagnosis_collection)
            for diagnosis in current_diagnoses:
                if diagnosis.isdisjoint(set(conflict)):
                    diagnosis_collection = self._update_diagnosis(diagnosis, diagnosis_collection, conflict)
        return sorted([sorted(d) for d in diagnosis_collection], key=lambda x: (len(x), x))

    def _update_diagnosis(self, diagnosis: Set[str], diagnosis_collection: List[Set[str]], conflict: List[str]) -> List[Set[str]]:
        diagnosis_collection = [d for d in diagnosis_collection if d != diagnosis]
        new_diagnoses = []
        for component in conflict:
            new_diagnosis = diagnosis.union({component})
            if not any(new_diagnosis > existing for existing in diagnosis_collection):
                new_diagnoses.append(new_diagnosis)
        diagnosis_collection.extend(new_diagnoses)
        diagnosis_collection = [d for d in diagnosis_collection if not any(d > n_d for n_d in new_diagnoses)]
        return list({frozenset(d) for d in diagnosis_collection})
