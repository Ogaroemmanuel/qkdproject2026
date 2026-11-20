def transmit_channel(qc, eve_active, noise_probability=0.0):
    """
    Models a memoryless Pauli-noise channel, not a calibrated physical fiber.
    If Eve taps the line, she measures Alice's traveling qubit (q0), collapsing the wave function.
    """
    if eve_active:
        qc.measure(0, 0)
        # Prevents Qiskit optimizer from deleting the mid-circuit measurement
        qc.barrier()
    if noise_probability:
        from qiskit_aer.noise import pauli_error
        p = float(noise_probability)
        if not 0 <= p <= 1:
            raise ValueError("Noise probability must lie between zero and one.")
        qc.append(pauli_error([('I', 1-p), ('X', p/3), ('Y', p/3), ('Z', p/3)]).to_instruction(), [0])
    return qc
