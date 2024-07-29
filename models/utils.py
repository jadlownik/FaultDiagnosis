def AND(*args):
    return int(all(args))


def OR(*args):
    return int(any(args))


def NOT(a):
    return int(not a)


def XOR(*args):
    return int(sum(args) % 2)


def NOR(*args):
    return int(not any(args))


def NAND(*args):
    return int(not all(args))


def XNOR(*args):
    return int(sum(args) % 2 == 0)


external_functions = {
    'AND': 'AND',
    'OR': 'OR',
    'NOT': 'NOT',
    'XOR': 'XOR',
    'NOR': 'NOR',
    'NAND': 'NAND',
    'XNOR': 'XNOR'}
