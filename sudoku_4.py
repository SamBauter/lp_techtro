from pulp import *
# Within any of the 4 individual 2x2 boxes, each of the numbers 1 to 4 must be found.
#
# Within any column of the 4x4 grid, each of the numbers 1 to 4 must be found.
#
# Within any row of the 4x4 grid, each of the numbers 1 to 4 must be found.

VALS = ROWS = COLS = range(1, 5)
BOX_NUMS = range(0,4)
prob = LpProblem("Small_Sudoku_Problem")


# STRUCTURE IS (VALUE, ROW, COLUMN)
choices = LpVariable.dicts("Choice", (VALS, ROWS, COLS), cat="Binary")

Boxes = [
    [(2 * i + k + 1, 2 * j + l + 1) for k in range(2) for l in range(2)]
    for i in range(2)
    for j in range(2)
]

#NO OBJECTIVE FUNCTION NEEDED

#Only one val can be created for each square
for r in ROWS:
    for c in COLS:
        prob += lpSum([choices[v][r][c] for v in VALS]) == 1, f"Single Value per each square constraint row:{r} col:{c}"

for v in VALS:
    for r in ROWS:
        #HARD CONSTRAINT Comment out when running with soft constraint
        #Each value choice should occur only once in a row
        prob += lpSum([choices[v][r][c] for c in COLS]) == 1, f"Value in Row Constraint value:{v} row:{r}"

    for c in COLS:
        #HARD CONSTRAINT Comment out when running with soft constraint
        #Each value choice should only occur once in a column
        prob += lpSum([choices[v][r][c]for r in ROWS]) == 1, f"Value in Col Constraint value:{v} col:{c}"

    for idx,b in enumerate(Boxes):
        #HARD CONSTRAINT Comment out when running with soft constraint
        #Each value choice should only occur once in a box
        prob += lpSum([choices[v][r][c] for (r, c) in b]) == 1, f"Value in Box Constraint value:{v} box:{b}"


#print(Boxes)

# Structure is Value, Row, Column
input_data = [
    (1, 1, 1),
    (2, 1, 2),
    (3, 1, 3),
    (4, 1, 4),
    (3, 2, 1),
    (4, 3, 1),
]

#Setting constraints for the initial state
for (v, r, c) in input_data:
    prob += choices[v][r][c] == 1, f"Initial Values Constraint v: {v} r: {r} c: {c}"


#Show the initial State
sudokuout = open("sudokuout_init.txt", "w")

for r in ROWS:
    if r in [1, 3]:
        sudokuout.write("+-----+-----+\n")
    for c in COLS:
        if c ==1:
            sudokuout.write("|")
        if c == 3:
            sudokuout.write(" |")
        written = False
        for v in VALS:
                if (v,r,c) in input_data:
                    sudokuout.write(" "+str(v))
                    written = True
        if not written:
            sudokuout.write("  ")
        if c == 4:
            sudokuout.write(" |\n")

sudokuout.write("+-----+-----+")
sudokuout.close()

prob.writeLP("sudoku_4.lp")
prob.solve()

loop_count = 1
while True:
    if loop_count >=11:
        break
    filename = f"sudoku_solution_{loop_count}.txt"
    sudoku_solution_file = open(filename, "w")
    prob.solve()
    # The status of the solution is printed to the screen
    print("Status:", LpStatus[prob.status])
    # The solution is printed if it was deemed "optimal" i.e met the constraints
    if LpStatus[prob.status] == "Optimal":
        # The solution is written to the sudoku_solution_x.txt file
        for r in ROWS:
            if r in [1, 3]:
                sudoku_solution_file.write("+-----+-----+\n")
            for c in COLS:
                for v in VALS:
                    if value(choices[v][r][c]) == 1:
                        if c in [1, 3]:
                            sudoku_solution_file.write("| ")
                        sudoku_solution_file.write(str(v) + " ")
                        if c == 4:
                            sudoku_solution_file.write("|\n")
        sudoku_solution_file.write("+-----+-----+\n")
        sudoku_solution_file.close()

        # The constraint is added that the same solution cannot be returned again
        # The value of the sum of choices can have 15 of the same choices set but not 16(which would be a same solution)
        prob += (
                lpSum(
                    [
                        choices[v][r][c]
                        for v in VALS
                        for r in ROWS
                        for c in COLS
                        if value(choices[v][r][c]) == 1
                    ]
                )
                <= 15
        )
        loop_count+=1
    # If a new optimal solution cannot be found, we end the program
    else:
        sudoku_solution_file.write("No further Feasible Solutions")
        break

