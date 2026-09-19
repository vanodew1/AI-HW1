# search.py

"""
In search.py, you will implement generic search algorithms (A* and Dijkstra)
that operate on any problem implementing the SearchProblem interface below.

For this assignment you will formulate TWO problems against this interface:
    1. Robot Navigation with Obstacles 
    2. Courier Delivery Route Planning 

You will implement a SearchProblem subclass for each (in separate files,
e.g. robotNavigation.py and courierDelivery.py), then write generic
aStarSearch and dijkstraSearch functions here that work on either subclass
purely through this interface.
"""

import util

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't
    implement any of the methods (in object-oriented terminology: an
    abstract class).

    You do not need to change anything in this class, ever. Instead, you
    will write problem-specific subclasses (for Robot Navigation and for
    Courier Delivery) that implement each of these methods.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples,
        (successor, action, stepCost), where 'successor' is a successor to
        the current state, 'action' is the action required to get there,
        and 'stepCost' is the incremental cost of expanding to that
        successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of
        actions. The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()

    def getHeuristic(self, state):
        """
         state: the current state of the agent

        This function returns the heuristic value of the current state,
        i.e. the estimated remaining cost/distance to the goal. Used by
        A* Search. Should return 0 for Dijkstra-equivalent behaviour.
        """
        util.raiseNotDefined()


def bestFirstSearch(problem, useHeuristic):
    """
    The one search engine behind both algorithms.

        A*       : priority = g + h   (useHeuristic=True)
        Dijkstra : priority = g       (useHeuristic=False, same as h = 0)

    where g is the cost of the path found so far and h is the heuristic.
    Only the SearchProblem interface is used, so it works on any problem.

    Returns (actions, totalCost, nodesExpanded):
        actions       : list of actions from the start state to a goal state,
                        or None if no goal can be reached
        totalCost     : cost of that path (infinity if unreachable)
        nodesExpanded : number of states taken off the frontier and expanded
                        (the goal state itself is counted)
    """
    startState = problem.getStartState()
    def heuristic(state): # returns h(state) if useHeuristic else 0
        return problem.getHeuristic(state) if useHeuristic else 0
    frontier = util.PriorityQueue() # priority queue of (state, actions, cost) triples
    frontier.push((startState, [], 0), (heuristic(startState), heuristic(startState))) # priority = (g + h, h) so that ties are broken by h
    bestCostSoFar = {startState: 0} 
    nodesExpanded = 0 
    while not frontier.isEmpty(): # while there are still states to explore
        state, actions, cost = frontier.pop()
        if cost > bestCostSoFar[state]: # ignore this state if a cheaper path to it has already been found
            continue
        nodesExpanded += 1
        if problem.isGoalState(state): # if this is a goal state, return the path to it and its cost
            return actions, cost, nodesExpanded

        for successor, action, stepCost in problem.getSuccessors(state): # for each successor of the current state
            newCost = cost + stepCost
            if newCost < bestCostSoFar.get(successor, float("inf")): # if this path to the successor is cheaper than any previously found
                bestCostSoFar[successor] = newCost
                h = heuristic(successor)
                frontier.push((successor, actions + [action], newCost),
                              (newCost + h, h))
    return None, float("inf"), nodesExpanded


def aStarSearch(problem):
    """
    Search the node that has the lowest combined cost (g) and heuristic (h)
    first, i.e. lowest f = g + h.

    This must work generically on ANY SearchProblem passed in - it should
    not know anything about grids, CSV files, robots, or couriers. All of
    that logic belongs inside the SearchProblem subclasses.

    Should return the list of actions from start to goal. Consider also
    tracking/returning the total cost and number of nodes expanded, since
    the assignment asks you to report these for the comparative analysis.
    """
    return bestFirstSearch(problem, useHeuristic = True)


def dijkstraSearch(problem):
    """
    Uniform-cost search: expand the node with the lowest cumulative path
    cost (g) first, ignoring the heuristic entirely (equivalent to A* with
    h(state) = 0 for every state).

    Like aStarSearch, this must work generically on any SearchProblem.
    You may reuse/adapt your CS 102 - DSA implementation here.
    """
    return bestFirstSearch(problem, useHeuristic = False)


def searchWithStopovers(problem, stopovers):
    """
    Part (d): Route with Stopovers.

    Adapts A* Search so that the resulting route starts at the hub, visits
    every location in `stopovers` (in some order you determine), and
    returns to the hub - using A* Search to find the route between each
    consecutive pair of locations.

    This is the function you should pseudocode/implement for Question 1(d).
    stopovers: a list of states/locations that must all be visited before
               returning to the start state.

    Should return the complete route, its total cost, and the order in
    which stopovers were visited (see assignment spec for exact output
    requirements).
    """
    "*** YOUR STOPOVER-ROUTING CODE HERE ***"
    util.raiseNotDefined()