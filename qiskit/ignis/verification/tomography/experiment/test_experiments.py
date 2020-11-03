import unittest
import sys
sys.path = [sys.path[-1]] + sys.path
from qiskit import Aer
from qiskit import QuantumCircuit
from experiment import StateTomographyExperiment
from qiskit.quantum_info import state_fidelity, partial_trace, Statevector

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


if __name__ == '__main__':
    unittest.main()