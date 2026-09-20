# 1d
import os
import search
from courierDelivery import RoadMap, CourierProblem
csvFolder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "csv")
hub = "Saddar (Hub)"

tests = [
    ["Clifton", "Gulshan-e-Iqbal", "North Nazimabad"],
    ["Korangi", "Malir", "Orangi Town", "Clifton"],
    ["Lyari", "DHA"],
]

def main():
    roadMap = RoadMap(os.path.join(csvFolder, "Connections.csv"), os.path.join(csvFolder, "heuristics.csv"), os.path.join(csvFolder, "TrackType.csv"))
    for stopovers in tests:
        problem = CourierProblem(roadMap, hub, hub)
        route, cost, order = search.searchWithStopovers(problem, stopovers)
        print("Stopovers given :", ", ".join(stopovers))
        print("Order visited   :", " > ".join([hub] + order + [hub]))
        print("Complete route  :", " > ".join([hub] + route))
        print(f"Total cost      : {cost:.3f}")
        print()

if __name__ == "__main__":
    main()