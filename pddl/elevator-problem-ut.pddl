(define (problem simple)
  (:domain miconic)
  (:objects
    p0 f0 f1
  )

  (:init
    (passenger p0)
    (floor f0)
    (floor f1)

    (above f0 f1)
    (origin p0 f1)
    (destin p0 f0)

    (lift-at f0)
  )

  (:goal
    (and
      (served p0)
    )
  )
)