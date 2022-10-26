from pulp import *
# Within any of the 4 individual 2x2 boxes, each of the numbers 1 to 4 must be found.
#
# Within any column of the 4x4 grid, each of the numbers 1 to 4 must be found.
#
# Within any row of the 4x4 grid, each of the numbers 1 to 4 must be found.

VALS = ROWS = COLS = range(1, 5)
BOX_NUMS = range(0,4)
#prob = LpProblem("Small_Sudoku_Problem")
prob = LpProblem("Small_Sudoku_Problem", LpMinimize)


# STRUCTURE IS (VALUE, ROW, COLUMN)
choices = LpVariable.dicts("Choice", (VALS, ROWS, COLS), cat="Binary")
duplicate_in_row = LpVariable.dicts("DUP_ROW",(VALS, ROWS), cat="Binary")
duplicate_in_col = LpVariable.dicts("DUP_COL",(VALS, COLS), cat="Binary")
duplicate_in_box = LpVariable.dicts("DUP_BOX",(VALS, BOX_NUMS), cat="Binary")
skip_choice = LpVariable.dicts("SkipCHoice", (VALS, ROWS, COLS), cat="Binary")

Boxes = [
    [(2 * i + k + 1, 2 * j + l + 1) for k in range(2) for l in range(2)]
    for i in range(2)
    for j in range(2)
]

#Objective minimize the number of the slack variables that get set to 1
prob+=lpSum(duplicate_in_row[v][r] for r in ROWS for v in VALS) + \
      lpSum(duplicate_in_col[v][c] for c in COLS for v in VALS) + \
      lpSum(duplicate_in_box[v][b] for b in BOX_NUMS for v in VALS), "ObjectiveMinimizePenalty"

#Only one val can be created for each square
for r in ROWS:
    for c in COLS:
        prob += lpSum([choices[v][r][c] for v in VALS]) == 1, f"Single Value per each square constraint row:{r} col:{c}"

for v in VALS:
    for r in ROWS:
        #Each value should occur only once in a row
        try:
            prob += lpSum([choices[v][r][c] + skip_choice[v][r][c] for c in COLS]) == 1 + duplicate_in_row[v][r], f"Value in Row Constraint value:{v} row:{r}"
        except KeyError:
            x = 'dog'
    for c in COLS:
        prob += lpSum([choices[v][r][c] + skip_choice[v][r][c] for r in ROWS]) == 1 + duplicate_in_col[v][c], f"Value in Col Constraint value:{v} col:{c}"

    for idx,b in enumerate(Boxes):
        prob += lpSum([choices[v][r][c] + skip_choice[v][r][c] for (r, c) in b]) == 1 + duplicate_in_box[v][idx], f"Value in Box Constraint value:{v} box:{b}"

print(Boxes)

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

prob.writeLP("test")
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

