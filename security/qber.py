def calculate_qber(sent_bits, received_bits):
    """
    Calculates the Quantum Bit Error Rate (QBER).
    Formula: (Number of error bits / Total number of transmitted bits) * 100
    """
    # Ensure both strings are the same length before comparing
    if len(sent_bits) != len(received_bits):
        raise ValueError("Sent and received bit strings must be of equal length.")
        
    total_bits = len(sent_bits)
    
    # Zip pairs up the bits (e.g., sent[0] with received[0]) so we can compare them
    error_count = sum(1 for s, r in zip(sent_bits, received_bits) if s != r)
    
    # Calculate percentage
    qber_percentage = (error_count / total_bits) * 100.0
    
    return qber_percentage, error_count, total_bits

# Test the function using the exact output from your terminal
if __name__ == "__main__":
    test_sent = "10110001"
    test_received = "00110001"
    
    qber, errors, total = calculate_qber(test_sent, test_received)
    
    print("--- QBER Calculation Test ---")
    print(f"Sent:     {test_sent}")
    print(f"Received: {test_received}")
    print(f"Errors Detected: {errors} out of {total} bits")
    print(f"Calculated QBER: {qber}%")