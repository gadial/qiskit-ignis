from qiskit.ignis.experiments.base import Generator
from qiskit.ignis.experiments.base import Analysis
from qiskit.ignis.experiments.base import Experiment
from qiskit import QuantumCircuit, Aer
from basis import state_tomography_circuits
from basis import process_tomography_circuits
from qiskit.ignis.verification.tomography.fitters import StateTomographyFitter
from qiskit.ignis.verification.tomography.fitters import ProcessTomographyFitter
from qiskit.providers import BaseJob
from qiskit.result import Result, Counts
from qiskit.ignis.verification.tomography.data import marginal_counts, combine_counts, count_keys

from typing import List, Dict, Union, Optional, Callable

from qiskit import execute, transpile, assemble

class StateTomographyGenerator(Generator):
    def __init__(self, qubits: Union[int, List[int]], circuit: QuantumCircuit):
        super().__init__("state tomography", circuit.num_qubits)
        self._circuits = state_tomography_circuits(circuit, qubits)
        self._qubits = qubits

    def circuits(self) -> List[QuantumCircuit]:
        """Return a list of experiment circuits."""
        return self._circuits

    def _extra_metadata(self) -> List[Dict[str, any]]:
        """Generate a list of experiment metadata dicts."""
        return [{
            'circuit_name': circ.name,
            'marginalize': circ.cregs != 1,
            'qubits': self._qubits
        }
            for circ in self._circuits]

class TomographyAnalysis(Analysis):
    def __init__(self,
                 data: Optional[Union[BaseJob, Result, List[any], any]] = None,
                 metadata: Optional[Union[List[Dict[str, any]], Dict[str, any]]] = None,
                 name: Optional[str] = None,
                 exp_id: Optional[str] = None):
        super().__init__(data, metadata,name,exp_id)
        self._analysis_fn = self.analysis_fn

    def _format_data(self, data: Result,
                     metadata: Dict[str, any],
                     index: int) -> Counts:
        counts = data.get_counts(index)
        if metadata['marginalize']:
            counts = marginal_counts(counts, metadata['qubits'])
        return counts

    def analysis_fn(self, data, metadata, **params):
        print(data)
        print(metadata)
    

class StateTomographyExperiment(Experiment):
    # pylint: disable=arguments-differ
    def __init__(self,
                 qubits: Union[int, List[int]],
                 circuit: QuantumCircuit,
                 job: Optional = None):

        analysis = TomographyAnalysis()
        generator = StateTomographyGenerator(qubits, circuit)

        super().__init__(generator=generator, analysis=analysis, job=job)


backend = Aer.get_backend('qasm_simulator')
bell = QuantumCircuit(2)
bell.h(0)
bell.cx(0, 1)



qst = state_tomography_circuits(bell, [0,1])
job = execute(qst, Aer.get_backend('qasm_simulator'))
tomo_fit = StateTomographyFitter(job.result(), qst)

exp = StateTomographyExperiment([0,1], bell)
exp.run(backend)

# qst = process_tomography_circuits(bell, [0,1])
# job = execute(qst, Aer.get_backend('qasm_simulator'))
# tomo_fit = ProcessTomographyFitter(job.result(), qst)


