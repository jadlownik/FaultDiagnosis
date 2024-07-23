PATH_EXAMPLES = 'examples\\'
PRINT_TO_CONSOLE = True
TITLE = 'title'
UNKNOWN_VARIABLES = 'x'
FAULTS = 'f'
KNOWN_VARIABLES = 'z'
EQUATIONS = 'r'
OBSERVATIONS = 'o'
PREFIX_FAULT = 'f_'
PREFIX_SIGNAL = 'u_'
RELATIONS = 'rels'
OPENAI_API_MODEL = 'gpt-4o'
JSON_KEY_CONFLICTS = 'minimal_conflicts'
JSON_KEY_DIAGNOSIS = 'minimal_diagnosis'
SD_INPUT = 'Input'
SD_OUTPUT = 'Output'
SD_ADD_SYMBOL = '+'
SD_MULT_SYMBOL = '*'
SD_AND_SYMBOL = '∧'
SD_OR_SYMBOL = '∨'
SD_NOT_SYMBOL = '¬'
SD_XOR_SYMBOL = '⊕'
SD_ARITHMETIC_ADD = 'ADD(x) ∧ ¬AB(x) ⇒ Output(x) = Input1(x) + Input2(x)'
SD_ARITHMETIC_MULT = 'MULT(x) ∧ ¬AB(x) ⇒ Output(x) = Input1(x) × Input2(x)'
SD_LOGIC_AND = 'ANDgate(x) ∧ ¬AB(x) ⇒ Output(x) = Input1(x) ∧ Input2(x)'
SD_LOGIC_OR = 'ORgate(x) ∧ ¬AB(x) ⇒ Output(x) = Input1(x) ∨ Input2(x)'
SD_LOGIC_NOT = 'NOTgate(x) ∧ ¬AB(x) ⇒ Output(x) = ¬Input(x)'
SD_LOGIC_XOR = 'XORgate(x) ∧ ¬AB(x) ⇒ Output(x) = Input1(x) ⊕ Input2(x)'
SD_LOGIC_NAND = 'NANDgate(x) ∧ ¬AB(x) ⇒ Output(x) = ¬(Input1(x) ∧ Input2(x))'
SD_LOGIC_NOR = 'NORgate(x) ∧ ¬AB(x) ⇒ Output(x) = ¬(Input1(x) ∨ Input2(x))'
SD_LOGIC_XNOR = 'XNORgate(x) ∧ ¬AB(x) ⇒ Output(x) = ¬(Input1(x) ⊕ Input2(x))'
GPT_SYSTEM_DESC = (
    'The task is to conduct diagnostic reasoning using the DX approach,'
    'to identify minimal conflicts (the smallest sets of system components '
    'that could explain observed malfunctions) and minimal diagnoses (the '
    'smallest sets of components that cannot all be functioning correctly '
    'given observed problems). The Hitting Set Tree (HST) algorithm should '
    'be used to determine minimal diagnoses from minimal conflicts. Within the <examples></examples> '
    'tags, you will find sample input data (<input></input>) and expected '
    'output data (<output></output>). COMPS lists all components in the '
    'system, OBS denotes the states of components during system malfunctions, '
    'and SD presents logical rules in First-Order Logic (FOL) describing '
    'expected system behavior and identifying violated conditions. The output '
    'data are provided in JSON format.'
                  )
