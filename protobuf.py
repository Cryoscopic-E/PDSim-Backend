from unified_planning.engines import PlanGenerationResult
from unified_planning.grpc.proto_writer import ProtobufWriter
from unified_planning.grpc.proto_reader import ProtobufReader
from unified_planning.io.pddl_reader import PDDLReader


def main():
    writer = ProtobufWriter()
    reader = ProtobufReader()
    # read the domain file
    pddl_reader = PDDLReader()

    problem = pddl_reader.parse_problem(
        './pddl/crewplanning.pddl', './pddl/crewplanning-problem.pddl')

    converted = writer.convert(problem)
    # `converted` need to be sent to unity
    print(converted.actions)

    # send as bytes
    converted = converted.SerializeToString()
    print(type(converted))

    # print(converted)

    # back_problem = reader.convert(converted)

    # print(back_problem)


if __name__ == '__main__':
    main()
