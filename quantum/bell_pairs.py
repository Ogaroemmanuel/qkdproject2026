from qiskit import QuantumCircuit

def create_bell_pair():
    """Generates the entangled Bell state |Φ+> between Alice (q0) and Bob (q1)."""
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    return qc