GPT_EXAMPLES = (
    '<examples>'
        '<example_1>'
            '<input>'
                'COMPS = { A1, A2, M1, M2, M3 } '
                'SD = { ADD(x) ∧ ¬AB(x) ⇒ Output(x) = Input1(x) + Input2(x), '
                        'MULT(x) ∧ ¬AB(x) ⇒ Output(x) = Input1(x) × Input2(x), '
                        'ADD(A1), ADD(A2), MULT(M1), MULT(M2), MULT(M3), '
                        'Output(M1) = Input1(A1), Output(M2) = Input2(A1), '
                        'Output(M2) = Input1(A2), Output(M3) = Input2(A2), '
                        'Input2(M1) = Input1(M3) } '
                'OBS = { Input1(M1) = 2, Input2(M1) = 3, Input1(M2) = 2, '
                        'Input2(M2) = 3, Input1(M3) = 3, Input2(M3) = 2, '
                        'Output(A1) = 12, Output(A2) = 12 } '
            '</input>'
            '<output>'
            '{'
            '"minimal_conflicts": []'
            '"minimal_diagnosis": []'
            '}'
            '</output>'
        '</example_1>'
        '<example_2>'
            '<input>'
                'COMPS = { A1, A2, M1, M2, M3 }'
                'SD = { ADD(x) ∧ ¬AB(x) ⇒ Output(x) = Input1(x) + Input2(x),'
                        'MULT(x) ∧ ¬AB(x) ⇒ Output(x) = Input1(x) × Input2(x),'
                        'ADD(A1), ADD(A2), MULT(M1), MULT(M2), MULT(M3),'
                        'Output(M1) = Input1(A1), Output(M2) = Input2(A1),'
                        'Output(M2) = Input1(A2), Output(M3) = Input2(A2),'
                        'Input2(M1) = Input1(M3) }'
                'OBS = { Input1(M1) = 2, Input2(M1) = 3, Input1(M2) = 2,'
                        'Input2(M2) = 3, Input1(M3) = 3, Input2(M3) = 2,'
                        'Output(A1) = 10, Output(A2) = 12 }'
            '</input>'
            '<output>'
            '{'
            '"minimal_conflicts": ['
            '["A1", "M1", "M2"],'
            '["A1", "A2", "M1", "M3"]'
            '],'
            '"minimal_diagnosis": ['
            '["A1"],'
            '["M1"],'
            '["A2", "M2"],'
            '["M2", "M3"]'
            ']'
            '}'
            '</output>'
        '</example_2>'
        '<example_3>'
            '<input>'
                'COMPS = { A1, A2, M1 }'
                'SD = { ADD(x) ∧ ¬AB(x) ⇒ Output(x) = Input1(x) + Input2(x),'
                        'MULT(x) ∧ ¬AB(x) ⇒ Output(x) = Input1(x) × Input2(x),'
                        'ADD(A1), ADD(A2), MULT(M1),'
                        'Output(A1) = Input1(M1), Output(A2) = Input2(M1) }'
                'OBS = { Input1(A1) = 1, Input2(A1) = 1,'
                        'Input1(A2) = 1, Input2(A2) = 1,'
                        'Output(M1) = 4 }'
            '</input>'
            '<output>'
            '{'
            '"minimal_conflicts": [],'
            '"minimal_diagnosis": []'
            '}'
            '</output>'
        '</example_3>'
        '<example_4>'
            '<input>'
                'COMPS = { A1, A2, M1 }'
                'SD = { ADD(x) ∧ ¬AB(x) ⇒ Output(x) = Input1(x) + Input2(x),'
                        'MULT(x) ∧ ¬AB(x) ⇒ Output(x) = Input1(x) × Input2(x),'
                        'ADD(A1), ADD(A2), MULT(M1),'
                        'Output(A1) = Input1(M1), Output(A2) = Input2(M1) }'
                'OBS = { Input1(A1) = 1, Input2(A1) = 1,'
                        'Input1(A2) = 1, Input2(A2) = 1,'
                        'Output(M1) = 2 }'
            '</input>'
            '<output>'
            '{'
            '"minimal_conflicts": ['
            '["A1", "A2", "M1"]'
            '],'
            '"minimal_diagnosis": ['
            '["A1"],'
            '["A2"],'
            '["M1"]'
            ']'
            '}'
            '</output>'
        '</example_4>'
    '</examples>'
            )

