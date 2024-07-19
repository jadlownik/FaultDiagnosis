def AND(a, b):
    return int(a & b)


def OR(a, b):
    return int(a | b)


def NOT(a):
    return int(1 - a)


def XOR(a, b):
    return int(a + b - 2 * a * b)


def NOR(a, b):
    return int(1 - (OR(a, b)))


def NAND(a, b):
    return int(1 - (AND(a, b)))


def XNOR(a, b):
    return int(1 - (XOR(a, b)))


external_functions = {
    'AND': 'AND',
    'OR': 'OR',
    'NOT': 'NOT',
    'XOR': 'XOR',
    'NOR': 'NOR',
    'NAND': 'NAND',
    'XNOR': 'XNOR'
    }
