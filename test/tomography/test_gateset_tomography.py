# -*- coding: utf-8 -*-
#
# This code is part of Qiskit.
#
# (C) Copyright IBM 2019.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

# pylint: disable=missing-docstring

import unittest

import numpy as np
from qiskit import Aer
from qiskit.compiler import transpile, assemble
from qiskit.ignis.verification.tomography.fitters.gateset_fitter import gateset_linear_inversion
from qiskit.ignis.verification.tomography.basis.circuits import gateset_tomography_circuits
from qiskit.ignis.verification.tomography.fitters.base_fitter import TomographyFitter
from qiskit.quantum_info import state_fidelity

class TestGatesetTomography(unittest.TestCase):
    def collect_tomography_data(self, shots=10000):
        backend_qasm = Aer.get_backend('qasm_simulator')
        circuits = gateset_tomography_circuits()
        transpiled_circuits = transpile(circuits, backend=backend_qasm)
        qobj = assemble(transpiled_circuits, shots=shots)
        result = backend_qasm.run(qobj).result()
        t = TomographyFitter(result, circuits)
        return t._data


    def test_linear_inversion(self):
        # based on linear inversion in	arXiv:1310.4492
        # PTM representation of Id, X rotation by 90 degrees, Y rotation by 90 degrees
        G0 = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
        G1 = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, -1], [0, 0, 1, 0]])
        G2 = np.array([[1, 0, 0, 0], [0, 0, 0, -1], [0, 0, 1, 0], [0, 1, 0, 0]])

        F0 = G0
        F1 = G1
        F2 = G2
        F3 = G1 @ G1

        # in PTM: [(1,0),(0,0)] == 0.5 I + 0.5 Z
        rho = np.array([[0.5], [0], [0], [0.5]])

        # Z-basis measurement in PTM
        E = np.array([[1, 0, 0, 1]])

        data = self.collect_tomography_data(shots=10000)
        gates, gate_labels = zip(*gateset_linear_inversion(data))
        # linear inversion should result in gates of the form B^-1*G*B where the columns
        # of B are F_k * rho, F_k being the SPAM circuits

        Fs = [F0, F1, F2, F3]
        B = np.array([(F @ rho).T[0] for F in Fs]).T
        expected_gates = [np.linalg.inv(B) @ G @ B for G in [G0, G1, G2]]
        for expected_gate, gate, label in zip(expected_gates, gates, gate_labels):
            hs_distance = sum([np.abs(x)**2 for x in np.nditer(expected_gate - gate)])
            msg = "Failure on gate {}: Expected gate = \n{}\n vs Actual gate = \n{}".format(label, expected_gate, gate)
            self.assertAlmostEqual(hs_distance, 0, delta = 0.1, msg=msg)


if __name__ == '__main__':
    unittest.main()
