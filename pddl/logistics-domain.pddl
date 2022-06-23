;; logistics domain Typed version.
;;

(define (domain logistics)
  (:requirements :strips :typing)
  (:types
    city place physobj - object
    airport location - place
    package vehicle - physobj
    truck airplane - vehicle

  )

  (:predicates
    (in-city ?loc - place ?city - city)
    (at ?obj - physobj ?loc - place)
    (in ?pkg - package ?veh - vehicle)
  )

  (:action LOAD-TRUCK
    :parameters (?pkg - package ?truck - truck ?loc - place)
    :precondition (and (at ?truck ?loc) (at ?pkg ?loc))
    :effect (and (not (at ?pkg ?loc)) (in ?pkg ?truck))
  )

  (:action LOAD-AIRPLANE
    :parameters (?pkg - package ?airplane - airplane ?loc - place)
    :precondition (and (at ?pkg ?loc) (at ?airplane ?loc))
    :effect (and (not (at ?pkg ?loc)) (in ?pkg ?airplane))
  )

  (:action UNLOAD-TRUCK
    :parameters (?pk - package ?truck - truck ?loc - place)
    :precondition (and (at ?truck ?loc) (in ?pk ?truck))
    :effect (and (not (in ?pk ?truck)) (at ?pk ?loc))
  )

  (:action UNLOAD-AIRPLANE
    :parameters (?pkg - package ?airplane - airplane ?loc - place)
    :precondition (and (in ?pkg ?airplane) (at ?airplane ?loc))
    :effect (and (not (in ?pkg ?airplane)) (at ?pkg ?loc))
  )

  (:action DRIVE-TRUCK
    :parameters (?truck - truck ?loc-from - place ?loc-to - place ?city - city)
    :precondition (and (at ?truck ?loc-from) (in-city ?loc-from ?city) (in-city ?loc-to ?city))
    :effect (and (not (at ?truck ?loc-from)) (at ?truck ?loc-to))
  )

  (:action FLY-AIRPLANE
    :parameters (?airplane - airplane ?loc-from - airport ?loc-to - airport)
    :precondition (at ?airplane ?loc-from)
    :effect (and (not (at ?airplane ?loc-from)) (at ?airplane ?loc-to))
  )
)