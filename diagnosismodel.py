import faultdiagnosistoolbox as fdt
import sympy as sym
import importlib
import re
from minihit.hsdag import HsDag
from config import FAULTS, KNOWN_VARIABLES, UNKNOWN_VARIABLES, \
                   PREFIX_FAULT, PREFIX_SIGNAL, EQUATIONS, RELATIONS, \
                   TITLE, OBSERVATIONS


class DiagnosisModel:
    _variables = None
    _model_definition = None
    _model = None
    _logic_equations_count = -1
    _signal_equations_count = -1

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

    def get_minimal_conflicts_for_observations(self):
        if not self._model_ok:
            return None
        else:
            return self._get_residuals()

    def get_all_minimal_diagnosis(self):
        if not self._model_ok:
            return None
        else:
            return self._get_all_minimal_diagnosis()

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
        rels = []
        self._create_equations_for_logic(rels, equations)
        self._create_equations_for_known_variables(rels,
                                                   unknown_variables,
                                                   known_variables)
        return rels

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
        conflicts = self._model_definition[FAULTS]
        fsm = self._get_filtered_fsm()
        minimal_conflicts = []
        for fsm_row in fsm:
            conflict_list = [conflicts[i].split(PREFIX_FAULT)[1]
                             for i, elem in enumerate(fsm_row) if elem == 1]
            minimal_conflicts.append(sorted(conflict_list))
        return minimal_conflicts

    def _get_all_minimal_diagnosis(self):
        hs_dag = HsDag(self._get_all_minimal_conflicts())
        hs_dag.solve(True, False)
        minimal_hittings = list(hs_dag.generate_minimal_hitting_sets())
        for i, hitting_set in enumerate(minimal_hittings):
            minimal_hittings[i] = sorted(hitting_set)
        minimal_hittings.sort()
        return minimal_hittings

    def _get_mso_from_model(self):
        return self._model.MSO()

    def _get_fsm_from_mso(self):
        return self._model.FSM(self._get_mso_from_model())

    def _get_filtered_fsm(self):
        fsm = self._get_fsm_from_mso()
        filtered_fsm = []
        for fsm_row in fsm:
            if any(element != 0 for element in fsm_row):
                filtered_fsm.append(fsm_row)
        return filtered_fsm

    def _create_equations_for_logic(self, rels, relations):
        self._logic_equations_count = len(relations)
        for relation in relations:
            equation = self._transform_expression_logic(relation)
            rels.append(equation)

    def _create_equations_for_known_variables(self, rels, known_variables, unknown_variables):
        common_elements = set(unknown_variables) & set(known_variables)
        sorted_common_elements = sorted(common_elements)
        self._signal_equations_count = len(sorted_common_elements)
        for element in sorted_common_elements:
            equation = self._transform_expression_variable(element)
            rels.append(equation)

    def _transform_expression_logic(self, expression):
        pattern = re.compile(r'(.+?)\s*=\s*(\S+)\s*\((\S+)\)')
        match = pattern.match(expression)
        if match:
            left_side = match.group(1).strip()
            result = match.group(2).strip()
            fault = match.group(3)
            transformed_expression = self._transform_to_symbolic(
                f"-{result}+{left_side}+{PREFIX_FAULT}{fault}")
            return transformed_expression

    def _transform_expression_variable(self, variable):
        transformed_expression = self._transform_to_symbolic(f"-{variable}+{PREFIX_SIGNAL}{variable}")
        return transformed_expression

    def _transform_to_symbolic(self, equation):
        return sym.sympify(equation)

    def _get_residuals(self):
        residuals = []
        for i in range(len(self._get_mso_from_model())):
            function = self._generate_residuals(i)
            residual = self._solve_residuals(function)
            residuals.append(residual)
        return residuals

    def _generate_residuals(self, iterator):
        equations, selected_equation = self._prepare_equations_for_residuals(iterator)
        function_name = self._generate_residuals_function(equations, selected_equation)
        return function_name

    def _prepare_equations_for_residuals(self, iterator):
        equations = self._get_equations_for_residual(iterator)
        selected_equation = self._get_selected_equation_for_residual(equations)
        equations_without_selected = [equation for equation in equations if equation != selected_equation]
        print(f'Equations: {equations_without_selected}')
        return equations_without_selected, selected_equation

    def _generate_residuals_function(self, equations, selected_equation):
        gamma = self._model.Matching(equations)
        function_name = f'{self._variables[TITLE].replace(" ", "_")}_ResGen'
        self._model.SeqResGen(gamma, selected_equation, f'{function_name}')
        return function_name

    def _solve_residuals(self, function_name):
        residuals_module = importlib.import_module(function_name)
        function = getattr(residuals_module, function_name)
        residuals, _ = function(self._variables[OBSERVATIONS], [], None, 1)
        return residuals

    def _get_equations_for_residual(self, iterator):
        return self._get_mso_from_model()[iterator]

    def _get_selected_equation_for_residual(self, equations):
        for equation in equations:
            if equation >= self._logic_equations_count and \
               equation < self._logic_equations_count + self._signal_equations_count:
                return equation
