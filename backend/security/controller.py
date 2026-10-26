import random
from qiskit_aer import Aer
from backend.quantum.bell_pairs import create_bell_pair
from backend.quantum.superdense import encode_message, decode_message
from backend.quantum.channel import transmit_channel
from backend.security.qber import calculate_organic_qber

def run_simulation(key_size=16, eve_active=False, num_shots=1024):
    if key_size % 2 != 0: key_size += 1 
    
    sent_key = "".join([str(random.randint(0, 1)) for _ in range(key_size)])
    bob_final_key = ""
    total_errors = 0
    total_bits_simulated = key_size * num_shots
    
    simulator = Aer.get_backend('qasm_simulator')
    
    for i in range(0, key_size, 2):
        bit_pair = sent_key[i:i+2]
        
        qc = create_bell_pair()
        qc = encode_message(qc, bit_pair)
        qc = transmit_channel(qc, eve_active)
        qc = decode_message(qc)
        
        # NATIVE EXECUTION: Bypasses transpiler to prevent Qiskit from swapping qubits
        result = simulator.run(qc, shots=num_shots).result()
        counts = result.get_counts(qc)
        
        total_errors += calculate_organic_qber(counts, bit_pair)
        
        best_measurement = max(counts, key=counts.get)
        bob_final_key += best_measurement 

    qber_value = (total_errors / total_bits_simulated) * 100
    threshold = 11.0 
    
    return {
        "sent_key": sent_key,
        "received_key": bob_final_key,
        "qber_value": round(qber_value, 2),
        "threshold": threshold,
        "status": "Compromised" if qber_value > threshold else "Secure",
        "kill_switch_triggered": qber_value > threshold
    }
  
