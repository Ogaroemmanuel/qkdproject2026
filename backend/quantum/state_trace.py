"""Exact ensemble states for the explanatory replay, in message order q0,q1."""

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix, Kraus, partial_trace

from backend.quantum.bell_pairs import create_bell_pair
from backend.quantum.superdense import encode_message


def build_state_trace(bits, eve_active=False, noise_probability=0.0):
    """Keep ensemble dephasing separate from a sampled measurement trajectory."""
    stages = {}

    def record(name, state):
        # Qiskit indexes basis states as q1q0; the interface labels them q0q1.
        order = [0, 2, 1, 3]
        matrix = state.data[np.ix_(order, order)]
        bloch = []
        for qubit in (0, 1):
            local = partial_trace(state, [1 - qubit]).data
            bloch.append([float(2 * local[0, 1].real),
                          float(-2 * local[0, 1].imag),
                          float((local[0, 0] - local[1, 1]).real)])
        stages[name] = {
            "probabilities": [float(x.real) for x in np.diag(matrix)],
            "coherences": [[float(abs(x)) for x in row] for row in matrix],
            "density_real": matrix.real.tolist(),
            "density_imag": matrix.imag.tolist(),
            "bloch": bloch,
            "purity": float(np.trace(state.data @ state.data).real),
        }

    initial = QuantumCircuit(2)
    record("initial", DensityMatrix.from_instruction(initial))
    initial.h(0)
    record("superposition", DensityMatrix.from_instruction(initial))
    bell = create_bell_pair()
    record("entangled", DensityMatrix.from_instruction(bell))
    encoded = DensityMatrix.from_instruction(encode_message(bell, bits))
    record("encoded", encoded)
    channel = encoded
    if eve_active:
        channel = channel.evolve(Kraus([np.diag([1, 0]), np.diag([0, 1])]), [0])
    if noise_probability:
        p = noise_probability
        channel = channel.evolve(Kraus([
            np.sqrt(1-p)*np.eye(2), np.sqrt(p/3)*np.array([[0,1],[1,0]]),
            np.sqrt(p/3)*np.array([[0,-1j],[1j,0]]), np.sqrt(p/3)*np.diag([1,-1])]), [0])
    record("channel", channel)
    decoder = QuantumCircuit(2)
    decoder.cx(0, 1)
    decoder.h(0)
    record("decoded", channel.evolve(decoder))
    return stages
