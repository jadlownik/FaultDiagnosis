PATH_EXAMPLES = 'examples\\'
TITLE = 'title'
UNKNOWN_VARIABLES = 'x'
FAULTS = 'f'
KNOWN_VARIABLES = 'z'
EQUATIONS = 'r'
OBSERVATIONS = 'o'
PREFIX_FAULT = 'f_'
PREFIX_SIGNAL = 'u_'
RELATIONS = 'rels'
OPENAI_API_MODEL = 'gpt-3.5-turbo-0125'
SD_INPUT = 'Input'
SD_OUTPUT = 'Output'
SD_ARITHMETIC_ADD = 'ADD(x) ∧ ¬AB(x) ⇒ Output(x) = Input1(x) + Input2(x)'
SD_ARITHMETIC_MULT = 'MULT(x) ∧ ¬AB(x) ⇒ Output(x) = Input1(x) × Input2(x)'
SD_LOGIC_AND = 'ANDgate(x) ∧ ¬AB(x) ⇒ Output(x) = Input1(x) ∧ Input2(x)'
SD_LOGIC_OR = 'ORgate(x) ∧ ¬AB(x) ⇒ Output(x) = Input1(x) ∨ Input2(x)'
GPT_SYSTEM_DESC = 'The task is to conduct diagnostic reasoning (DX approach),\
                   resulting in providing information about minimal conflicts\
                   (the smallest sets of system components that could explain\
                   the observed malfunctions) and minimal diagnoses (the smallest\
                   sets of components that cannot all be functioning correctly\
                   given the observed problems) In the examples located between\
                   the <examples></examples> tags, you have sample input data\
                   (<input></input>) and output data (<output></output>).\
                   The output data are the correct solutions for the given input data.\
                   The output data should be JSON.'
GPT_EXAMPLES = '<examples>\
                    <example_1>\
                        <input>\
                            COMPS = { A1, A2, M1, M2, M3 }\
                            SD = { ADD(x) ∧ ¬AB(x) ⇒ Output(x) = Input1(x) + Input2(x),\
                                   MULT(x) ∧ ¬AB(x) ⇒ Output(x) = Input1(x) × Input2(x),\
                                   ADD(A1), ADD(A2), MULT(M1), MULT(M2), MULT(M3),\
                                   Output(M1) = Input1(A1), Output(M2) = Input2(A1),\
                                   Output(M2) = Input1(A2), Output(M3) = Input2(A2),\
                                   Input2(M1) = Input1(M3) }\
                            OBS = { Input1(M1) = 2, Input2(M1) = 3, Input1(M2) = 2,\
                                    Input2(M2) = 3, Input1(M3) = 3, Input2(M3) = 2,\
                                    Output(A1) = 10, Output(A2) = 12 }\
                        </input>\
                        <output>\
                        {\
                        "minimal_conflicts": [\
                        ["A1", "M1", "M2"],\
                        ["A1", "A2", "M1", "M3"]\
                        ],\
                        "minimal_diagnosis": [\
                        ["A1"],\
                        ["M1"],\
                        ["A2", "M2"],\
                        ["M2", "M3"]\
                        ]\
                        }\
                        </output>\
                    </example_1>\
                    <example_2>\
                        <input>\
                            COMPS = { A1, A2, M1 }\
                            SD = { ADD(x) ∧ ¬AB(x) ⇒ Output(x) = Input1(x) + Input2(x),\
                                   MULT(x) ∧ ¬AB(x) ⇒ Output(x) = Input1(x) × Input2(x),\
                                   ADD(A1), ADD(A2), MULT(M1),\
                                   Output(A1) = Input1(M1), Output(A2) = Input2(M1) }\
                            OBS = { Input1(A1) = 1, Input2(A1) = 1,\
                                    Input1(A2) = 1, Input2(A2) = 1,\
                                    Output(M1) = 2 }\
                        </input>\
                        <output>\
                        {\
                        "minimal_conflicts": [\
                        ["A1", "M1", "M2"],\
                        ["A1", "A2", "M1", "M3"]\
                        ],\
                        "minimal_diagnosis": [\
                        ["A1"],\
                        ["M1"],\
                        ["A2", "M2"],\
                        ["M2", "M3"]\
                        ]\
                        }\
                        </output>\
                    </example_2>\
                </examples>'