GPT_TO_MSO_GENERATE = '''
'equations' the equations building the system in format (numer of equation, equation, unkonwns in equation). 
Analyse all possible combinations of systems of equations so that the 
sum of unknowns in the equations is exactly one (1) less than the 
number of equations, and the sum of the same unknown in the equation 
is to be equal to 2. In mso_generator.txt you have a python program which can do it.
As the result give me the list of lists with numbers of eqautions.
Plaese use code interperter aand code belowe to give me right answer.
Output should be in JSON.
Remember THE SUM OF UNKONOWNS VARIABLES MUST BE ONE LESS THEN THE NUMBER OF EQUATIONS!

Code:
def find_unknowns(equations_subset):
    unknowns = set()
    for eq in equations_subset:
        unknowns.update(eq[2])
    return unknowns

def count_unknowns(equations_subset):
    counter = {}
    for eq in equations_subset:
        for var in eq[2]:
            if var in counter:
                counter[var] += 1
            else:
                counter[var] = 1
    return counter

num_equations = len(equations)
result = []

for r in range(2, num_equations + 1):
    for subset in combinations(equations, r):
        unknowns = find_unknowns(subset)
        if len(unknowns) == r - 1:
            counter = count_unknowns(subset)
            if all(count == 2 for count in counter.values()):
                result.append([eq[0] for eq in subset])
Example:
'unknown' = ['x01', 'x02', 'x03'] 
'equations' = ['M1: a * c = x01', 'M2: b * d = x02', 'M3: c * e = x03', 'A1: x01 + x02 = f', 'A2: x02 + x03 = g ']
For equations number [0, 1, 3] we have:
Unknowns x01, x02. 
Number of equations = 3, 
number of unknowns = 2, 
number of occurrences of x01 = 2, 
number of occurrences of x02 = 2. 
Output:
{
   'mso' = [[0, 1, 3]]
}

'''

# <input_data_format>
# 'equations_part1' the equations building the system in format (numer of equation, equation, unkonwns in equation). 
# 'equations_part2' all equations are numbered starting from 0
# 'mso' each list consists of numbers representing the equation numbers from 'equations_part2' and together they form a system of equations
# 'data' varaibles which should be used to solve system of equations.
# </input_data_format>

GPT_KNOWN_MSO = '''
Your task is to generate equations and solve them. In 'equations', 
all equations are numbered starting from 0. In 'mso', each list 
consists of numbers representing the equation numbers from 
'equations' and together they form a system of equations. 
Each system of equations can be solved using the variable values 
from 'data'. The solved system of equations may be inconsistent. 
This means that the obtained result for the given variables does 
not match the expected result, for example, 10 ≠ 12, or when from 
two independent equations, the result for the same variable is 
different, for example, x02 = 4, x02 = 6, 4 ≠ 6.If the system  
of equations is correct you can go chech the next system of eqautions.
If the system  of equations is incorrect, check which for which list 
from 'mso' the system of equations was created and for each element
from list, add to the value that appears before the colon ':'. 
Create a new list of lists called 'minimal_conflicts' and return 
it in output. Please solve the following problem. Final answer should
contain json with 'minimal_conflicts'. 
Between <example></example> you have solved example.
<example>
<input>
equations = ['M1: a * c = x01',
'M2: b * d = x02',
'M3: c * e = x03',
'A1: x01 + x02 = f',
'A2: x02 + x03 = g ']
mso = [[2, 4, 1],
[2, 4, 0, 3],
[1, 0, 3]]
data = ['a = 2', 'b = 2', 'c = 3', 'd = 3', 'e = 2', 'f = 12', 'g = 10']
</input>
<operations>
For MSO [2, 4, 1]:
    Equations involved:
    M3: c * e = x03
    A2: x02 + x03 = g
    M2: b * d = x02
    Substituting data values:
    M3: 3 * 2 = x03 ⟹ x03 = 6
    M2: 2 * 3 = x02 ⟹ x02 = 6
    A2: x02 + x03 = 10 ⟹ 6 + 6 = 10 ⟹ 12 ≠ 10
    This system is inconsistent. The labels for the involved equations are M3, A2, and M2.

For MSO [2, 4, 0, 3]:
    Equations involved:
    M3: c * e = x03
    A2: x02 + x03 = g
    M1: a * c = x01
    A1: x01 + x02 = f
    Substituting data values:
    M3: 3 * 2 = x03 ⟹ x03 = 6
    M2: 2 * 3 = x02 ⟹ x02 = 6
    M1: 2 * 3 = x01 ⟹ x01 = 6
    A2: x02 + x03 = 10 ⟹ 6 + 6 = 10 ⟹ 12 ≠ 10
    A1: x01 + x02 = 12 ⟹ 6 + 6 = 12
    This system is inconsistent. The labels for the involved equations are M3, A2, M1, and A1.`

For MSO [1, 0, 3]:
    Equations involved:
    M2: b * d = x02
    M1: a * c = x01
    A1: x01 + x02 = f
    Substituting data values:
    M2: 2 * 3 = x02 ⟹ x02 = 6
    M1: 2 * 3 = x01 ⟹ x01 = 6
    A1: x01 + x02 = 12 ⟹ 6 + 6 = 12 ⟹ 12 = 12
    This system is consistent.

Based on the evaluation, the minimal conflicts list for the inconsistent systems are:
    For [2, 4, 1]: ['M3', 'A2', 'M2']
    For [2, 4, 0, 3]: ['M3', 'A2', 'M1', 'A1']
</operations>
<output>
{
"minimal_conflicts": [['M3', 'A2', 'M2'], ['M3', 'A2', 'M1', 'A1']]
}
</output>
</example>
'''

