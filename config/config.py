PATH_EXAMPLES = 'examples\\'
PRINT_TO_CONSOLE = True
TITLE = 'title'
ALL_VARIABLES = 'x'
FAULTS = 'f'
KNOWN_VARIABLES = 'z'
EQUATIONS = 'r'
OBSERVATIONS = 'o'
PREFIX_FAULT = 'f_'
PREFIX_SIGNAL = 'u_'
RELATIONS = 'rels'
OPENAI_API_MODEL = 'gpt-4o-mini'
JSON_KEY_MSO= 'mso'
JSON_KEY_CONFLICTS = 'minimal_conflicts'
JSON_KEY_DIAGNOSES = 'minimal_diagnoses'
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
GPT_INSTRUCTION_PART_1 = '''
Imagine you are an engineer specialized in fault diagnosis. The final result should be in JSON format and should consist of 'mso'.
Use 'equations,' a list of tuples in the format (symbol, equation, list of unknowns in the equation), to build
the system. Analyze all possible combinations of symbols and choose those which meet the following conditions:
1. The set of equations must have exactly one structural redundancy. Structural redundancy is defined as the number 
of equations minus the number of unknown variables that are present in these equations. 
2. All proper subsets of this set must not be PSO. This means that the structural redundancy of each subset must be 0 or less.
Check the number of unknowns at the end as they may be repeated
The result is the list of lists with symbols of equations.
[USE CODE INTERPRETER]
<example>
<input>
equations = [
('M1', 'a * c - x01', ['x01']),
('M2', 'b * d - x02', ['x02']),
('M3', 'c * e - x03', ['x03']),
('A2', 'x01 + x02 - f', ['x01', 'x02']),
('A1', 'x02 + x03 - g', ['x02', 'x03'])
]
</input>
<output>
{
"mso" = [['M1', 'M2', 'A1'], ['M2', 'M3', 'A2'], ['M1', 'M3', 'A1', 'A2']]
}
</output>
</example>
'''

