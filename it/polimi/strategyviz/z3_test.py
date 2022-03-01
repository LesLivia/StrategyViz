from z3 import Or, And, Then, Repeat, Tactic, OrElse, Real, Goal, simplify, Optimize, help_simplify

x = Real('x')

split_solve = Repeat(Then(OrElse(Tactic('split-clause'), Tactic('nnf')),
                          Tactic('propagate-ineqs'),
                          Tactic('ctx-solver-simplify')))

c = And(x >= 0, x <= 20, x <= 50, x >= 10)
g = Goal()
g.add(c)
print(split_solve(g).as_expr())
for sg in split_solve(g):
    print(sg.as_expr())

c = Or(x == 0, x == 2)
g = Goal()
g.add(c)
print(split_solve(g).as_expr())
for sg in split_solve(g):
    print(sg.as_expr())

print(simplify(c, eq2ineq=True))

o = Optimize()
o.add(c)
min_x = o.minimize(x)
o.check()
print(o.upper(min_x))

c = Or(And(x >= 0.5, x <= 1.5), And(x >= 1.5, x <= 2.5), And(x >= 2.5, x <= 3.5))
g = Goal()
g.add(c)
print(split_solve(g).as_expr())
for sg in split_solve(g):
    print(sg.as_expr())
