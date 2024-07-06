class FOLService:
    def __init__(self):
        pass

    def convert_to_FOL(self, r, f, z, o):
        comps = self._get_components(f)
        sd = self._get_system_description(r)
        obs = self._get_observations(r, z, o)

        fol = comps + sd + obs

        return fol

    def _get_components(self, faults):
        return "COMPS = " + "{ " + ", ".join(faults) + " }\n"

    def _get_system_description(self, equations):
        system_description = ""
        system_description = self._get_system_description_introduction(system_description)
        system_description += "\n"
        system_description = self._get_system_description_components(system_description, equations)
        system_description += "\n"
        system_description = self._get_system_description_equations(system_description, equations)
        system_description += "\n"
        return system_description

    def _get_system_description_introduction(self, system_description):
        system_description += "SD = { ADD(x) ∧ ¬AB(x) ⇒ Output(x) = Input1(x) + Input2(x),\n"
        system_description += "MULT(x) ∧ ¬AB(x) ⇒ Output(x) = Input1(x) × Input2(x),"
        return system_description

    def _get_system_description_components(self, system_description, relations):
        sd_comps = []
        for i in relations:
            if "*" in i:
                sd_comps.append(f"MULT({i.split(':')[0].strip()})")
            elif "+" in i:
                sd_comps.append(f"ADD({i.split(':')[0].strip()})")

        system_description += ", ".join(sd_comps) + ", "
        return system_description

    def _get_system_description_equations(self, system_description, equations):
        outputs = {}
        inputs_sources = {}
        relations = []

        for eq in equations:
            equation = eq.replace(" ", "")
            parts = equation.split(':')
            component = parts[0]
            expression = parts[1]

            if '=' in expression:
                left, right = expression.split('=')
                terms = left.split('+') if '+' in left else left.split('*')

                for i, term in enumerate(terms):
                    if term in outputs:
                        relations.append(f'Output({outputs[term]}) = Input{i+1}({component})')

                outputs[right] = component
                inputs_sources[component] = (terms), right

        for key, (inputs, outputs) in inputs_sources.items():
            for i, input in enumerate(inputs):
                for blk_key, (blk_inputs, blk_output) in inputs_sources.items():
                    if blk_key != key and \
                       input in blk_inputs and \
                       self._is_output_not_input_for_any_equation(blk_output, inputs_sources):
                        relation = f"Input{i+1}({key}) = Input{blk_inputs.index(input)+1}({blk_key})"
                        rev_relation = f"Input{blk_inputs.index(input)+1}({blk_key}) = Input{i+1}({key})"
                        if relation not in relations and rev_relation not in relations:
                            relations.append(relation)

        system_description += ", ".join(relations) + " }"
        return system_description

    def _is_output_not_input_for_any_equation(self, output, all_inputs):
        for key, (inputs, outputs) in all_inputs.items():
            nok = output in inputs
            if nok:
                return True
        return False

    def _get_observations(self, equations, variables, observations):
        obs = []
        obs_dict = self._get_observations_dictionary(variables, observations)
        for eq in equations:
            equation = eq.replace(" ", "")
            parts = equation.split(':')
            component = parts[0]
            expression = parts[1]

            if '=' in expression:
                inputs, output = expression.split('=')
                inputs_variables = inputs.split('+') if '+' in inputs else inputs.split('*')

                for i, input in enumerate(inputs_variables):
                    if input in variables:
                        obs.append(f'Input{i+1}({component}) = {obs_dict[input]}')

                if output in variables:
                    obs.append(f'Output({component}) = {obs_dict[output]}')

        return "OBS = { " + ", ".join(obs) + " }"

    def _get_observations_dictionary(self, variables, observations):
        return {variable: value for variable, value in zip(variables, observations)}
