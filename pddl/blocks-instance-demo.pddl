(define (problem BLOCKS-4-1)
(:domain BLOCKS)
(:objects D E M O - block)
(:init 
(clear D)
(clear E)
(clear M)
(clear O)

(ontable D)
(ontable E)
(ontable M)
(ontable O)


(handempty))
(:goal (and (on D E) (on E M) (on M O)))
)