from braket.circuits import Circuit
from braket.devices import LocalSimulator
import numpy as np

class B92Protocol:
    def __init__(self, n_qubits=500):
        self.n_qubits = n_qubits
        self.protocol_name = "B92"
    
    def create_circuit(self, bit):
        """B92 uses only two non-orthogonal states"""
        circuit = Circuit()
        if bit == 0:
            # |0⟩ state - do nothing
            pass
        else:
            # |+⟩ = H|0⟩
            circuit.h(0)
        return circuit
    
    def apply_noise(self, circuit, noise_model):
        """Apply single-qubit depolarizing noise"""
        p = noise_model['depolarizing_1q']
        if np.random.random() < p:
            circuit.x(0)
        return circuit
    
    def run_protocol(self, device, shots=1, noise_model=None):
        """Execute B92 protocol"""
        alice_bits = np.random.randint(0, 2, self.n_qubits)
        bob_results = []
        bob_bases = []
        
        for i in range(self.n_qubits):
            circuit = self.create_circuit(alice_bits[i])
            
            # Apply hardware noise
            if noise_model:
                circuit = self.apply_noise(circuit, noise_model)
            
            # Bob randomly measures in Z or X basis
            bob_basis = np.random.choice([0, 1])  # 0=Z, 1=X
            bob_bases.append(bob_basis)
            
            if bob_basis == 1:  # X basis
                circuit.h(0)
            
            circuit.measure(0)
            
            task = device.run(circuit, shots=shots)
            result = task.result()
            counts = result.measurement_counts
            bob_results.append(int(max(counts, key=counts.get)))
        
        return {
            'alice_bits': alice_bits,
            'bob_results': np.array(bob_results),
            'bob_bases': np.array(bob_bases)
        }
    
    def post_processing(self, raw_data):
        """B92 sifting logic"""
        alice_bits = raw_data['alice_bits']
        bob_results = raw_data['bob_results']
        bob_bases = raw_data['bob_bases']
        
        # Keep only when: (alice=0, bob_basis=0, result=0) or (alice=1, bob_basis=1, result=1)
        keep_mask = ((alice_bits == 0) & (bob_bases == 0) & (bob_results == 0)) | \
                    ((alice_bits == 1) & (bob_bases == 1) & (bob_results == 1))
        
        sifted_alice = alice_bits[keep_mask]
        sifted_bob = bob_results[keep_mask]
        
        sifted_length = len(sifted_alice)
        raw_key_rate = sifted_length / len(alice_bits)
        
        # QBER
        if sifted_length > 10:
            sample_size = max(1, sifted_length // 10)
            sample_idx = np.random.choice(sifted_length, sample_size, replace=False)
            errors = np.sum(sifted_alice[sample_idx] != sifted_bob[sample_idx])
            qber = errors / sample_size
        else:
            qber = 0.0
        
        return {
            'sifted_length': sifted_length,
            'raw_key_rate': raw_key_rate,
            'qber': qber
        }
    
    def calculate_secure_key_rate(self, qber, raw_key_rate):
        """B92 secure key rate"""
        if qber >= 0.15:  # B92 is more noise-sensitive
            return 0.0
        
        if 0 < qber < 1:
            h = lambda x: -x * np.log2(x) - (1-x) * np.log2(1-x) if x > 0 else 0
            secure_fraction = max(0, 1 - 2.2 * h(qber))
        else:
            secure_fraction = 1.0
        
        return raw_key_rate * secure_fraction