GIVE_ME_FUCKING_JSON = '''
From your last answer return me only JSON!!!
[OUTPUT ONLY JSON]
'''
# '''
# Input Format:
# 'equations':
# List of strings, each representing an equation. The format is [label]: [expression], e.g., 'A1: a + b = x02'.
# 'mso':
# List of lists, each containing integers representing the indices of the equations in the equations list.
# 'data':
# List of strings, each representing a variable assignment in the format [variable] = [value], e.g., 'a = 1'.
# Example Input:
# equations = ['A1: a + b = x02', 'M1: c * d = x01', 'M2: e * x01 = x03', 'A2: x02 + x03 = x04', 'M3: f * x04 = h', 'M4: x04 * g = i']
# mso = [[5, 4], [5, 0, 1, 2, 3], [4, 0, 1, 2, 3]]
# data = ['a = 1', 'b = 1', 'c = 1', 'd = 1', 'e = 1', 'f = 1', 'g = 1', 'h = 3', 'i = 3']
# Expected Output:
# The output should be a JSON object with the key "minimal_conflicts" and a value of a list of lists, each representing a set of labels for inconsistent equations.

# Correct Approach:
# 1. Parse the Data:
# - Extract variable assignments from the data list.
# - Substitute values in the equations using these assignments.
# 2.Check Each System of Equations (MSO):
# -Evaluate each system of equations.
# -Identify inconsistencies in the results.
# -For each inconsistent system, determine the corresponding labels from the equations list.
# 3.Create the Minimal Conflicts List:
# -For each inconsistent system, list the labels of the involved equations.

# Revised Example Execution:
# 1. Parse the Data:
# data_dict = {'a': 1, 'b': 1, 'c': 1, 'd': 1, 'e': 1, 'f': 1, 'g': 1, 'h': 3, 'i': 3}
# 2. Evaluate Each System:
#     For MSO [5, 4]:
#         Equations:
#         M4: x04 * g = i ⟹ x04 * 1 = 3 ⟹ x04 = 3
#         M3: f * x04 = h ⟹ 1 * x04 = 3 ⟹ x04 = 3
#         Both equations agree, so this system is consistent.
#     For MSO [5, 0, 1, 2, 3]:
#         Equations:
#         M4: x04 * g = i ⟹ x04 * 1 = 3 ⟹ x04 = 3
#         A1: a + b = x02 ⟹ 1 + 1 = x02 ⟹ x02 = 2
#         M1: c * d = x01 ⟹ 1 * 1 = x01 ⟹ x01 = 1
#         M2: e * x01 = x03 ⟹ 1 * 1 = x03 ⟹ x03 = 1
#         A2: x02 + x03 = x04 ⟹ 2 + 1 = x04 ⟹ x04 = 3
#         All equations agree, so this system is consistent.
#     For MSO [4, 0, 1, 2, 3]:
#         Equations:
#         M3: f * x04 = h ⟹ 1 * x04 = 3 ⟹ x04 = 3
#         A1: a + b = x02 ⟹ 1 + 1 = x02 ⟹ x02 = 2
#         M1: c * d = x01 ⟹ 1 * 1 = x01 ⟹ x01 = 1
#         M2: e * x01 = x03 ⟹ 1 * 1 = x03 ⟹ x03 = 1
#         A2: x02 + x03 = x04 ⟹ 2 + 1 = x04 ⟹ x04 = 3
#         All equations agree, so this system is consistent.
# Output:
# Since all systems are consistent, the minimal_conflicts list should be empty.

