(define (domain robot-warehouse)
(:requirements :typing)
(:types 
	robot cell box van - object
	)

(:predicates
		(robot-at ?r - robot ?x - cell)
		(box-at ?b - box ?x - cell)

		;movement
		(up ?x - cell ?y - cell)
		(down ?x - cell ?y - cell)
		(right ?x - cell ?y - cell)
		(left ?x - cell ?y - cell)
		(clear ?x - cell)

		;van
		(van-at ?v - van ?x - cell)
		(van-request ?v - van ?b - box)
		(van-loaded ?v - van)

		;robot
		(robot-has ?r - robot ?b - box)
		(robot-empty ?r - robot)
)


(:action pick-up-box
  :parameters (?r - robot ?b - box ?c - cell)
  :precondition (and 
		(robot-at ?r ?c)
  		(robot-empty ?r) 
		;(box-at ?b ?c)
		)
  :effect (and 
  		(not (robot-empty ?r))
  		(not (box-at ?b ?c))
  		(robot-has ?r ?b)
  		)
) 

(:action put-down-box
  :parameters (?r - robot ?b - box ?c - cell)
  :precondition (and 
  		(robot-has ?r ?b)
		(robot-at ?r ?c)
		)
  :effect (and
  		(not(robot-has ?r ?b))
  		(robot-empty ?r)
		(box-at ?b ?c)
  		)
) 

(:action load-on-van
  :parameters (?r - robot ?b - box ?c - cell ?v - van)
  :precondition (and 
  		(robot-has ?r ?b)
		(robot-at ?r ?c)
		(van-at ?v ?c)
		(van-request ?v ?b)
		)
  :effect (and 
  		(not (robot-has ?r ?b))
  		(robot-empty ?r)
		(van-loaded ?v)
  		)
)

; Robot movements
(:action move-up 
  :parameters (?r - robot ?x - cell ?y - cell)
  :precondition (and 
  	(robot-at ?r ?x) 
	(up ?y ?x) 
	(clear ?y))
  :effect (and 
  	(robot-at ?r ?y) 
	(not (robot-at ?r ?x))
    (clear ?x) 
	(not (clear ?y)))
)


(:action move-down 
  :parameters (?r - robot ?x - cell ?y - cell)
  :precondition (and 
  	(robot-at ?r ?x) 
	(down ?y ?x) 
	(clear ?y))
  :effect (and (robot-at ?r ?y) (not (robot-at ?r ?x))
               (clear ?x) (not (clear ?y))
))

(:action move-right 
  :parameters (?r - robot ?x - cell ?y - cell)
  :precondition (and 
  	(robot-at ?r ?x) 
	(right ?y ?x) 
	(clear ?y))
  :effect (and 
  	(robot-at ?r ?y) 
	(not (robot-at ?r ?x))
    (clear ?x) 
	(not (clear ?y))
))

(:action move-left 
  :parameters (?r - robot ?x - cell ?y - cell)
  :precondition (and 
  	(robot-at ?r ?x) 
	(left ?y ?x) 
	(clear ?y))
  :effect (and 
  	(robot-at ?r ?y) 
	(not (robot-at ?r ?x))
    (clear ?x) 
	(not (clear ?y))
))

)