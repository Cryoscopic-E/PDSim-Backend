(define (problem depotprob1818) (:domain Depot)
(:objects
	depot0 distributor0 distributor1 truck0 truck1 pallet0 pallet1 pallet2 crate0 crate1 hoist0 hoist1 hoist2 )
(:init
	(pallet pallet0)
	(surface pallet0)
	(at pallet0 depot0)
	(clear crate1)
	(pallet pallet1)
	(surface pallet1)
	(at pallet1 distributor0)
	(clear crate0)
	(pallet pallet2)
	(surface pallet2)
	(at pallet2 distributor1)
	(clear pallet2)
	(truck truck0)
	(at truck0 distributor1)
	(truck truck1)
	(at truck1 depot0)
	(hoist hoist0)
	(at hoist0 depot0)
	(available hoist0)
	(hoist hoist1)
	(at hoist1 distributor0)
	(available hoist1)
	(hoist hoist2)
	(at hoist2 distributor1)
	(available hoist2)
	(crate crate0)
	(surface crate0)
	(at crate0 distributor0)
	(on crate0 pallet1)
	(crate crate1)
	(surface crate1)
	(at crate1 depot0)
	(on crate1 pallet0)
	(place depot0)
	(place distributor0)
	(place distributor1)
)

(:goal (and
		(on crate0 pallet2)
		(on crate1 pallet1)
	)
))