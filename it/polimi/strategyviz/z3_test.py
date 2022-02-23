from z3 import Or, Solver, And, Then, Repeat, Tactic, OrElse, Optimize, simplify, Not, Real, help_simplify

s = Solver()
x = Real('x')
c = And(x >= 0, x <= 20, x <= 50, x >= 10)
s.add(c)

split_solve = Repeat(Then(OrElse(Tactic('split-clause'), Tactic('nnf')),
                          Tactic('propagate-ineqs'),
                          Tactic('ctx-solver-simplify')))

c = Or(x == 0, x == 1, x == 2)
c2 = And(Or(x == 0, x == 1, x == 2), Not(And(x > 0, x < 1)), Not(And(x > 1, x < 2)))
c3 = Or(And(x >= 0, x <= 0), And(x >= 1, x <= 1), And(x >= 2, x <= 2))
c4 = Or(And(x >= 0, x < 1), And(x >= 1, x < 2), And(x >= 2, x < 3))

help_simplify()

print(simplify(c2, eq2ineq=True))
