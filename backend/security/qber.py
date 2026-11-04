def calculate_organic_qber(counts, original_pair):
    """Count decoded message-bit errors over all shots.

    Qiskit formats a two-bit counts key as ``c1c0`` (bit 0 is rightmost),
    while this app presents the encoded message as ``bit0bit1``. Normalize
    that display order before comparing the result with Alice's message.
    """
    total_bit_errors = 0
    for measured_state, count in counts.items():
        decoded_pair = measured_state.replace(" ", "")[::-1]
        bit_errors = sum(1 for sent, received in zip(original_pair, decoded_pair) if sent != received)
        total_bit_errors += bit_errors * count
            
    return total_bit_errors
