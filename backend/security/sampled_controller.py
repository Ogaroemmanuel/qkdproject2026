"""Sequential disturbance testing; this is not a QKD security proof."""
import math
import random
import secrets
from collections import Counter
from importlib.metadata import version
import platform

from qiskit_aer import AerSimulator
from backend.quantum.bell_pairs import create_bell_pair
from backend.quantum.superdense import encode_message, decode_message
from backend.quantum.channel import transmit_channel
from backend.quantum.state_trace import build_state_trace

MODEL_VERSION = "sampled-channel-v3"


def run_simulation(key_size=16, eve_active=False, num_shots=1024,
                   noise_probability=0.02, test_fraction=0.5,
                   error_limit=0.11, confidence=0.95, seed=None):
    for value, name, minimum in ((key_size, "Message length", 2), (num_shots, "Shots", 2)):
        if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
            raise ValueError(f"{name} must be an integer of at least {minimum}.")
    if key_size % 2:
        raise ValueError("Message length must be even.")
    for value, name in ((noise_probability, "Noise"), (error_limit, "Error limit")):
        if not math.isfinite(value) or not 0 <= value <= 1:
            raise ValueError(f"{name} must be between zero and one.")
    if not 0 < test_fraction < 1 or not 0 < confidence < 1:
        raise ValueError("Test fraction and confidence must be between zero and one, exclusively.")
    if not isinstance(eve_active, bool):
        raise ValueError("Eve setting must be boolean.")
    if seed is not None and (isinstance(seed, bool) or not isinstance(seed, int) or not 0 <= seed < 2**32):
        raise ValueError("Seed must be a 32-bit nonnegative integer.")
    seed = secrets.randbits(32) if seed is None else seed
    rng = random.Random(seed)  # Reproducible experiments, not cryptographic keys.
    planned_message = "".join(str(rng.randrange(2)) for _ in range(key_size))
    planned_batches = key_size // 2
    sample_shots = max(1, min(num_shots-1, int(num_shots * test_fraction)))
    simulator = AerSimulator(max_parallel_threads=1)
    pair_results, batches = [], []
    test_errors = total_errors = test_bits = total_bits = 0
    observed_message = ""
    lower, upper, rejected = 0.0, 1.0, False
    for index in range(planned_batches):
        bits = planned_message[index*2:index*2+2]
        # Select independently of outcomes; discard BOTH bits from each test shot.
        test_indices = set(rng.sample(range(num_shots), sample_shots))
        simulator_seed = rng.randrange(2**32)
        # Probes encode independent random bits. Disclosing repeated copies of
        # the payload itself would expose the very data supposedly retained.
        inputs = ["".join(str(rng.randrange(2)) for _ in range(2)) if i in test_indices else bits
                  for i in range(num_shots)]
        decoded = [None] * num_shots
        for symbol in sorted(set(inputs)):
            indices = [i for i, value in enumerate(inputs) if value == symbol]
            qc = decode_message(transmit_channel(encode_message(create_bell_pair(), symbol),
                                                  eve_active, noise_probability))
            memory = simulator.run(qc, shots=len(indices), memory=True,
                                   seed_simulator=(simulator_seed+int(symbol, 2)) % 2**32).result().get_memory()
            for i, out in zip(indices, memory):
                decoded[i] = out.replace(" ", "")[::-1]
        tests = {symbol: Counter(decoded[i] for i in test_indices if inputs[i] == symbol)
                 for symbol in sorted(set(inputs[i] for i in test_indices))}
        retained = Counter(out for i, out in enumerate(decoded) if i not in test_indices)
        def errors(counts, sent=bits):
            return sum(sum(a != b for a, b in zip(sent, out))*n for out, n in counts.items())
        batch_test_errors = sum(errors(counts, sent) for sent, counts in tests.items())
        test_errors += batch_test_errors
        test_bits += 2 * sample_shots
        total_errors += batch_test_errors + errors(retained)
        total_bits += 2 * num_shots
        observed_message += next(out for i, out in enumerate(decoded) if i not in test_indices)
        # Errors within a shot are correlated. Apply Hoeffding to bounded
        # per-shot error fractions, with a union bound over every planned look.
        n = (index+1) * sample_shots
        margin = math.sqrt(math.log(2*planned_batches/(1-confidence))/(2*n))
        estimate = test_errors / test_bits
        lower, upper = max(0.0, estimate-margin), min(1.0, estimate+margin)
        rejected = lower > error_limit
        batches.append({"batch": index+1, "test_error_bits": batch_test_errors,
                        "test_bits": 2*sample_shots, "estimate": estimate,
                        "lower_bound": lower, "upper_bound": upper,
                        "rejected": rejected, "simulator_seed": simulator_seed})
        pair_results.append({"sent_bits": bits, "received_bits": observed_message[-2:],
                             "encoding_operation": {"00":"I","01":"X","10":"Z","11":"Z → X"}[bits],
                             "outcome_counts": dict(retained),
                             "test_counts": {sent: dict(counts) for sent, counts in tests.items()},
                             "retained_counts": dict(retained),
                             "test_inputs": {str(i): inputs[i] for i in sorted(test_indices)},
                             "test_indices": sorted(test_indices),
                             "state_trace": build_state_trace(bits, eve_active, noise_probability) if index == 0 else None})
        if rejected:
            break  # Later message pairs never reach the simulator.
    status = "Rejected" if rejected else "Within limit" if upper <= error_limit else "Inconclusive"
    return {"model_version": MODEL_VERSION, "seed": seed,
            "runtime_versions": {"python": platform.python_version(), "qiskit": version("qiskit"),
                                 "qiskit-aer": version("qiskit-aer")},
            "expected_baseline_ber": 100 * 2 * noise_probability / 3,
            "configuration": {"key_size": key_size, "eve_active": eve_active,
                              "num_shots": num_shots, "noise_probability": noise_probability,
                              "test_fraction": test_fraction, "error_limit": error_limit,
                              "confidence": confidence},
            "planned_message": planned_message,
            "sent_key": planned_message[:len(observed_message)], "received_key": observed_message,
            "pair_results": pair_results, "batches": batches,
            "planned_batches": planned_batches, "completed_batches": len(batches),
            "untransmitted_bits": key_size - 2*len(batches),
            "error_bits": test_errors, "total_bits": test_bits,
            "qber_value": round(100*test_errors/test_bits, 4),
            "ground_truth_error_bits": total_errors, "ground_truth_total_bits": total_bits,
            "ground_truth_ber": 100*total_errors/total_bits,
            "confidence_interval": [100*lower, 100*upper],
            "threshold": error_limit*100, "status": status,
            "kill_switch_triggered": rejected,
            "payload_released": status == "Within limit"}