GPT_INSTRUCTION_PART_2 = '''
Imagine you are an engineer specialized in fault diagnosis.
Create a class with the following components:
Initialize the class with three parameters:
    A list of lists containing equation names (call it 'mso')
    A dictionary where keys are equation names and values are equation strings (call it 'equations')
    A dictionary of observed data (call it 'data')
    Store these as instance variables with the same names.
    Create an additional instance variable called 'parsed_equations' by calling a method that defines and parses the equations.
Implement a private method that defines and parses equations:
    Initialize an empty dictionary called 'parsed'
    Iterate through each item in the 'equations' dictionary
    For each equation:
        Split the equation string by '=' into 'left_side' and 'right_side'
        Strip whitespace from both sides
        Create a 'symbols_dict' using dictionary comprehensions:
            For the left side: {var: symbols(var) for var in left_side.split() if var.isidentifier()}
            Update it with right side: {var: symbols(var) for var in right_side.split() if var.isidentifier()}
        Replace observed data in the symbols_dict:
            For each item in 'data', if the key is in symbols_dict, replace the value
        Build the equation based on the operator:
            Check for '&', '|', '^', '~^', '~', '~&', '~|' in the left_side
                For your information what means these symbols :
                    NAND ('~&')
                    NOR ('~|')
                    XNOR ('~^')
                    XOR ('^')
                    NOT ('~')
                    AND ('&')
                    OR ('|')
            For each case, create a parsed_expression using SymPy functions (Not, And, Or, Xor)
            Use list comprehensions to get the relevant symbols from symbols_dict
            Convert to equality using Eq(parsed_expression, symbols_dict[right_side])
        For arithmetic:
            If '+' in left_side: split by '+', use sum() with a generator expression
            If '' in left_side: split by '', use a loop to multiply terms
            Otherwise, assume it's a single term
            Create an Eq object with left_expr and right_expr
        Add the parsed expression to the 'parsed' dictionary
    Return the 'parsed' dictionary
Implement a private method to check if a set of equations is contradictory:
    Check if equations are logical or arithmetic:
        Use: any(char in equation for equation in self.equations.values() for char in ['~', '&', '|', '^'])
    For logical equations:
        Get all variables: {var for eq in equations.values() for var in eq.free_symbols}
        Generate all True/False combinations: product([True, False], repeat=len(variables))
        For each combination:
            Create an assignment dictionary using dict(zip(variables, combination))
            Check if all equations are satisfied using all() and a generator expression
            If any combination satisfies all equations, return False
        If no satisfying combination is found, return True
    For arithmetic equations:
        Convert equations.values() to a list
        Use SymPy's solve function: solve(eqs, dict=True)
        Return True if the solution list is empty, False otherwise
Implement a public method to get minimal conflicts:
    Initialize an empty list called 'minimal_conflicts'
    Iterate through each group in self.mso
    For each group:
        Create a dictionary 'group_equations' using a dictionary comprehension:
        {name: self.parsed_equations[name] for name in group if name in self.parsed_equations}
        Check if the group is contradictory using the method from step 3
        If contradictory, append the sorted group to 'minimal_conflicts'
Return 'minimal_conflicts' sorted using: sorted(minimal_conflicts, key=lambda x: (len(x), x))

HINTS:
1. To check whether the equation is logical, check the presence of at least one character from the list ['|', '&', '^', '~'] in at least one provided equations.values().
2. Be sure that all logical opearation (AND (&), OR (|), XOR (^), NOT (~), NAND (~&), NOR (~|), XNOR (~^)) and arithmetic (+, *) are supported.
3. Use example_1, example_2 and example_3 to test your code before generate results for given data.

<example_1>
<input>
equations = {
    'M1': 'a * c = x01', 
    'M2': 'b * d = x02', 
    'M3': 'c * e = x03', 
    'A1': 'x01 + x02 = f', 
    'A2': 'x02 + x03 = g'}
mso = [['M1', 'M2', 'A1'], ['M2', 'M3', 'A2'], ['M1', 'M3', 'A1', 'A2']]
data = {'a': 2, 'b': 2, 'c': 3, 'd': 3, 'e': 2, 'f': 10, 'g': 12}
</input>
For ['M1', 'M2', 'A1'] system of equations is:
[a * c = x01,
b * d = x02,
x01 + x02 = f
]
For ['M2', 'M3', 'A2'] system of equations is:
[b * d = x02,
c * e = x03,
x02 + x03 = g
]
For ['M1', 'M3', 'A1', 'A2'] system of equations is:
[a * c = x01,
c * e = x03,
x01 + x02 = f,
x02 + x03 = g
]
For ['M1', 'M2', 'A1'] and ['M1', 'M3', 'A1', 'A2'] systems of eqautions are inconsistent so output should be:
<output>
{
'minimal_conflicts': [['M1', 'M2', 'A1'], ['M1', 'M3', 'A1', 'A2']]
}
</output>
</example_1>
<example_2>
<input>
mso = [['A1', 'O1', 'O2'], ['A2', 'O2', 'O3'], ['A1', 'A2', 'O1', 'O3']]
equations = {
    'O1': 'a | c = x01',
    'O2': 'b | d = x02',
    'O3': 'c | e = x03',
    'A1': 'x01 & x02 = f',
    'A2': 'x02 & x03 = g'}
data = {'a': True, 'b': True, 'c': True, 'd': True, 'e': True, 'f': False, 'g': False}
</input>
For ['A1', 'O1', 'O2'] system of equations is:
[x01 & x02 = f,
a | c = x01,
b | d = x02
]
For ['A2', 'O2', 'O3'] system of equations is:
[x02 & x03 = g,
b | d = x02,
c | e = x03
]
For ['A1', 'A2', 'O1', 'O3'] system of equations is:
[x01 & x02 = f,
x02 & x03 = g,
a | c = x01,
c | e = x03
]
For ['A1', 'O1', 'O2'] and ['A2', 'O2', 'O3'] systems of eqautions are inconsistent so output should be:
<output>
{
'minimal_conflicts': [['A1', 'O1', 'O2'], ['A2', 'O2', 'O3']]
}
</example_2>
<example_3>
<input>
mso = [['NA1', 'NO2', 'NX1']]
equations = {
    'NA1': 'a ~& b = x01', 
    'NO2': 'c ~| d = x02', 
    'NX1': 'x01 ~^ x02 = e'}
data = {'a': True, 'b': True, 'c': True, 'd': True, 'e': False}
</input>
For ['NA1', 'NO2', 'NX1'] system of equations is:
[a ~& b = x01,
c ~| d = x02,
x01 ~^ x02 = e
]
For ['NA1', 'NO2', 'NX1'] system of eqautions are inconsistent so output should be:
<output>
{
'minimal_conflicts': [['NA1', 'NO2', 'NX1']]
}
</example_3>
'''

