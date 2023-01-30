# PDSim Backend

Using [Unified Planning Library](https://github.com/aiplan4eu/unified-planning) to parse PDDL and generate plans for PDSim



### Availbale planners:
    
- [FastDownward](https://github.com/aibasel/downward)
- [Tamer](https://github.com/aiplan4eu/up-tamer)
- [Pyperplan](https://github.com/aiplan4eu/up-pyperplan)

## Install
- Get the project

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
    
- Install requirements
    
    `python -m pip install -r requirements.txt`

## Usage

Run the server before starting a new simulation in Unity.

    `python server_upf.py`
