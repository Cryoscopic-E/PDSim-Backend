# PDSim Backend

Using [Unified Planning Library](https://github.com/aiplan4eu/unified-planning) to parse PDDL and generate plans for PDSim


## Install

This project is now hosted on [pypi](https://pypi.org/project/pdsim-backend/)

### Use Conda (preferred)

##### Create a new venv
`conda create -n pdsim python=3.11`

##### Activate
`conda activate pdsim`
  
##### Install PDSim-Backend
`pip install pdsim-backend`

### Use Venv
  
##### Create a new venv
`python -m venv <directory>`

##### Activate
- Windows(Powershell): `<directory>\Scripts\activate.ps1`
- Linux/macOS: `source <directory>/bin/activate`
  
##### Install PDSim-Backend
`pip install pdsim-backend` 

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

PDSim will try to find the planner that suits best the planning problem provided and let you choose which one to run.

#### Some Availbale planners:
    
- [FastDownward](https://github.com/aibasel/downward)
- [Tamer](https://github.com/aiplan4eu/up-tamer)
- [Pyperplan](https://github.com/aiplan4eu/up-pyperplan)
FUll list [here](https://unified-planning.readthedocs.io/en/latest/engines/01_available_engines.html)

