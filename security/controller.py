import random
from quantum.superdense import run_full_key_exchange
from security.qber import calculate_qber

def run_simulation(key_size, eve_active):
    """
    Acts as the Sim Controller.
    Orchestrates key generation, transmission, QBER calculation, and threshold decision.
    """
    # 1. Generate a random classical key of the requested size (e.g., 8 or 16 bits)
    sent_key = "".join(str(random.randint(0, 1)) for _ in range(key_size))
    
    # 2. Transmit the key through the quantum channel
    received_key = run_full_key_exchange(sent_key, eve_active=eve_active)
    
    # 3. Calculate QBER
    qber_value, errors, total_bits = calculate_qber(sent_key, received_key)
    
    # 4. Compare against the 11% safety threshold
    threshold = 11.0
    kill_switch_triggered = qber_value > threshold
    
    # 5. Determine Final Status
    if kill_switch_triggered:
        status = "Automated Connection Kill-Switch (Alert Triggered)"
    else:
        status = "Validated Hybrid Key Handshake (Success)"
        
    # Return a dictionary containing all data needed for logging and the dashboard
    return {
        "sent_key": sent_key,
        "received_key": received_key,
        "qber_value": qber_value,
        "threshold": threshold,
        "status": status,
        "kill_switch_triggered": kill_switch_triggered
    }

# Test the Controller Module
if __name__ == "__main__":
    print("--- Testing Sim Controller ---")
    
    print("\nScenario 1: Safe 16-bit Key Exchange")
    safe_run = run_simulation(key_size=16, eve_active=False)
    print(f"Sent:     {safe_run['sent_key']}")
    print(f"Received: {safe_run['received_key']}")
    print(f"QBER:     {safe_run['qber_value']}%")
    print(f"Status:   {safe_run['status']}")
    
    print("\nScenario 2: Attacked 16-bit Key Exchange")
    attacked_run = run_simulation(key_size=16, eve_active=True)
    print(f"Sent:     {attacked_run['sent_key']}")
    print(f"Received: {attacked_run['received_key']}")
    print(f"QBER:     {attacked_run['qber_value']}%")
    print(f"Status:   {attacked_run['status']}")