GPT_INSTRUCTION_PART_3 = '''
Imagine you are an engineer specialized in fault diagnosis.
Use the 'minimal_conflicts' which contains lists of equation symbols
The final result should be in JSON format and should consist of 'minimal_diagnoses'.
Use the algorithm below to generate minimal diagnoses.
Translate the algorithm steps into Python functions:
- Convert the high-level pseudocode into Python functions, maintaining the same logic and operations.
- Implement the main loop of the algorithm, handling conflicts and candidates (diagnoses) generation.
- Implement the logic to update the candidates (diagnoses) collection and ensure duplicates and non-minimal elements are removed.
In <output></output> you have example format of output for this part.
[USE CODE INTERPRETER]
<algorithm>
Algorithm 1: Conflicts guide candidates generation.
Inputs: MinimalConflicts
CandidatesCollection←{∅}
for each Conflict ∈ MinimalConflicts do
CurrentCandidates←CandidatesCollection
for each Candidate ∈ CurrentCandidates do
if Candidate ∩ Conflict = ∅ then
CandidatesCollection←UpdateCandidates(Candidate, CandidatesCollection, Conflict)
Return CandidatesCollection

Algorithm 2: UpdateCandidates.
Inputs: Candidate, CandidatesCollection, Conflict
CandidatesCollection←CandidatesCollection - Candidate
for each Component ∈ Conflict do
NewCandidate←Candidate ∪ { Component }
CandidatesCollection←CandidatesCollection ∪ NewCandidate
Remove duplicates and non-minimal elements from CandidatesCollection
Return CandidatesCollection

</algorithm>
<output>
{
"minimal_diagnoses": [['A1'], ['M1'], ['A2', 'M2'], ['M2', 'M3']]
}
</output>
'''

