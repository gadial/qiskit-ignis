import unittest
from qiskit import Aer
from qiskit import QuantumCircuit
from experiment import StateTomographyExperiment, ProcessTomographyExperiment
from qiskit.quantum_info import state_fidelity, partial_trace, Statevector, Choi

BACKEND = Aer.get_backend('qasm_simulator')
class TestStateTomography(unittest.TestCase):
    def test_bell_basic(self):
        bell = QuantumCircuit(2)
        bell.h(0)
        bell.cx(0, 1)

        exp = StateTomographyExperiment(bell, [0])
        rho = exp.run(BACKEND)
        psi = partial_trace(Statevector.from_instruction(bell), [0])

        F_bell = state_fidelity(psi, rho, validate=False)
        self.assertAlmostEqual(F_bell, 1, places=1)

    def test_bell_meas(self):
        bell = QuantumCircuit(2,2)
        bell.h(0)
        bell.cx(0, 1)

        psi = partial_trace(Statevector.from_instruction(bell), [0])

        bell.measure(1,1)

        exp = StateTomographyExperiment(bell, [0])
        rho = exp.run(BACKEND)

        F_bell = state_fidelity(psi, rho, validate=False)
        self.assertAlmostEqual(F_bell, 1, places=1)

    def test_bell_full(self):
        bell = QuantumCircuit(2,2)
        bell.h(0)
        bell.cx(0, 1)

        exp = StateTomographyExperiment(bell)
        rho = exp.run(BACKEND)
        psi = Statevector.from_instruction(bell)
        F_bell = state_fidelity(psi, rho, validate=False)
        self.assertAlmostEqual(F_bell, 1, places=1)

class TestProcessTomography(unittest.TestCase):
    def test_bell_full(self):
        bell = QuantumCircuit(2)
        bell.h(0)
        bell.cx(0, 1)

        exp = ProcessTomographyExperiment(bell)
        rho = exp.run(BACKEND)
        psi = Choi(bell).data
        F_bell = state_fidelity(psi / 4, rho / 4, validate=False)
        self.assertAlmostEqual(F_bell, 1, places=1)

if __name__ == '__main__':
    unittest.main()