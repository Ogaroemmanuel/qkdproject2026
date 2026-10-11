def encode_message(qc, bit_pair):
    """Alice applies Pauli gates to her entangled qubit (q0) to encode 2 classical bits."""
    if bit_pair == "01":
        qc.z(0)
    elif bit_pair == "10":
        qc.x(0)
    elif bit_pair == "11":
        qc.z(0)
        qc.x(0)
    # "00" requires no operation (Identity)
    return qc

def decode_message(qc):
    """Bob applies the reverse Bell measurement on both qubits to extract the 2 bits."""
    qc.cx(0, 1)
    qc.h(0)
    qc.measure([0, 1], [0, 1])
    return qc