GPT_INSTRUCTION = '''
Imagine you are an engineer specialized in fault diagnosis. Your task is divided into three parts.
You have to complete the first part before the second part, and the second part before the third part.
Use the result from the first part to get the result for the second part and use the second part results to get
the final result. The final result should be in JSON format and should consist of 'mso' from the first part and
'minimal_conflicts' from the second part and 'minimal_diagnoses' from the third part. You can use the code 
interpreter but in the answer, I want only JSON with two keys 'minimal_conflicts' and 'minimal_diagnoses'.
<part1>
Use 'equations,' a list of tuples in the format (symbol, equation, list of unknowns in the equation), to build
the system. Analyze all possible combinations of symbols and choose those which meet the following conditions:
1. The set of equations must have exactly one structural redundancy. Structural redundancy is defined as the number 
of equations minus the number of unknown variables that are present in these equations. 
2. All proper subsets of this set must not be PSO. This means that the structural redundancy of each subset must be 0 or less.
Check the number of unknowns at the end as they may be repeated
The result is the list of lists with symbols of equations.
[USE CODE INTERPRETER]
<example>
<input>
equations = [
('M1', 'a * c = x01', ['x01']),
('M2', 'b * d = x02', ['x02']),
('M3', 'c * e = x03', ['x03']),
('A2', 'x01 + x02 = f', ['x01', 'x02']),
('A1', 'x02 + x03 = g', ['x02', 'x03'])
]
</input>
<output>
{
"mso" = [['M1', 'M2', 'A1'], ['M2', 'M3', 'A2'], ['M1', 'M3', 'A1', 'A2']]
}
</output>
</example>
</part1>
<part2>
To implement the function for finding minimal conflicts, follow these instructions:
First, initialize an empty list called minimal_conflicts to store the groups of equations that represent
minimal conflicts. Then, iterate through each group in mso. For each group, create a list of equations 
called eq_list, where you substitute the values from observations into the corresponding variables in the 
equations. If the equations are logical, check for contradictions by evaluating all possible assignments 
of True and False to the variables. If a group of equations is found to be contradictory, add the sorted 
group to the minimal_conflicts list. If the equations are algebraic, solve the system of equations and 
check if there is no solution or if the equations are contradictory. If a group of equations is found to 
be contradictory, add the sorted group to the minimal_conflicts list.

After processing all the groups, sort the minimal_conflicts list first by the number of equations in each 
group and then alphabetically. Finally, return the sorted list of minimal_conflicts.

To process the equations, start by creating a dictionary called symbols_dict that maps variable names and 
observations to symbols. For each equation, split it into the left and right sides around the equality sign. 
Handle logical operators such as NAND, NOR, and negated XOR. If a logical operator appears on the left side, 
split the left side around this operator and apply the corresponding logical function. Create an equation 
representing the equality of the left side (with the applied logical function) to the right side. If no 
logical operator is present, use eval to evaluate the expressions on both sides of the equation. Return the 
resulting equation object.

To check for contradictions, gather all unique variables from the equations. Generate all possible assignments 
of True and False to these variables. Check if for any assignment, all the equations are satisfied. If not, 
indicate that the equations are contradictory. Otherwise, indicate that the equations are not contradictory.

Use the sympy library for symbolic algebraic operations and the itertools library for generating combinations 
of True and False values. Below you have a corectlly solved example, you can use it to write and test your code.
<example>
<input>
equations = [('M1', 'a * c = x01', ['x01']), 
('M2', 'b * d = x02', ['x02']), 
('M3', 'c * e = x03', ['x03']), 
('A1', 'x01 + x02 = f', ['x01', 'x02']), 
('A2', 'x02 + x03 = g', ['x02', 'x03'])],  
mso = [['M1', 'M2', 'A1'], ['M2', 'M3', 'A2'], ['M1', 'M3', 'A1', 'A2']], 
data = {'a': 2, 'b': 2, 'c': 3, 'd': 3, 'e': 2, 'f': 10, 'g': 12}
</input>
For ['M1', 'M2', 'A1'] system of equations is:
[a * c = x01,
b * d = x02,
x01 + x02 = f
]
For ['M2', 'M3', 'A2'] system of equations is:
[b * d = x02,
c * e = x03,
x02 + x03 = g
]
For ['M1', 'M3', 'A1', 'A2'] system of equations is:
[a * c = x01,
c * e = x03,
x01 + x02 = f,
x02 + x03 = g
]

For ['M1', 'M2', 'A1'] and ['M1', 'M3', 'A1', 'A2'] systems of eqautions are inconsistent so output should be:
<output>
{
'minimal_conflicts': [['M1', 'M2', 'A1'], ['M1', 'M3', 'A1', 'A2']]
}
</output>
</example>
</part2>
<part3>
Use 'minimal_conflicts' from the second part. Use the algorithm below to generate minimal diagnoses.
Translate the algorithm steps into Python functions:
- Convert the high-level pseudocode into Python functions, maintaining the same logic and operations.
- Implement the main loop of the algorithm, handling conflicts and candidates (diagnoses) generation.
- Implement the logic to update the candidates (diagnoses) collection and ensure duplicates and non-minimal elements are removed.
In <output></output> you have example format of output for this part.
[USE CODE INTERPRETER]
<algorithm>
Algorithm 1: Conflicts guide candidates generation.
Inputs: MinimalConflicts
CandidatesCollection←{∅}
for each Conflict ∈ MinimalConflicts do
CurrentCandidates←CandidatesCollection
for each Candidate ∈ CurrentCandidates do
if Candidate ∩ Conflict = ∅ then
CandidatesCollection←UpdateCandidates(Candidate, CandidatesCollection, Conflict)
Return CandidatesCollection

Algorithm 2: UpdateCandidates.
Inputs: Candidate, CandidatesCollection, Conflict
CandidatesCollection←CandidatesCollection - Candidate
for each Component ∈ Conflict do
NewCandidate←Candidate ∪ { Component }
CandidatesCollection←CandidatesCollection ∪ NewCandidate
Remove duplicates and non-minimal elements from CandidatesCollection
Return CandidatesCollection

</algorithm>
<output>
{
"minimal_diagnoses": [['A1'], ['M1'], ['A2', 'M2'], ['M2', 'M3']]
}
</output>
</part3>
'''



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

