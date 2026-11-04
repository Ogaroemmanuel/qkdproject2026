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
    pair_results = []
    
    simulator = Aer.get_backend('qasm_simulator')
    
    for i in range(0, key_size, 2):
        bit_pair = sent_key[i:i+2]
        
        qc = create_bell_pair()
        qc = encode_message(qc, bit_pair)
        qc = transmit_channel(qc, eve_active)
        qc = decode_message(qc)
        
        # Run the pedagogical circuit directly; normalize Qiskit's classical
        # bit-string display order before comparing or presenting the message.
        result = simulator.run(qc, shots=num_shots).result()
        counts = result.get_counts(qc)
        
        total_errors += calculate_organic_qber(counts, bit_pair)

        # Qiskit counts are displayed c1c0; convert them to the app's message
        # order (q0/q1) for the sample readout and the process visualization.
        decoded_counts = {outcome.replace(" ", "")[::-1]: count for outcome, count in counts.items()}
        sampled_outcome = random.choices(
            list(counts.keys()), weights=list(counts.values()), k=1
        )[0]
        received_pair = sampled_outcome.replace(" ", "")[::-1]
        bob_final_key += received_pair
        pair_results.append({
            "sent_bits": bit_pair,
            "received_bits": received_pair,
            "outcome_counts": decoded_counts,
        })

    qber_value = (total_errors / total_bits_simulated) * 100
    threshold = 11.0 
    
    return {
        "sent_key": sent_key,
        "received_key": bob_final_key,
        "pair_results": pair_results,
        "error_bits": total_errors,
        "total_bits": total_bits_simulated,
        "qber_value": round(qber_value, 2),
        "threshold": threshold,
        "status": "Compromised" if qber_value > threshold else "Secure",
        "kill_switch_triggered": qber_value > threshold
    }
  
