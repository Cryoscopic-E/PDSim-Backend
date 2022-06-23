# PDSim Backend

Using [Unified Planning Library](https://github.com/aiplan4eu/unified-planning) to parse PDDL and generate plans for PDSim



### Availbale planners:
    
- [FastDownward](https://github.com/aibasel/downward)
- More to come..

## Install
- Get the project

    `git clone https://github.com/Cryoscopic-E/PDSim-Backend.git`

- Move to project folder

    `cd PDSim-Backend`

- Create pdsim anaconda environment

    `conda env create -f environment.yml`

## Usage

Run the server before starting a new simulation in Unity.

- Activate environment

    `conda activate pdsim`

- Run server
    
    `python server_upf.py`