GPT_INSTRUCTIONS = '''
Imagine your are an engineer specialized in fault diagnosis. Your task is divided to three part.
You have to realize first part before second part, and second part before third part. 
Use result from first part to get result for second part and use second part 
results to get final result. Final result should be in JSON format and should consist 
'minimal_conflicts' from second part and 'minimal_diagnoses' from third part. 
You can use code interpreter but in the answer i want only JSON with 
two keys 'minimal_conflicts' and 'minimal_diagnoses'. 
<part1>
Use 'equations_part1' as 'equations'. 
'equations' the equations building the system in format 
(numer of equation, equation, unkonwns in equation). 
Generate MSO using algorithm below. 
<algorithm> 
Algorithm: FindMSO 
Input: 
    A set of equations M, which is a Proper Structurally Overdetermined (PSO) set. 
Output: 
    The set of all MSO (Maximally Structurally Overdetermined) sets contained in M. 
Steps: 
1. Initialize the Output Set: 
    Create an empty set MMSO to store the found MSO sets. 
2. Base Case - Check Structural Redundancy: 
    If the structural redundancy φ(M) = 1, then M is an MSO set. Add M to MMSO. Return MMSO. 
3. Recursive Case - Reduce the Model: 
    If φ(M) > 1: 
        For each equation e in M: 
            Remove e from M to form M' = M - {e}. 
            Compute the overdetermined part of M', denoted as (M')+. 
            Recursively call the algorithm with (M')+: FindMSO((M')+). 
            Union the result with MMSO. 

4. Return the Result:
    Return MMSO, which now contains all the MSO sets found.

Structural Redundancy - The difference between the number of equations and the number of unknowns in the set.
Overdetermined Part - The subset of equations in M that remains overdetermined when an equation is removed.
Variables Connected to Equations - The set of variables present in the set of equations M
</algorithm> 
As the result give me the list of lists with numbers of eqautions. 
Plaese use code interperter aand code belowe to give me right answer. 
Remember THE SUM OF UNKONOWNS VARIABLES MUST BE ONE LESS THEN THE NUMBER OF EQUATIONS! 
<example>
<input>
equations = [
('A1', 'a + b = x02', ['x02']), 
('M1', 'c * d = x01', ['x01']), 
('M2', 'e * x01 = x03', ['x01', 'x03']), 
('A2', 'x02 + x03 = x04', ['x02', 'x03', 'x04']), 
('M3', 'f * x04 = h', ['x04']), 
('M4', 'x04 * g = i', ['x04'])
]
</input>
For equations number [0, 1, 3] we have: 
unknowns: x01, x02. 
number of equations: 3, 
number of unknowns: 2, 
number of occurrences of x01: 2, 
number of occurrences of x02: 2. 
<output>
{
"mso" = [[0, 1, 3]]
}
</output>
</example>
</part1>
<part2>
Use 'equations_part2' as 'equations'. 
Use 'mso' from first part. 
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
[DO NOT USE CODE INTERPRETER] 
[MAKE CALCULATION MANUALLY] 
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
</part2>
<part3>
Use 'minimal_conflicts from second part. 
Use algorithm below to generate minimal diagnoses. 
Translate the algorithm steps into Python functions: 
- Convert the high-level pseudocode into Python functions, 
  maintaining the same logic and operations. 
- Implement the main logic in a method: Implement 
  the main loop of the algorithm, handling conflicts 
  and candidates (diagnoses) generation. 
- Handle updates and filtering: Implement the logic to 
  update the candidates (diagnoses) collection and ensure 
  duplicates and non-minimal elements are removed. 
[USE CODE INTERPRETER] 
<algorithm>
Algorithm 1: Conflicts guide candidates generation. 
    Inputs: MinimalConflicts 
    CandidatesCollection←{∅} 
    for each Conflict ∈ MinimalConflics do 
        CurrentCandidates←CandidatesCollection 
    for each Candidate ∈ CurrentCandidates do 
        if Candidate ∩ Conflict = ∅ then 
            CandidatesCollection←UpdateCandidates(Candidate, CandidatesCollection, Conflict) 
    Return CandidatesCollection 
Algorithm 2: UpdateCandidates. 
    Inputs: Candidate, CandidatesCollection, Conflict 
    CandidatesCollection←CandidatesCollection - Candidate 
    for each Component ∈ Conflict do 
        NewCandidate←Candidate ∪ { Component } 
        CandidatesCollection←CandidatesCollection ∪ NewCandidate 
    Remove duplicates and non-minimal elements from CandidatesCollection 
    Return CandidatesCollection 
</algorithm>
<output>
{
"minimal_diagnoses": [['A1'],['M1'],['A2', 'M2'],['M2', 'M3']]
}
</output>
</part3>
'''


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
