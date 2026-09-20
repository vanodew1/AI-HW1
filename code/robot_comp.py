# Question 1b and 1c
import os
import search
from robotNavigation import RobotProblem, MOVES


example = """
S . . # . . .
# # . # . # .
. . . . . # .
. # # # . . .
. . . . . # G
"""

openGrid = """
S . . . . . .
. . . . . . .
. . . . . . .
. . . . . . .
. . . . . . G
"""

comb = """
S . # . . . # . . .
. . # . # . # . # .
. . # . # . # . # .
. . . . # . . . # G
"""

configurations = [
    ("Problem 1 eg", example, None, None),
    ("Problem 1 w.o bounds", openGrid, None, None),
    ("Comb", comb, None, None),
    ("Problem 1 eg reversed", example, (4, 6), (0, 0)),   
]

def makeRows(gridText):
    rows = []
    for line in gridText.splitlines():
        row = line.replace(" ", "")
        if row != "":
            rows.append(row)
    return rows


def pathCells(problem, actions):
    current = problem.getStartState()
    cells = [current]
    for action in actions:
        for name, dr, dc in MOVES:
            if name == action:
                current = (current[0] + dr, current[1] + dc)
        cells.append(current)
    return cells


def main():
    lines = []   
    def show(text):
        print(text)
        lines.append(text)

    show("## Robot Navigation with Obstacles: A* vs Dijkstra")
    show("")
    show("Cost = number of moves, Heuristic = Manhattan distance.")
    show("")
    show("| Configuration | Optimal cost | Route | A* nodes | Dijkstra nodes |")
    show("|---|---|---|---|---|")
    for name, gridText, start, goal in configurations:
        problem = RobotProblem(makeRows(gridText), start, goal)
        aActions, aCost, aNodes = search.aStarSearch(problem)
        dActions, dCost, dNodes = search.dijkstraSearch(problem)
        cells = pathCells(problem, aActions)
        route = " > ".join("(" + str(r) + "," + str(c) + ")" for r, c in cells)
        show(f"| {name} | {aCost} | {route} | {aNodes} | {dNodes} |")
        if aCost != dCost:
            show("WARNING: the two costs are different for " + name)

    resultsFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), "robot_results.md")
    with open(resultsFile, "w") as file:
        file.write("\n".join(lines) + "\n")
    print("\nsaved to", resultsFile)


if __name__ == "__main__":
    main()