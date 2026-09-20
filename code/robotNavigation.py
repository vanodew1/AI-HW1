import util
from search import SearchProblem

MOVES = [("Up", -1, 0), ("Down", 1, 0), ("Left", 0, -1), ("Right", 0, 1)]

def readGrid(filename): # reads the grid from a text file
    rows = []
    with open(filename) as file:
        for line in file.read().splitlines():
            row = line.replace(" ", "")
            if row != "":
                rows.append(row)
    return rows

def findCell(grid, marker): #returns the (row,col) of S or G
    for r in range(len(grid)):
        for c in range(len(grid[r])):
            if grid[r][c] == marker:
                return (r,c)
    raise ValueError("no" + marker + "in the grid")

class RobotProblem(SearchProblem):
    def __init__(self, grid, start=None, goal=None):
        if len(set(len(row) for row in grid)) != 1:
            raise ValueError("the grid rows are not all the same length")
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.start = start if start is not None else findCell(grid, "S")
        self.goal = goal if goal is not None else findCell(grid, "G")
        for cell in(self.start, self.goal):
            if not self.isFree(cell):
                raise ValueError("start or goal is an obstacle or is not on the grid")

    def isFree(self, cell): #inside the grid and not an obstacle
        r, c = cell
        if r < 0 or r>= self.rows or c < 0 or c >= self.cols:
            return False
        return self.grid[r][c] != "#"

    def getStartState(self):
        return self.start

    def isGoalState(self, state):
        return state == self.goal

    def getSuccessors(self, state): #returns a list of (successor, action, stepCost)
        successors = []
        r,c = state
        for action, dr, dc in MOVES:
            neighbour = (r + dr, c + dc)
            if self.isFree(neighbour):
                successors.append((neighbour, action, 1))
        return successors

    def getCostOfActions(self, actions): #every move costs 1, so the cost is the path length
        current = self.start
        total = 0
        for action in actions:
            for name, dr, dc in MOVES:
                if name == action:
                    current = (current[0] + dr, current[1] + dc)
                    break
            else:
                raise ValueError("unknown action: " + action)
            if not self.isFree(current):
                raise ValueError("illegal move into " + str(current))
            total += 1
        return total

    def getHeuristic(self, state):
        return util.manhattanDistance(state, self.goal)

def showPath(problem, actions): #draws the route on the grid with *
        grid = [list(row) for row in problem.grid]
        current = problem.getStartState()
        for action in actions:
            for name, dr, dc, in MOVES:
                if name == action:
                    current = (current[0] + dr, current[1] + dc)
                    break
            if current != problem.goal:
                grid[current[0]][current[1]] = "*"
        grid[problem.start[0]][problem.start[1]] = "S"
        grid[problem.goal[0]][problem.goal[1]] = "G"
        return "\n".join(" ".join(row) for row in grid)