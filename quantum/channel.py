def transmit_channel(qc, eve_active):
    """
    Simulates the physical fiber channel. 
    If Eve taps the line, she measures Alice's traveling qubit (q0), collapsing the wave function.
    """
    if eve_active:
        qc.measure(0, 0)
        # Prevents Qiskit optimizer from deleting the mid-circuit measurement
        qc.barrier() 
    return qc