# #
#
#
# def run_circuit_and_tomography(circuit, qubits, method='lstsq'):
#     psi = Statevector.from_instruction(circuit)
#     qst = tomo.state_tomography_circuits(circuit, qubits)
#     job = qiskit.execute(qst, Aer.get_backend('qasm_simulator'),
#                          shots=5000)
#     tomo_fit = tomo.StateTomographyFitter(job.result(), qst)
#     rho = tomo_fit.fit(method=method)
#     return (rho, psi)
#
#
# @unittest.skipUnless(cvx_fit._HAS_CVX, 'cvxpy is required to run this test')
# class TestFitter(unittest.TestCase):
#     def test_trace_constraint(self):
#         p = numpy.array([1/2, 1/2, 1/2, 1/2, 1/2, 1/2])
#
#         # the basis matrix for 1-qubit measurement in the Pauli basis
#         A = numpy.array([
#             [0.5 + 0.j, 0.5 + 0.j, 0.5 + 0.j, 0.5 + 0.j],
#             [0.5 + 0.j, -0.5 + 0.j, -0.5 + 0.j, 0.5 + 0.j],
#             [0.5 + 0.j, 0. - 0.5j, 0. + 0.5j, 0.5 + 0.j],
#             [0.5 + 0.j, 0. + 0.5j, 0. - 0.5j, 0.5 + 0.j],
#             [1. + 0.j, 0. + 0.j, 0. + 0.j, 0. + 0.j],
#             [0. + 0.j, 0. + 0.j, 0. + 0.j, 1. + 0.j]
#         ])
#
#         for trace_value in [1, 0.3, 2, 0, 42]:
#             rho = cvx_fit.cvx_fit(p, A, trace=trace_value)
#             self.assertAlmostEqual(numpy.trace(rho), trace_value, places=3)
#
#
# class TestStateTomography(unittest.TestCase):
#     def setUp(self):
#         super().setUp()
#         self.method = 'lstsq'
#
#     def test_bell_2_qubits(self):
#         q2 = QuantumRegister(2)
#         bell = QuantumCircuit(q2)
#         bell.h(q2[0])
#         bell.cx(q2[0], q2[1])
#
#         rho, psi = run_circuit_and_tomography(bell, q2, self.method)
#         F_bell = state_fidelity(psi, rho, validate=False)
#         self.assertAlmostEqual(F_bell, 1, places=1)
#
#     def test_bell_2_qubits_no_register(self):
#         bell = QuantumCircuit(2)
#         bell.h(0)
#         bell.cx(0, 1)
#
#         rho, psi = run_circuit_and_tomography(bell, (0, 1), self.method)
#         F_bell = state_fidelity(psi, rho, validate=False)
#         self.assertAlmostEqual(F_bell, 1, places=1)
#
#     def test_different_qubit_sets(self):
#         circuit = QuantumCircuit(5)
#         circuit.h(0)
#         circuit.cx(0, 1)
#         circuit.x(2)
#         circuit.s(3)
#         circuit.z(4)
#         circuit.cx(1, 3)
#
#         for qubit_pair in [(0, 1), (2, 3), (1, 4), (0, 3)]:
#             rho, psi = run_circuit_and_tomography(circuit, qubit_pair, self.method)
#             psi = partial_trace(psi, [x for x in range(5) if x not in qubit_pair])
#             F = state_fidelity(psi, rho, validate=False)
#             self.assertAlmostEqual(F, 1, places=1)
#
#     def test_bell_3_qubits(self):
#         q3 = QuantumRegister(3)
#         bell = QuantumCircuit(q3)
#         bell.h(q3[0])
#         bell.cx(q3[0], q3[1])
#         bell.cx(q3[1], q3[2])
#
#         rho, psi = run_circuit_and_tomography(bell, q3, self.method)
#         F_bell = state_fidelity(psi, rho, validate=False)
#         self.assertAlmostEqual(F_bell, 1, places=1)
#
#     def test_complex_1_qubit_circuit(self):
#         q = QuantumRegister(1)
#         circ = QuantumCircuit(q)
#         circ.u3(1, 1, 1, q[0])
#
#         rho, psi = run_circuit_and_tomography(circ, q, self.method)
#         F_bell = state_fidelity(psi, rho, validate=False)
#         self.assertAlmostEqual(F_bell, 1, places=1)
#
#     def test_complex_3_qubit_circuit(self):
#         def rand_angles():
#             # pylint: disable=E1101
#             return tuple(2 * numpy.pi * numpy.random.random(3) - numpy.pi)
#
#         q = QuantumRegister(3)
#         circ = QuantumCircuit(q)
#         for j in range(3):
#             circ.u3(*rand_angles(), q[j])
#
#         rho, psi = run_circuit_and_tomography(circ, q, self.method)
#         F_bell = state_fidelity(psi, rho, validate=False)
#         self.assertAlmostEqual(F_bell, 1, places=1)
#
#     def test_fitter_string_input(self):
#         q3 = QuantumRegister(3)
#         bell = QuantumCircuit(q3)
#         bell.h(q3[0])
#         bell.cx(q3[0], q3[1])
#         bell.cx(q3[1], q3[2])
#
#         qst = tomo.state_tomography_circuits(bell, q3)
#         qst_names = [circ.name for circ in qst]
#         job = qiskit.execute(qst, Aer.get_backend('qasm_simulator'),
#                              shots=5000)
#         tomo_fit = tomo.StateTomographyFitter(job.result(), qst_names)
#         rho = tomo_fit.fit(method=self.method)
#         psi = Statevector.from_instruction(bell)
#         F_bell = state_fidelity(psi, rho, validate=False)
#         self.assertAlmostEqual(F_bell, 1, places=1)
#
#
# @unittest.skipUnless(cvx_fit._HAS_CVX, 'cvxpy is required  to run this test')
# class TestStateTomographyCVX(TestStateTomography):
#     def setUp(self):
#         super().setUp()
#         self.method = 'cvx'
#
#     def test_split_job(self):
#         q3 = QuantumRegister(3)
#         bell = QuantumCircuit(q3)
#         bell.h(q3[0])
#         bell.cx(q3[0], q3[1])
#         bell.cx(q3[1], q3[2])
#
#         psi = Statevector.from_instruction(bell)
#         qst = tomo.state_tomography_circuits(bell, q3)
#         qst1 = qst[:len(qst) // 2]
#         qst2 = qst[len(qst) // 2:]
#
#         backend = Aer.get_backend('qasm_simulator')
#         job1 = qiskit.execute(qst1, backend, shots=5000)
#         job2 = qiskit.execute(qst2, backend, shots=5000)
#
#         tomo_fit = tomo.StateTomographyFitter([job1.result(), job2.result()], qst)
#
#         rho_mle = tomo_fit.fit(method='lstsq')
#         F_bell_mle = state_fidelity(psi, rho_mle, validate=False)
#         self.assertAlmostEqual(F_bell_mle, 1, places=1)
#
#
# if __name__ == '__main__':
#     unittest.main()
