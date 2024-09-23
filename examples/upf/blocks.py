from unified_planning.model.types import BOOL
from unified_planning.shortcuts import *


def blocks_upf_problem():
    # Create a new type (without parent)
    block = UserType("block")

    # The UP calls "fluents" both predicates and functions
    # Each fluent has a type (BOOL for all fluents in this case) and might have parameters
    clear = Fluent("clear", BOOL, obj=block)  # in PDDL this would be (clear ?obj - block)
    on_table = Fluent("on-table", BOOL, obj=block)
    arm_empty = Fluent("arm-empty", BOOL)
    holding = Fluent("holding", BOOL, obj=block)
    on = Fluent("on", BOOL, above=block, below=block)

    # Pickup action with one parameter a precondition formula and some effects
    pickup = InstantaneousAction("pickup", obj=block)
    pickup.add_precondition(clear(pickup.obj) & on_table(pickup.obj) & arm_empty)
    pickup.add_effect(holding(pickup.obj), True)
    pickup.add_effect(clear(pickup.obj), False)
    pickup.add_effect(on_table(pickup.obj), False)
    pickup.add_effect(arm_empty, False)

    # More actions...
    putdown = InstantaneousAction("putdown", obj=block)
    putdown.add_precondition(holding(putdown.obj))
    putdown.add_effect(holding(putdown.obj), False)
    putdown.add_effect(clear(putdown.obj), True)
    putdown.add_effect(on_table(putdown.obj), True)
    putdown.add_effect(arm_empty, True)

    stack = InstantaneousAction("stack", obj=block, underobj=block)
    # More than one precondition can be set (implicit conjunction)
    stack.add_precondition(clear(stack.underobj) & holding(stack.obj))
    stack.add_precondition(Not(Equals(stack.obj, stack.underobj)))
    stack.add_effect(arm_empty, True)
    stack.add_effect(clear(stack.obj), True)
    stack.add_effect(on(stack.obj, stack.underobj), True)
    stack.add_effect(clear(stack.underobj), False)
    stack.add_effect(holding(stack.obj), False)

    unstack = InstantaneousAction("unstack", obj=block, underobj=block)
    unstack.add_precondition(on(unstack.obj, unstack.underobj) & clear(unstack.obj) & arm_empty)
    unstack.add_effect(holding(unstack.obj), True)
    unstack.add_effect(clear(unstack.underobj), True)
    unstack.add_effect(on(unstack.obj, unstack.underobj), False)
    unstack.add_effect(clear(unstack.obj), False)
    unstack.add_effect(arm_empty, False)

    # So far we just created objects in memory, we have not yet declared a problem
    # A `Problem` is a planning instance, but as a mutable object it can be partially specified
    # Here we just add fluents and actions, so we represent the "domain"
    problem = Problem("blocksworld")
    for f in [clear, on_table, arm_empty, holding, on]:
        # We can specify arbitrary default initial values (particularly useful for numeric fluents)
        problem.add_fluent(f, default_initial_value=False)
    problem.add_actions([pickup, putdown, stack, unstack])

    # Each letter is a block
    objects = [Object(x, block) for x in "DEMO"]
    problem.add_objects(objects)

    # Set the initial state (all fluents are false by default because of the domain specification)
    problem.set_initial_value(arm_empty, True)
    for o in objects:
        problem.set_initial_value(on_table(o), True)
        problem.set_initial_value(clear(o), True)

    # Set the goal
    base = objects[0]
    for o in objects[1:]:
        problem.add_goal(on(base, o))
        base = o

    return problem


from pdsim_unity import pdsim_upf

if __name__ == '__main__':
    upf_problem = blocks_upf_problem()
    pdsim_upf(upf_problem, "fast-downward")
