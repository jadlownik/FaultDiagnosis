from config.config import SD_ARITHMETIC_ADD, SD_ARITHMETIC_MULT, SD_LOGIC_AND, SD_LOGIC_OR, \
    SD_LOGIC_NAND, SD_LOGIC_NOR, SD_LOGIC_NOT, SD_LOGIC_XOR, SD_LOGIC_XNOR, \
    SD_INPUT, SD_OUTPUT, FAULTS, EQUATIONS, OBSERVATIONS, KNOWN_VARIABLES


class FOLService:
    def __init__(self):
        pass

    def convert_to_FOL(self, variables):
        comps = self._get_components(variables[FAULTS])
        sd = self._get_system_description(variables[EQUATIONS])
        obs = self._get_observations(variables[EQUATIONS], variables[KNOWN_VARIABLES], variables[OBSERVATIONS])

        fol = comps + sd + obs

        return fol

    def _get_components(self, faults):
        return 'COMPS = ' + '{ ' + ', '.join(faults) + ' } '

    def _get_system_description(self, equations):
        system_description = 'SD = { '
        system_description = self._get_system_description_introduction(system_description, equations)
        system_description = self._get_system_description_components(system_description, equations)
        system_description = self._get_system_description_equations(system_description, equations)
        return system_description

    def _get_system_description_introduction(self, system_description, equations):
        sd_desc = []
        for equation in equations:
            if '+' in equation and SD_ARITHMETIC_ADD not in sd_desc:
                sd_desc.append(SD_ARITHMETIC_ADD)
            elif '*' in equation and SD_ARITHMETIC_MULT not in sd_desc:
                sd_desc.append(SD_ARITHMETIC_MULT)
            elif '~^' in equation and SD_LOGIC_XNOR not in sd_desc:
                sd_desc.append(SD_LOGIC_XNOR)
            elif '~&' in equation and SD_LOGIC_NAND not in sd_desc:
                sd_desc.append(SD_LOGIC_NAND)
            elif '~|' in equation and SD_LOGIC_NOR not in sd_desc:
                sd_desc.append(SD_LOGIC_NOR)
            elif '~' in equation and SD_LOGIC_NOT not in sd_desc:
                sd_desc.append(SD_LOGIC_NOT)
            elif '&' in equation and SD_LOGIC_AND not in sd_desc:
                sd_desc.append(SD_LOGIC_AND)
            elif '|' in equation and SD_LOGIC_OR not in sd_desc:
                sd_desc.append(SD_LOGIC_OR)
            elif '^' in equation and SD_LOGIC_XOR not in sd_desc:
                sd_desc.append(SD_LOGIC_XOR)
        system_description += ', '.join(sd_desc) + ', '
        return system_description

    def _get_system_description_introduction_element():
        pass

    def _get_system_description_components(self, system_description, equations):
        sd_comps = []
        for equation in equations:
            if '*' in equation:
                sd_comps.append(f'MULT({equation.split(':')[0].strip()})')
            elif '+' in equation:
                sd_comps.append(f'ADD({equation.split(':')[0].strip()})')
            elif '~^' in equation:
                sd_comps.append(f'XNORgate({equation.split(':')[0].strip()})')
            elif '~&' in equation:
                sd_comps.append(f'NANDgate({equation.split(':')[0].strip()})')
            elif '~|' in equation:
                sd_comps.append(f'NORgate({equation.split(':')[0].strip()})')
            elif '~' in equation:
                sd_comps.append(f'NOTgate({equation.split(':')[0].strip()})')
            elif '&' in equation:
                sd_comps.append(f'ANDgate({equation.split(':')[0].strip()})')
            elif '|' in equation:
                sd_comps.append(f'ORgate({equation.split(':')[0].strip()})')
            elif '^' in equation:
                sd_comps.append(f'XORgate({equation.split(':')[0].strip()})')

        system_description += ', '.join(sd_comps) + ', '
        return system_description

    def _get_system_description_equations(self, system_description, equations):
        outputs = {}
        inputs_sources = {}
        relations = []

        for eq in equations:
            equation = eq.replace(' ', '')
            parts = equation.split(':')
            component = parts[0]
            expression = parts[1]

            if '=' in expression:
                left, right = expression.split('=')
                terms = left.split('+') if '+' in left else \
                    left.split('*') if '*' in left else \
                    left.split('~^') if '~^' in left else \
                    left.split('~&') if '~&' in left else \
                    left.split('~|') if '~|' in left else \
                    left.split('&') if '&' in left else \
                    left.split('|') if '|' in left else \
                    left.split('^') if '^' in left else \
                    left.split('~')

                for i, term in enumerate(terms):
                    if term in outputs:
                        relations.append(f'{SD_OUTPUT}({outputs[term]}) = {SD_INPUT}{i + 1}({component})')

                outputs[right] = component
                inputs_sources[component] = (terms), right

        for key, (inputs, outputs) in inputs_sources.items():
            for i, input in enumerate(inputs):
                for blk_key, (blk_inputs, blk_output) in inputs_sources.items():
                    if blk_key != key and \
                       input in blk_inputs and \
                       self._is_output_not_input_for_any_equation(blk_output, inputs_sources):
                        relation = f'{SD_INPUT}{i + 1}({key}) = {SD_INPUT}{blk_inputs.index(input) + 1}({blk_key})'
                        rev_relation = f'{SD_INPUT}{blk_inputs.index(input) + 1}({blk_key}) = {SD_INPUT}{i + 1}({key})'
                        if relation not in relations and rev_relation not in relations:
                            relations.append(relation)

        system_description += ', '.join(relations) + ' } '
        return system_description

    def _is_output_not_input_for_any_equation(self, output, all_inputs):
        for key, (inputs, outputs) in all_inputs.items():
            if output in inputs:
                return True
        return False

    def _get_observations(self, equations, variables, observations):
        obs = []
        obs_dict = self._get_observations_dictionary(variables, observations)
        for eq in equations:
            equation = eq.replace(' ', '')
            parts = equation.split(':')
            component = parts[0]
            expression = parts[1]

            if '=' in expression:
                inputs, output = expression.split('=')
                inputs_variables = inputs.split('+') if '+' in inputs else \
                    inputs.split('*') if '*' in inputs else \
                    inputs.split('~^') if '~^' in inputs else \
                    inputs.split('~&') if '~&' in inputs else \
                    inputs.split('~|') if '~|' in inputs else \
                    inputs.split('&') if '&' in inputs else \
                    inputs.split('|') if '|' in inputs else \
                    inputs.split('^') if '^' in inputs else \
                    inputs.split('~')

                for i, input in enumerate(inputs_variables):
                    if input in variables:
                        obs.append(f'{SD_INPUT}{i + 1}({component}) = {obs_dict[input]}')

                if output in variables:
                    obs.append(f'{SD_OUTPUT}({component}) = {obs_dict[output]}')

        return 'OBS = { ' + ', '.join(obs) + ' }'

    def _get_observations_dictionary(self, variables, observations):
        return {variable: value for variable, value in zip(variables, observations)}
