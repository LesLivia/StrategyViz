from z3 import Or, And, Then, Repeat, Tactic, OrElse, Real, Goal, simplify, Optimize, Int, Solver, describe_tactics

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

y = Int('y')
z = Int('z')
mega_or = Or(And(x == 2, y == 0, z == 10), And(x == 3, y == 0, z == 10), And(x == 4, y == 0, z == 10),
             And(x == 5, y == 0, z == 10), And(x == 6, y == 0, z == 10), And(x == 7, y == 0, z == 10))
s = Solver()
s.add(mega_or)
g = Goal()
g.add(mega_or)
print(simplify(mega_or))

mega_or = Or(And(y == 0, z == 10, Or(x == 2, x == 3, x == 4, x == 5)))
s.reset()
s.add(mega_or)
print(split_solve(mega_or).as_expr())

describe_tactics()