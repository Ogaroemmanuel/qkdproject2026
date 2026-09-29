from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

def run_full_key_exchange(classical_key, eve_active=False):
    """
    Takes a full key (e.g., 8 or 16 bits), chunks it into 2-bit pairs,
    transmits each pair using Superdense Coding, and returns the full measured key.
    """
    # Split the incoming string into pairs of 2 bits (e.g., "1011" -> ["10", "11"])
    bit_pairs = [classical_key[i:i+2] for i in range(0, len(classical_key), 2)]
    measured_key = ""
    
    simulator = AerSimulator()

    for pair in bit_pairs:
        qc = QuantumCircuit(2, 2)
        
        # 1. GENERATE BELL PAIR
        qc.h(0)
        qc.cx(0, 1)
        
        # 2. ALICE'S ENCODING
        if pair == "01":
            qc.x(0)
        elif pair == "10":
            qc.z(0)
        elif pair == "11":
            qc.x(0)
            qc.z(0)
            
        # 3. MITM INTERCEPTION (Eve)
        if eve_active:
            # Eve intercepts Qubit 0 in transit and measures it.
            # This unauthorized observation collapses the entangled state.
            qc.measure(0, 0)
            
        # 4. BOB'S DECODING
        qc.cx(0, 1)
        qc.h(0)
        
        # 5. BOB'S MEASUREMENT
        qc.measure([0, 1], [0, 1])
        
        # 6. RUN SIMULATION
        job = simulator.run(qc, shots=1)
        result = job.result().get_counts()
        
        # Extract, reverse (due to Qiskit formatting), and append the result
        measured_pair = list(result.keys())[0][::-1]
        measured_key += measured_pair
        
    return measured_key

if __name__ == "__main__":
    # Test an 8-bit key sequence
    test_key_8 = "10110001"
    
    print("--- 8-Bit Key Transmission Simulation ---")
    
    # Scenario A: Safe Channel
    safe_result = run_full_key_exchange(test_key_8, eve_active=False)
    print(f"SAFE CHANNEL   | Sent: {test_key_8} -> Received: {safe_result}")
    
    # Scenario B: Attacked Channel
    attacked_result = run_full_key_exchange(test_key_8, eve_active=True)
    print(f"ATTACKED (EVE) | Sent: {test_key_8} -> Received: {attacked_result}")