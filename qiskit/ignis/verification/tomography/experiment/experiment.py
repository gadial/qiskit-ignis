import sys
import numpy as np
sys.path = [sys.path[-1]] + sys.path

from qiskit.ignis.experiments.base import Generator
from qiskit.ignis.experiments.base import Experiment
from qiskit import QuantumCircuit, Aer
from qiskit.ignis.verification.tomography.basis import state_tomography_circuits
from qiskit.ignis.verification.tomography.basis import process_tomography_circuits
from qiskit.ignis.verification.tomography.basis import TomographyBasis, default_basis
from qiskit.ignis.verification.tomography.fitters import StateTomographyFitter
from qiskit.ignis.verification.tomography.fitters import ProcessTomographyFitter
from ast import literal_eval

from typing import List, Dict, Union, Optional, Tuple

from qiskit import execute, transpile, assemble
from analysis import TomographyAnalysis

class TomographyGenerator(Generator):
    def __init__(self,
                 name: str,
                 circuit: QuantumCircuit,
                 meas_qubits: Union[int, List[int]] = None,
                 prep_qubits: Union[int, List[int]] = None,
                 meas_clbits: Union[int, List[int]] = None
                 ):
        super().__init__(name, circuit.num_qubits)
        self._meas_qubits = meas_qubits if meas_qubits else list(range(circuit.num_qubits))
        self._prep_qubits = prep_qubits if prep_qubits is not None else self._meas_qubits
        self._meas_clbits = meas_clbits if meas_clbits is not None else self._meas_qubits

    def circuits(self) -> List[QuantumCircuit]:
        """Return a list of experiment circuits."""
        return self._circuits

    def _extra_metadata(self) -> List[Dict[str, any]]:
        """Generate a list of experiment metadata dicts."""
        return [{
            'circuit_name': circ.name,
            'marginalize': circ.cregs != 1,
            'meas_qubits': self._meas_qubits,
            'prep_qubits': self._prep_qubits,
            'meas_clbits': self._meas_clbits
        }
            for circ in self._circuits]


class StateTomographyExperiment(Experiment):
    # pylint: disable=arguments-differ
    def __init__(self,
                 circuit: QuantumCircuit,
                 qubits: Union[int, List[int]] = None,
                 meas_basis: Union[TomographyBasis, str] = 'Pauli',
                 meas_labels: Union[str, Tuple[str], List[Tuple[str]]] = 'Pauli',
                 method: str = 'auto',
                 job: Optional = None):

        analysis = TomographyAnalysis(method=method,
                                      meas_basis=meas_basis,
                                      )
        generator = StateTomographyGenerator(circuit, qubits,
                                             meas_basis=meas_basis,
                                             meas_labels=meas_labels
                                             )

        super().__init__(generator=generator, analysis=analysis, job=job)

class ProcessTomographyExperiment(Experiment):
    # pylint: disable=arguments-differ
    def __init__(self,
                 circuit: QuantumCircuit,
                 qubits: Union[int, List[int]] = None,
                 meas_basis: Union[TomographyBasis, str] = 'Pauli',
                 meas_labels: Union[str, Tuple[str], List[Tuple[str]]] = 'Pauli',
                 prep_basis: Union[TomographyBasis, str] = 'Pauli',
                 prep_labels: Union[str, Tuple[str], List[Tuple[str]]] = 'Pauli',
                 method: str = 'auto',
                 job: Optional = None):

        analysis = TomographyAnalysis(method=method,
                                      meas_basis=meas_basis,
                                      prep_basis=prep_basis
                                      )
        generator = ProcessTomographyGenerator(circuit, qubits,
                                               meas_basis=meas_basis,
                                               meas_labels=meas_labels,
                                               prep_basis=prep_basis,
                                               prep_labels=prep_labels
                                               )

        super().__init__(generator=generator, analysis=analysis, job=job)

class StateTomographyGenerator(TomographyGenerator):
    def __init__(self,
                 circuit: QuantumCircuit,
                 qubits: Union[int, List[int]] = None,
                 meas_basis: Union[TomographyBasis, str] = 'Pauli',
                 meas_labels: Union[str, Tuple[str], List[Tuple[str]]] = 'Pauli'
                 ):
        super().__init__("state tomography", circuit, qubits)
        self._circuits = state_tomography_circuits(circuit,
                                                   self._meas_qubits,
                                                   meas_basis=meas_basis,
                                                   meas_labels=meas_labels
                                                   )

    def _extra_metadata(self):
        metadata_list = super()._extra_metadata()
        for metadata in metadata_list:
            metadata['prep_label'] = None
            metadata['meas_label'] = literal_eval(metadata['circuit_name'])
        return metadata_list

class ProcessTomographyGenerator(TomographyGenerator):
    def __init__(self,
                 circuit: QuantumCircuit,
                 qubits: Union[int, List[int]] = None,
                 meas_basis: Union[TomographyBasis, str] = 'Pauli',
                 meas_labels: Union[str, Tuple[str], List[Tuple[str]]] = 'Pauli',
                 prep_basis: Union[TomographyBasis, str] = 'Pauli',
                 prep_labels: Union[str, Tuple[str], List[Tuple[str]]] = 'Pauli',
                 ):
        super().__init__("process tomography", circuit, qubits)
        self._circuits = process_tomography_circuits(circuit,
                                                     self._meas_qubits,
                                                     meas_basis=meas_basis,
                                                     meas_labels=meas_labels,
                                                     prep_basis=prep_basis,
                                                     prep_labels=prep_labels
                                                     )

    def _extra_metadata(self):
        metadata_list = super()._extra_metadata()
        for metadata in metadata_list:
            circuit_labels = literal_eval(metadata['circuit_name'])
            metadata['prep_label'] = circuit_labels[0]
            metadata['meas_label'] = circuit_labels[1]
        return metadata_list