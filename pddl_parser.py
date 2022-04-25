from tarski.errors import LanguageError, UndefinedElement, SyntacticError
from tarski.model import unwrap_tuple
from tarski.syntax.sorts import children
from tarski.io.fstrips import FstripsReader, DelEffect
import simplejson as json


class PDDLParser(FstripsReader):
    def __init__(self):
        FstripsReader.__init__(self, raise_on_error=True)
        self.current_domain = ''
        self.current_instance = ''

    def set_files(self, domain_text, instance_text):
        self.current_domain = domain_text
        self.current_instance = instance_text

    def _parse(self, text, rule):
        parse_tree, _ = self.parser.parse_string(text, rule)
        self.parser.visit(parse_tree)

    def _parse_pddl_domain(self):
        self._parse(self.current_domain, "domain")

    def _parse_pddl_problem(self):
        self._parse(self.current_instance, "problem")
        return self.problem

    def parse_pddl(self):

        output = {}

        try:
            self._parse_pddl_domain()
            problem = self._parse_pddl_problem()
            lang = problem.language
            parsed_pddl = lang.dump()

            problem_name = problem.name

            # Get Objects
            objects = {}
            for o in lang.constants():
                object_name = o.name
                object_type = lang.get_constant(object_name).sort.name

                #obj["name"] = object_name
                #obj["type"] = lang.get_constant(object_name).sort.name

                if objects.get(object_type) is None:
                    objects[object_type] = []
                objects[object_type].append(object_name)

            # Get Types
            types = {}
            for t in parsed_pddl["sorts"]:
                s = lang.get_sort(t["name"])
                types[s.name] = [c.name for c in children(s)]

            # Get Predicates
            predicates = {}
            for p in parsed_pddl["predicates"]:
                if isinstance(p["symbol"], str):
                    # predicate = {"name": p["symbol"],"attributes": p["domain"]}
                    # predicates.append(predicate)
                    predicates[p["symbol"]] = p["domain"]

            # Get Init
            init_block = []
            for k, ext in problem.init.predicate_extensions.items():
                pred = lang.get_predicate(k[0])
                for tup in ext:
                    #fact = {"predicate": pred.symbol, "attributes": [att.name for att in unwrap_tuple(tup)]}
                    fact = {pred.symbol: [
                        att.name for att in unwrap_tuple(tup)]}
                    init_block.append(fact)

            # Get Actions
            actions = {}

            for a in list(problem.actions):
                action_class = problem.get_action(a)
                actions[a.lower()] = {}
                actions[a.lower()]["params"] = [
                    p.sort.name for p in action_class.parameters]
                actions[a.lower()]["effects"] = []
                params = [p.symbol for p in action_class.parameters]
                for effect in action_class.effects:
                    effect_predicate = effect.atom.predicate
                    effect_params = effect.atom.subterms
                    indexes = [params.index(ep.symbol) for ep in effect_params]
                    actions[a.lower()]["effects"].append(
                        {"predicate": effect_predicate.symbol,
                         "param_index": indexes,
                         "negated": isinstance(effect, DelEffect)})
            
            output["instance_name"] = problem_name
            output["objects"] = objects
            output["predicates"] = predicates
            output["types"] = types
            output["init"] = init_block
            output["actions"] = actions

        except LanguageError as error:
            if isinstance(error, UndefinedElement):
                output["error"] = str(error).split('(')[0]
            elif isinstance(error, SyntacticError):
                output["error"] = "Syntax Error: " + str(error)
            else:
                output["error"] = "Language error"
        print(output)
        return json.dumps(output).encode("utf-8")
