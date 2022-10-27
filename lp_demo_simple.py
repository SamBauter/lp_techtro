from pulp import *

prob = LpProblem("SimpleBlending", LpMinimize)
x = LpVariable("Feed1Quantity",0,None)
y = LpVariable("Feed2Quantity",0, None,)

prob += 10*x + 4*y, "Total Cost of Mixed Feeds"

prob += 3 * x + 2 * y >= 60, "A-Requirement"
prob += 7 * x + 2*y >= 84, "B-Requirement"
prob += 3*x + 6*y >= 72, "C-Requirement"

prob.writeLP("simple_mixing.lp")

prob.solve()

print("Status:", LpStatus[prob.status])

for v in prob.variables():
    print(v.name, "=", v.varValue)

print("Total Cost of the blended feeds = ", value(prob.objective))