# Corrected Output:
# {
#   "minimal_conflicts": []
# }

# Clarifications and Improvements:
#     To ensure clarity in the problem statement:
#     - Provide a clear format for input and output.
#     - Emphasize the need to check each system of equations individually and list the corresponding labels for inconsistent systems.
#     - Provide an example with inconsistent results to illustrate the process clearly.
# '''

# TEST = 'Your task is to conduct diagnostic reasoning for a given set of data. The data is formatted as follows:
# <input> title = 'Example 2 classic polybox' x = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'x01', 'x02', 'x03'] f = ['M1', 'M2', 'M3', 'A1', 'A2'] z = ['a', 'b', 'c', 'd', 'e', 'f', 'g'] r = ['M1: a * c = x01', 'M2: b * d = x02', 'M3: c * e = x03', 'A1: x01 + x02 = f', 'A2: x02 + x03 = g '] o = [2, 2, 3, 3, 2, 10, 10] </input>
# Where:
# x is the set of all variables present in the system.
# f are all the components in the system where faults might occur.
# z are all variables with known values from observations.
# r are equations describing the system; the value before ":" indicates the component where the calculation occurs.
# o are observations for the known variables listed in the order of the known variables, i.e., a = 2, b = 2, c = 3, d = 3, e = 2, f = 10, g = 10.
# Your task is to identify all possible minimal conflicts and minimal diagnoses for the analyzed example and observed data.
# First, determine all possible minimal conflict sets that the analyzed example is sensitive to. The set [M1, M2, M3, A1, A2] will be rejected because it is not minimal and contains all components. Faults in any component within the set [M1, M2, A1] lead to incorrect observation of 'f'. Faults in any component within the set ['M2', 'M3', 'A2'] lead to incorrect observation of 'g'.
# In summary, all minimal conflicts for the analyzed example are: [['M1', 'M2', 'A1'], ['M2', 'M3', 'A2']]
# To determine minimal conflicts for the observed data, the obtained system must be analyzed. Notably, known variables can be divided into input and output variables. Perform calculations to check if the observed output values are obtained from the input data.
# M1: 2 * 3 = 6 M2: 2 * 3 = 6 M3: 3 * 2 = 6 A1: 6 + 6 = 12 A2: 6 + 6 = 12
# As observed, the values for variables 'f' and 'g' are incorrect. In such a case, we need to check where the fault might have occurred. To do this, follow the path from output to output leading to the result.
# To obtain the result for variable 'f', calculations must occur in component A1. The input data for component A1 are x01 and x02. x01 is the output of component M1, and x02 is the output of component M2. The input data for components M1 and M2 come from variables a, c and b, d, which are known. Thus, the result differing from the observation might be due to a fault in any component of the set ['A1', 'M1', 'M2'].
# To obtain the result for variable 'g', calculations must occur in component A2. The input data for component A2 are x02 and x03. x02 is the output of component M2, and x03 is the output of component M3. The input data for components M2 and M3 come from variables b, d and c, e, which are known. Thus, the result differing from the observation might be due to a fault in any component of the set ['A2', 'M2', 'M3'].
# Having the set of minimal conflicts for the analyzed example: [['A1', 'M1', 'M2'], ['A2', 'M2', 'M3']] please identify all minimal hitting sets for the given sets. A minimal hitting set is a set that contains at least one element from each set in the collection and is minimal with respect to this property (i.e., removing any element would cause the set to no longer satisfy this property). Minimal hitting sets is a set of minimal dingosis for given example.
# Having the set of minimal conflicts and minimal diagnoses concludes the diagnostic reasoning. Remember, if the observation results are correct according to the calculations made during diagnostic reasoning, then the minimal conflict set and minimal diagnoses WILL BE EMPTY!!!
# You should return ONLY JSON with minimal conflicts (key 'minimal_conflicts') and minimal diagnoses (key 'minimal_diagnoses') for the provided data in JSON FORMAT!!!
# [NO PROSE]
# [OUTPUT ONLY JSON]
# '
