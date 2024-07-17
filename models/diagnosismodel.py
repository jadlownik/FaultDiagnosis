import faultdiagnosistoolbox as fdt
import sympy as sym
import importlib
import re
import os
from config.config import FAULTS, KNOWN_VARIABLES, UNKNOWN_VARIABLES, \
                   PREFIX_FAULT, PREFIX_SIGNAL, EQUATIONS, RELATIONS, \
                   TITLE, OBSERVATIONS


class DiagnosisModel:
    _variables = None
    _model_definition = None
    _model = None
    _logic_equations = -1

    def __init__(self):
        pass

    def create(self, variables):
        self._variables = variables
        x = self._create_unknown_variables(variables[UNKNOWN_VARIABLES])
        f = self._create_faults(variables[FAULTS])
        z = self._create_known_variables(variables[KNOWN_VARIABLES])
        r = self._create_relations(variables[EQUATIONS], variables[UNKNOWN_VARIABLES],
                                   variables[KNOWN_VARIABLES])
        self._create_model_definition(x, f, z, r)
        self._create_model()

    def get_all_minimal_conflicts(self):
        if not self._model_ok:
            return None
        else:
            return self._get_all_minimal_conflicts()

    def get_minimal_conflicts(self):
        if not self._model_ok:
            return None
        else:
            return self._get_minimal_conflicts()

    def get_all_minimal_diagnosis(self):
        if not self._model_ok:
            return None
        else:
            return self._get_all_minimal_diagnosis()

    def get_minimal_diagnosis(self):
        if not self._model_ok:
            return None
        else:
            return self._get_minimal_diagnosis()

    def _model_ok(self):
        # TODO: more complex model verification
        return self._model is not None

    def _create_unknown_variables(self, variables):
        vars = []
        for variable in variables:
            vars.append(str(variable))
        return vars

    def _create_faults(self, faults):
        vars = []
        for fault in faults:
            vars.append(PREFIX_FAULT + str(fault))
        return vars

    def _create_known_variables(self, variables):
        vars = []
        for variable in variables:
            vars.append(PREFIX_SIGNAL + str(variable))
        return vars

    def _create_relations(self, equations, unknown_variables, known_variables):
        relations = []
        self._create_relations_for_logic(relations, equations)
        self._create_relations_for_known_variables(relations,
                                                   unknown_variables,
                                                   known_variables)
        self._equations_count = len(relations)
        return relations

    def _create_model_definition(self, x, f, z, r):
        self._model_definition = {'type': 'Symbolic',
                                  UNKNOWN_VARIABLES: x,
                                  FAULTS: f,
                                  KNOWN_VARIABLES: z,
                                  RELATIONS: r}
        sym.var(self._model_definition[UNKNOWN_VARIABLES])
        sym.var(self._model_definition[FAULTS])
        sym.var(self._model_definition[KNOWN_VARIABLES])

    def _create_model(self):
        self._model = fdt.DiagnosisModel(self._model_definition)

    def _get_all_minimal_conflicts(self):
        fsm = self._get_filtered_fsm()
        return self._get_conflicts(fsm)

    def _get_minimal_conflicts(self):
        residulas = self._get_residuals()
        return self._get_conflicts(residulas)

    def _get_all_minimal_diagnosis(self):
        return self._get_diagnosis(self._get_all_minimal_conflicts())

    def _get_minimal_diagnosis(self):
        return self._get_diagnosis(self._get_minimal_conflicts())

    def _get_conflicts(self, data):
        conflicts = self._model_definition[FAULTS]
        result = []
        for data_row in data:
            conflict_list = [conflicts[i].split(PREFIX_FAULT)[1]
                             for i, elem in enumerate(data_row) if elem == 1]
            sorted_conflicts = sorted(conflict_list)
            result.append(sorted_conflicts)
        result.sort(key=lambda x: (len(x), x))
        return result

    def _get_diagnosis(self, minimal_conflicts):
        diagnosis_collection = [set()]
        for conflict in minimal_conflicts:
            current_diagnoses = list(diagnosis_collection)
            for diagnosis in current_diagnoses:
                if diagnosis.isdisjoint(conflict):
                    diagnosis_collection = self._update_diagnosis(diagnosis, diagnosis_collection, conflict)
        for i, hitting_set in enumerate(diagnosis_collection):
            diagnosis_collection[i] = sorted(hitting_set)
        diagnosis_collection.sort(key=lambda x: (len(x), x))
        return [list(hit_set) for hit_set in diagnosis_collection]

    def _update_diagnosis(self, diagnosis, diagnosis_collection, conflict):
        diagnosis_collection = [c for c in diagnosis_collection if c != diagnosis]
        new_diagnoses = []
        for component in conflict:
            new_diagnosis = diagnosis.union({component})
            if not any(new_diagnosis > existing for existing in diagnosis_collection):
                new_diagnoses.append(new_diagnosis)
        diagnosis_collection.extend(new_diagnoses)
        diagnosis_collection = [d for d in diagnosis_collection if not any(d > n_d for n_d in new_diagnoses)]
        diagnosis_collection = list(set(tuple(sorted(c)) for c in diagnosis_collection))
        diagnosis_collection = [set(c) for c in diagnosis_collection]
        return diagnosis_collection

    def _get_mso_from_model(self):
        return self._model.MSO()

    def _get_fsm_from_mso(self):
        return self._model.FSM(self._get_mso_from_model())

    def _get_filtered_fsm(self):
        fsm = self._get_fsm_from_mso()
        filtered_fsm = []
        for fsm_row in fsm:
            if any(element == 0 for element in fsm_row) or len(fsm) == 1:
                filtered_fsm.append(fsm_row)
        return filtered_fsm

    def _get_filtered_mso(self):
        fsm = self._get_fsm_from_mso()
        mso = self._get_mso_from_model()
        filtered_mso = []
        for i, fsm_row in enumerate(fsm):
            if any(element == 0 for element in fsm_row) or len(fsm) == 1:
                filtered_mso.append(mso[i])
        return filtered_mso

    def _create_relations_for_logic(self, relations, equations):
        for equation in equations:
            relation = self._transform_expression_logic(equation)
            relations.append(relation)

    def _create_relations_for_known_variables(self, relations, known_variables, unknown_variables):
        common_elements = set(unknown_variables) & set(known_variables)
        sorted_common_elements = sorted(common_elements)
        for element in sorted_common_elements:
            relation = self._transform_expression_variable(element)
            relations.append(relation)

    def _transform_expression_logic(self, expression):
        pattern = re.compile(r'(\S+):\s*(.+?)\s*=\s*(\S+)')
        match = pattern.match(expression)
        if match:
            fault = match.group(1).strip()
            left_side = match.group(2)\
                             .strip() \
                             .replace('~^', 'xnor') \
                             .replace('~&', 'nand') \
                             .replace('~|', 'nor') \
                             .replace('&', 'and') \
                             .replace('|', 'or') \
                             .replace('~', 'not') \
                             .replace('^', 'xor')
            left_side = f'({left_side})'
            result = match.group(3)
            if 'nand' in left_side:
                left_side = f'(1 - {left_side.replace('nand', 'and')})'
            elif 'nor' in left_side:
                left_side = f'(1 - {left_side.replace('nor', 'or')})'
            elif 'xnor' in left_side:
                left_side = f'(1 - {left_side.replace('xnor', 'xor')})'

            transformed_expression = self._transform_to_symbolic(
                f'-{result} + {left_side} + {PREFIX_FAULT}{fault}')
            return transformed_expression

    def _transform_expression_variable(self, variable):
        transformed_expression = self._transform_to_symbolic(f'-{variable} + {PREFIX_SIGNAL}{variable}')
        return transformed_expression

    def _transform_to_symbolic(self, equation):
        return sym.sympify(equation)

    def _get_residuals(self):
        residuals = []
        fsm = self._get_filtered_fsm()
        for i in range(len(self._get_filtered_mso())):
            function = self._generate_residual(i)
            residual = self._solve_residual(function)
            if residual != 0:
                residuals.append(fsm[i])
            self._remove_residual_function(function)
        return residuals

    def _generate_residual(self, iterator):
        equations, selected_equation = self._prepare_equations_for_residual(iterator)
        function_name = self._generate_residual_function(equations, selected_equation, iterator)
        return function_name

    def _remove_residual_function(self, function):
        if os.path.exists(f'{function}.py'):
            os.remove(f'{function}.py')

    def _prepare_equations_for_residual(self, iterator):
        equations = self._get_equations_for_residual(iterator)
        selected_equation = self._get_selected_equation_for_residual(equations)
        equations_without_selected = [equation for equation in equations if equation != selected_equation]
        return equations_without_selected, selected_equation

    def _generate_residual_function(self, equations, selected_equation, iterator):
        gamma = self._model.Matching(equations)
        function_name = f'{self._variables[TITLE].replace(' ', '_')}_ResGen{iterator}'
        self._model.SeqResGen(gamma, selected_equation, f'{function_name}')
        return function_name

    def _solve_residual(self, function_name):
        residuals_module = importlib.import_module(function_name)
        function = getattr(residuals_module, function_name)
        residual, _ = function(self._variables[OBSERVATIONS], [], None, 1)
        return residual

    def _get_equations_for_residual(self, iterator):
        return self._get_mso_from_model()[iterator]

    def _get_selected_equation_for_residual(self, equations):
        return max(equations)
