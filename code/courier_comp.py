## Question 1(c)

import os
import search
from courierDelivery import RoadMap, CourierProblem
csvFolder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "csv")

trips = [
    ("Saddar (Hub)", "Clifton", "short trip on a main road"),
    ("Saddar (Hub)", "Lyari", "only reachable by a narrow lane"),
    ("Saddar (Hub)", "Baldia Town", "route avoids the narrow lanes"),
    ("Saddar (Hub)", "Korangi", "long trip across the city"),
    ("Clifton", "Korangi", "long trip, main road then standard"),
    ("II Chundrigar Road", "Malir", "long trip"),
    ("Liaquatabad", "FB Area", "detour to avoid a narrow lane"),
    ("Orangi Town", "Gulistan-e-Johar", "far apart"),
    ("PECHS", "DHA", "medium trip"),
    ("North Nazimabad", "Korangi", "far apart"),
]


def loadMap(multipliers=None):
    connections = os.path.join(csvFolder, "Connections.csv")
    aerial = os.path.join(csvFolder, "heuristics.csv")
    roadTypes = os.path.join(csvFolder, "TrackType.csv")
    if multipliers is None:
        return RoadMap(connections, aerial, roadTypes)
    return RoadMap(connections, aerial, roadTypes, multipliers)


def runBoth(roadMap, start, goal):
    problem = CourierProblem(roadMap, start, goal)
    aActions, aCost, aNodes = search.aStarSearch(problem)
    dActions, dCost, dNodes = search.dijkstraSearch(problem)
    return aActions, aCost, aNodes, dActions, dCost, dNodes


def main():
    lines = []   
    def show(text):
        print(text)
        lines.append(text)

    roadMap = loadMap()# table one starts here
    show("## Table 1: A* vs Dijkstra on 10 trips (cost = km * road type multiplier)")
    show("")
    show("| Trip | Optimal cost | Route | A* nodes | Dijkstra nodes | A* saves |") # used other tables for formating reference 
    show("|---|---|---|---|---|---|")
    for start, goal, why in trips:
        aActions, aCost, aNodes, dActions, dCost, dNodes = runBoth(roadMap, start, goal)
        route = " > ".join([start] + aActions)
        saved = round(100 * (dNodes - aNodes) / dNodes)
        show(f"| {start} to {goal} | {aCost:.2f} | {route} | {aNodes} | {dNodes} | {saved}% |")
        if abs(aCost - dCost) > 0.000001:
            show("WARNING: the two costs are different for " + start + " to " + goal)
        if aActions != dActions:
            show(f"(note: Dijkstra found a different route with the same cost for {start} to {goal})")
    show("")
    show("## Table 2: all 272 possible trips (17 areas, every start and destination)")
    show("")
    show("| Cost used | A* nodes (total) | Dijkstra nodes (total) | A* saves | Trips where A* expanded fewer |")
    show("|---|---|---|---|---|")
    settings = [
        ("km * road type multiplier", None),
        ("plain km only", {"M": 1.0, "S": 1.0, "N": 1.0}),
    ]
    for settingName, multipliers in settings:
        oneMap = loadMap(multipliers)
        totalA = 0
        totalD = 0
        fewer = 0
        tripCount = 0
        for start in oneMap.areas:
            for goal in oneMap.areas:
                if start == goal:
                    continue
                aActions, aCost, aNodes, dActions, dCost, dNodes = runBoth(oneMap, start, goal)
                totalA += aNodes
                totalD += dNodes
                tripCount += 1
                if aNodes < dNodes:
                    fewer += 1
        saved = round(100 * (totalD - totalA) / totalD)
        show(f"| {settingName} | {totalA} | {totalD} | {saved}% | {fewer} of {tripCount} |")
    resultsFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), "courier_results.md")
    with open(resultsFile, "w") as file:
        file.write("\n".join(lines) + "\n")
    print("\nsaved to", resultsFile)


if __name__ == "__main__":
    main()