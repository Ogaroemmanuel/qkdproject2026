def calculate_organic_qber(counts, original_pair):
    """
    Analyzes the probability distribution of all Qiskit shots directly.
    """
    total_bit_errors = 0
    for measured_state, count in counts.items():
        if measured_state != original_pair:
            # Count how many individual bits are wrong in this pair
            bit_errors = sum(1 for a, b in zip(original_pair, measured_state) if a != b)
            total_bit_errors += bit_errors * count
            
    return total_bit_errors