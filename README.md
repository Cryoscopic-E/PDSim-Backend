# PDSim Backend

Using [Unified Planning Library](https://github.com/aiplan4eu/unified-planning) to parse PDDL and generate plans for PDSim



### Availbale planners:
    
- [FastDownward](https://github.com/aibasel/downward)
- [Tamer](https://github.com/aiplan4eu/up-tamer)
- [Pyperplan](https://github.com/aiplan4eu/up-pyperplan)

## Install
- Get the project to have the script and examples available

    `git clone https://github.com/Cryoscopic-E/PDSim-Backend.git`

- Move to project folder

    `cd PDSim-Backend`

- Activate environment (optional)

    `python -m venv venv`
    
    - Linux:
    `source myvenv/bin/activate`
    - Windows (Powereshell):
    `.\venv\Scripts\activate.ps1`
    - Windows (CMD):
    `.\venv\Scripts\activate.bat` 
    
- Install package and requirements for scripting
    
    `pip install pdsim-backend`

This will install the PDSim-Backend python package along with dependencies. It can now be used from python or as a cli script.


## Usage

### Python Mode

```python
from pdsim_backend import run_backend

run_backend(domain='./examples/pddl/blocks/domain.pddl', problem='./examples/pddl/blocks/problem.pddl')
```


### CLI Mode 

 - Provide your domain and problem files.

`python pdsim_unity.py --domain <domain_path> --problem <problem_path>`

You can provide an optional `--planner` flag, by default it'll use fast-downward, but the user will be prompted which planner is available for a specific problem.

 - Embed pdsim server in your up problem definition.

````
from pdsim_unity import pdsim_upf

< your  problem definition >

pdsim_upf(up_problem, planner_name)

````

This will create a server to communicate with unity and serve the protobuf representation of the problem and the generated plan.
