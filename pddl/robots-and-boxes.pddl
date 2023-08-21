(define (domain robot)

    (:requirements :strips :typing :negative-preconditions)
    
    (:types
        location physical_object - object
        room - location
        robot box - physical_object
    )
    
    (:predicates
        (at_location ?p - physical_object ?l - location)
        (path ?l1 - location ?l2 - location)
        (holding_box ?b - box ?r - robot)
    )
    
    (:action drop_down_box
        :parameters (?r - robot ?b - box ?l - room)
        
        :precondition
        (and
            (at_location ?r ?l)
            (holding_box ?b ?r)
            (not (at_location ?b ?l))
        )
        
        :effect
        (and
            (not(holding_box ?b ?r))
            (at_location ?b ?l)
        )
    )
    
    (:action pick_up_box
        :parameters (?r - robot ?b - box ?l - room)
        
        :precondition
        (and
            (at_location ?r ?l)
            (not (holding_box ?b ?r))
            (at_location ?b ?l)
        )
        
        :effect
        (and
            (not (at_location ?b ?l))
            (holding_box ?b ?r)
        )
            
    )
    
    (:action move_robot
        :parameters (?r - robot ?l1 - room ?l2 - room)
        :precondition 
        (and 
            (at_location ?r ?l1)
            (not (at_location ?r ?l2)) 
            (path ?l1 ?l2)
        )
        :effect 
        (and
            (not (at_location ?r ?l1))
            (at_location ?r ?l2)
        )
    )
)