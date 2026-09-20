from search import SearchProblem

roadmath = {"M": 1.0, "S": 1.25, "N": 3.0}
def readTable(filename, isNumbers): # reads the csv file
    table = {}
    names = []
    with open(filename) as file:
        lines = file.read().splitlines()
    for name in lines[0].split(",")[1:]:
        names.append(name.strip())
    for line in lines[1:]:
        if line == "":
            continue
        parts = line.split(",")
        rowName = parts[0].strip()
        table[rowName] = {}
        for i in range(len(names)):
            value = parts[i + 1].strip()
            if isNumbers:
                value = float(value)
            table[rowName][names[i]] = value
    return names, table

class RoadMap: # has all the road network info and their costs  
    def __init__(self, connectionsFile, aerialFile, roadTypeFile,
                 multipliers=roadmath):
        areas, kmTable = readTable(connectionsFile, True)
        aerialAreas, aerialTable = readTable(aerialFile, True)
        typeAreas, typeTable = readTable(roadTypeFile, False)
        self.roads = {}
        if areas != aerialAreas or areas != typeAreas:
            raise ValueError("the three csv files have different areas")
        self.areas = areas
        self.aerial = aerialTable 
        for a in areas:
            self.roads[a] = []
            for b in areas:
                km = kmTable[a][b]
                if a == b or km == -1:   # -1 = no road
                    continue
                roadType = typeTable[a][b]
                cost = km * multipliers[roadType]
                self.roads[a].append((b, km, roadType, cost))

    def getRoadCost(self, a, b): # cost from a to b
        for neighbour, km, roadType, cost in self.roads[a]:
            if neighbour == b:
                return cost
        raise ValueError("no direct road from " + a + " to " + b) # if error 

    def getRoadInfo(self, a, b): # returns (km, roadType) for the road from a to b
        for neighbour, km, roadType, cost in self.roads[a]:
            if neighbour == b:
                return km, roadType
        raise ValueError("no direct road from " + a + " to " + b)


class CourierProblem(SearchProblem):
    def __init__(self, roadMap, start, goal):
        if start not in roadMap.roads:
            raise ValueError("unknown start area: " + start)
        if goal not in roadMap.roads:
            raise ValueError("unknown goal area: " + goal)
        self.map = roadMap
        self.start = start
        self.goal = goal

    def getStartState(self):
        return self.start

    def isGoalState(self, state):
        return state == self.goal

    def getSuccessors(self, state): # returns a list of (successor, action, stepCost) triples
        successors = []
        for neighbour, km, roadType, cost in self.map.roads[state]:
            successors.append((neighbour, neighbour, cost))
        return successors

    def getCostOfActions(self, actions): # returns the total cost of a particular sequence of actions
        current = self.start
        total = 0
        for nextArea in actions:
            total += self.map.getRoadCost(current, nextArea)
            current = nextArea
        return total

    def getHeuristic(self, state): #returns the heuristic value of current state
        return self.map.aerial[state][self.goal]

    def makeLegProblem(self, start, goal): # same map with a new start and goal, used for the stopover route
        return CourierProblem(self.map, start, goal)