import pyomo.environ as pyo


class Parent():
    def __init__(self, solver: pyo.SolverFactory) -> None:
        self.solver = solver
    

        

class Child():
    def __init__(self, solver: pyo.SolverFactory) -> None:
        self.solver = solver
    