(define (problem prob)
 (:domain robot-warehouse)
 (:objects cell_0_1 cell_0_2 cell_0_3 
           cell_1_1 cell_1_2 cell_1_3 
           cell_2_1 cell_2_2 cell_2_3 - cell
           robot1 robot2 - robot
           box1 box2 - box
           van1 van2 - van
)
(:init
    (box-at box1 cell_2_1)
    (box-at box2 cell_1_3)

    (robot-at robot1 cell_2_2)
    (robot-at robot2 cell_2_3)
    (robot-empty robot1)
    (robot-empty robot2)

    (van-request van1 box1)
    (van-request van2 box2)

    (van-at van1 cell_0_1)
    (van-at van2 cell_0_3)
    
    (clear cell_0_1)
    (clear cell_0_2)
    (clear cell_0_3)
    (clear cell_1_1)
    (clear cell_1_2)
    (clear cell_1_3)
    (clear cell_2_1)

    (up cell_0_1 cell_1_1)
    (up cell_0_2 cell_1_2)
    (up cell_0_3 cell_1_3)
    (up cell_1_1 cell_2_1)
    (up cell_1_2 cell_2_2)
    (up cell_1_3 cell_2_3)

    (down cell_1_1 cell_0_1)
    (down cell_1_2 cell_0_2)
    (down cell_1_3 cell_0_3)
    (down cell_2_1 cell_1_1)
    (down cell_2_2 cell_1_2)
    (down cell_2_3 cell_1_3)

    (right cell_0_2 cell_0_1)
    (right cell_0_3 cell_0_2)
    (right cell_1_2 cell_1_1)
    (right cell_1_3 cell_1_2)
    (right cell_2_2 cell_2_1)
    (right cell_2_3 cell_2_2)

    (left cell_0_1 cell_0_2)
    (left cell_0_2 cell_0_3)
    (left cell_1_1 cell_1_2)
    (left cell_1_2 cell_1_3)
    (left cell_2_1 cell_2_2)
    (left cell_2_2 cell_2_3)
)
(:goal 
 (and
    (van-loaded van1)
 )
)
)