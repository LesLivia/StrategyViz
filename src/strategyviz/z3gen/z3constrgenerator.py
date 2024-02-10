from typing import List, Set
from z3 import Int, And, Or, Tactic

OPERATORS = ['==', '<=', '>=', '<', '>']


def get_atoms(guard: str):
    # splits formula into atomic propositions
    atoms: List[str] = guard.replace('(', '').replace(')', '') \
        .replace('&&', '&').replace('||', '&').replace('\n', '').split('&')
    return atoms


def get_variables(atoms: List[str]):
    # isolates variables identifiers from atomic propositions
    variables: Set[str] = set()
    for a in atoms:
        if all([not a.__contains__(o) for o in OPERATORS]):
            variables.add(a)
        else:
            o = [o for o in OPERATORS if a.__contains__(o)][0]
            new_var = a.split(o)[0]
            variables.add(new_var)
    return variables


def atom2z3constr(atom: str, z3vars):
    o = [o for o in OPERATORS if atom.__contains__(o)][0]
    elems = atom.split(o)
    z3var = [v for v in z3vars if str(v) == elems[0]][0]
    if o == '==':
        return z3var == int(elems[1])
    elif o == '<=':
        return z3var <= int(elems[1])
    elif o == '>=':
        return z3var >= int(elems[1])
    elif o == '<':
        return z3var < int(elems[1])
    elif o == '>':
        return z3var > int(elems[1])


def guard2constr(guard: str):
    atoms = get_atoms(guard)
    variables = get_variables(atoms)
    z3_variables = [Int(v) for v in variables]
    z3_atomic_constraints = And([atom2z3constr(a, z3_variables) for a in atoms])

    return z3_atomic_constraints


def constraint2str(constraint):
    res = str(constraint[0][0]) + '&&('
    single_c = str(constraint[0][1]).split('And')[1:]
    single_c_str = [c.replace('(', '').replace('),\n', '').replace(' ', '').split(',') for c in single_c]
    res += '||'.join(['(' + '&&'.join(f) + ')' for f in single_c_str])
    res += ')'
    return res


def guards2singleconstr(guards: List[str]):
    single_constr = [guard2constr(g) for g in guards]
    mega_or = Or(single_constr)
    return constraint2str(Tactic('solve-eqs')(mega_or))
