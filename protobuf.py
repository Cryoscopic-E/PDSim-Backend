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
        './pddl/blocks-domain.pddl', './pddl/blocks-instance-demo.pddl')

    converted = writer.convert(problem)

    back_problem = reader.convert(converted)

    print(back_problem)


if __name__ == '__main__':
    main()
