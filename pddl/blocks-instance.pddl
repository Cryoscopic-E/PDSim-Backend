(define (problem BLOCKS-4-1)
(:domain BLOCKS)
(:objects A C D B - block)
(:init (clear B) (ontable D) (on B C) (on C A) (on A D) (handempty))
(:goal (and (on D C) (on C A) (on A B)))
)