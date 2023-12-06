from unified_planning.model.types import BOOL
from unified_planning.shortcuts import *
from pdsim_unity import pdsim_upf


def warehouse_problem():
    # TYPES #
    physical_object = UserType("physical_object")
    item = UserType("item", physical_object)
    robot = UserType("robot", physical_object)
    location = UserType("location")

    # Represents the location of the robot
    at = Fluent("at", BOOL, obj=physical_object, loc=location)

    # Represents which item the robot is holding
    holding = Fluent("holding", BOOL, r=robot, obj=item)

    # Represents whether the robot has the item
    arm_empty = Fluent("arm-empty", BOOL, obj=robot)

    # Represents whether there is a path between two locations
    path = Fluent("path", BOOL, loc1=location, loc2=location)

    # ACTIONS #

    # === PICK-UP === #

    pickup = InstantaneousAction("pick-up", rob=robot, obj=item, loc=location)
    # Preconditions
    pickup.add_precondition(
        at(pickup.rob, pickup.loc)
        &
        at(pickup.obj, pickup.loc)
        &
        arm_empty(pickup.rob))
    # Effects
    pickup.add_effect(holding(pickup.rob, pickup.obj), True)
    pickup.add_effect(arm_empty(pickup.rob), False)
    pickup.add_effect(at(pickup.obj, pickup.loc), False)

    # === DROP === #

    drop = InstantaneousAction("drop", rob=robot, obj=item, loc=location)
    # Preconditions
    drop.add_precondition(
        at(drop.rob, drop.loc)
        &
        holding(drop.rob, drop.obj))
    # Effects
    drop.add_effect(holding(drop.rob, drop.obj), False)
    drop.add_effect(arm_empty(drop.rob), True)
    drop.add_effect(at(drop.obj, drop.loc), True)

    # === MOVE === #

    move = InstantaneousAction("move", rob=robot, loc1=location, loc2=location)
    # Preconditions
    move.add_precondition(
        at(move.rob, move.loc1)
        &
        path(move.loc1, move.loc2))
    # Effects
    move.add_effect(at(move.rob, move.loc1), False)
    move.add_effect(at(move.rob, move.loc2), True)

    # CREATE PROBLEM #
    up_problem = Problem("robot")

    # === ADD FLUENTS & ACTIONS === #
    for f in [at, holding, arm_empty, path]:
        up_problem.add_fluent(f, default_initial_value=False)
    up_problem.add_actions([pickup, drop, move])

    # === CREATE OBJECTS === #

    # Add 3 locations
    rooms = ['room1', 'room2', 'room3']
    locations = [Object(x, location) for x in rooms]
    up_problem.add_objects(locations)

    # Add 1 robot
    robot = Object('robot1', robot)
    up_problem.add_object(robot)

    # Add 2 items
    items_list = ['item1', 'item2']
    items = [Object(x, item) for x in items_list]
    up_problem.add_objects(items)

    # === SET INITIAL STATE === #

    # Set initial location of robot to room1
    up_problem.set_initial_value(at(robot, locations[0]), True)

    # Set initial location of items to room2
    for item in items:
        up_problem.set_initial_value(at(item, locations[1]), True)

    # Set initial state of arm_empty to True
    up_problem.set_initial_value(arm_empty(robot), True)

    # Set Path
    # 1 <--> 2 <--> 3
    up_problem.set_initial_value(path(locations[0], locations[1]), True)
    up_problem.set_initial_value(path(locations[1], locations[0]), True)

    up_problem.set_initial_value(path(locations[1], locations[2]), True)
    up_problem.set_initial_value(path(locations[2], locations[1]), True)

    # === SET GOAL === #
    # All items are in room3
    # Robot back in room1

    up_problem.add_goal(at(robot, locations[0]))
    up_problem.add_goal(at(items[0], locations[2]))
    up_problem.add_goal(at(items[1], locations[2]))

    return up_problem


if __name__ == '__main__':
    problem = warehouse_problem()
    pdsim_upf(problem, "fast-downward")
