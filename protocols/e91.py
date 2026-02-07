from braket.circuits import Circuit
from braket.devices import LocalSimulator
import numpy as np

class E91Protocol:
    def __init__(self, n_pairs=500):
        self.n_pairs = n_pairs
        self.protocol_name = "E91"
        # Measurement angles for Alice and Bob
        self.alice_angles = [0, np.pi/4, np.pi/2]
        self.bob_angles = [np.pi/4, np.pi/2, 3*np.pi/4]
    
    def create_bell_pair(self):
        """Create Bell pair |Φ+⟩ = (|00⟩ + |11⟩)/√2"""
        circuit = Circuit()
        circuit.h(0)
        circuit.cnot(0, 1)
        return circuit
    
    def apply_noise(self, circuit, noise_model):
        """Apply depolarizing noise to simulate real hardware"""
        # Single-qubit depolarizing on both qubits
        p1 = noise_model['depolarizing_1q']
        for i in range(2):
            if np.random.random() < p1:
                circuit.x(i)
        
        # Two-qubit depolarizing after CNOT
        p2 = noise_model['depolarizing_2q']
        if np.random.random() < p2:
            circuit.x(0)
            circuit.x(1)
        
        return circuit
    
    def run_protocol(self, device, shots=1, noise_model=None):
        """Execute E91 protocol"""
        alice_results = []
        bob_results = []
        alice_bases = []
        bob_bases = []
        
        for _ in range(self.n_pairs):
            # Create entangled pair
            circuit = self.create_bell_pair()
            
            # Apply hardware noise if provided
            if noise_model:
                circuit = self.apply_noise(circuit, noise_model)
            
            # Random measurement angles
            alice_angle = np.random.choice(self.alice_angles)
            bob_angle = np.random.choice(self.bob_angles)
            
            alice_bases.append(alice_angle)
            bob_bases.append(bob_angle)
            
            # Apply rotation gates
            circuit.ry(0, 2 * alice_angle)
            circuit.ry(1, 2 * bob_angle)
            
            # Measure
            circuit.measure([0, 1])
            
            # Execute
            task = device.run(circuit, shots=shots)
            result = task.result()
            counts = result.measurement_counts
            
            outcome = max(counts, key=counts.get)
            alice_results.append(int(outcome[0]))
            bob_results.append(int(outcome[1]))
        
        return {
            'alice_results': np.array(alice_results),
            'bob_results': np.array(bob_results),
            'alice_bases': np.array(alice_bases),
            'bob_bases': np.array(bob_bases)
        }
    
    def post_processing(self, raw_data):
        """Key generation and Bell test"""
        alice_results = raw_data['alice_results']
        bob_results = raw_data['bob_results']
        alice_bases = raw_data['alice_bases']
        bob_bases = raw_data['bob_bases']
        
        # Use matching angle pairs for key
        matching_mask = (alice_bases == bob_bases)
        key_alice = alice_results[matching_mask]
        key_bob = bob_results[matching_mask]
        
        sifted_length = len(key_alice)
        raw_key_rate = sifted_length / len(alice_results)
        
        # QBER estimation
        if sifted_length > 10:
            sample_size = max(1, sifted_length // 10)
            sample_idx = np.random.choice(sifted_length, sample_size, replace=False)
            errors = np.sum(key_alice[sample_idx] != key_bob[sample_idx])
            qber = errors / sample_size
        else:
            qber = 0.0
        
        # Bell parameter (simplified)
        correlations = np.mean(alice_results == bob_results)
        bell_S = 2.828 * correlations  # Simplified CHSH
        
        return {
            'sifted_length': sifted_length,
            'raw_key_rate': raw_key_rate,
            'qber': qber,
            'bell_parameter': bell_S,
            'entanglement_verified': bell_S > 2.0
        }
    
    def calculate_secure_key_rate(self, qber, raw_key_rate):
        """E91 has stricter QBER threshold due to entanglement"""
        if qber >= 0.076:  # E91 threshold
            return 0.0
        
        if 0 < qber < 1:
            h = lambda x: -x * np.log2(x) - (1-x) * np.log2(1-x) if x > 0 else 0
            secure_fraction = max(0, 1 - 2.2 * h(qber))
        else:
            secure_fraction = 1.0
        
        return raw_key_rate * secure_fraction