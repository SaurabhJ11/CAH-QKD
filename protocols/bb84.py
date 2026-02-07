"""BB84 Protocol Implementation"""
from braket.circuits import Circuit
from braket.devices import LocalSimulator
import numpy as np

class BB84Protocol:
    def __init__(self, n_qubits=500):
        self.n_qubits = n_qubits
        self.protocol_name = "BB84"
    
    def create_circuit(self, bit, basis):
        """Create quantum circuit for encoding"""
        circuit = Circuit()
        
        if basis == 'Z':
            if bit == 1:
                circuit.x(0)
        elif basis == 'X':
            circuit.h(0)
            if bit == 1:
                circuit.z(0)
        
        return circuit
    
    def run_protocol(self, device, shots=1):
        """Execute BB84 protocol"""
        # Alice generates random bits and bases
        alice_bits = np.random.randint(0, 2, self.n_qubits)
        alice_bases = np.random.choice(['Z', 'X'], self.n_qubits)
        
        # Bob chooses random bases
        bob_bases = np.random.choice(['Z', 'X'], self.n_qubits)
        bob_results = []
        
        # Quantum transmission
        for i in range(self.n_qubits):
            circuit = self.create_circuit(alice_bits[i], alice_bases[i])
            
            # Bob's measurement
            if bob_bases[i] == 'X':
                circuit.h(0)
            circuit.measure(0)
            
            # Execute
            task = device.run(circuit, shots=shots)
            result = task.result()
            counts = result.measurement_counts
            bob_results.append(int(max(counts, key=counts.get)))
        
        return {
            'alice_bits': alice_bits,
            'alice_bases': alice_bases,
            'bob_bases': bob_bases,
            'bob_results': np.array(bob_results)
        }
    
    def post_processing(self, raw_data):
        """Basis reconciliation and QBER calculation"""
        alice_bits = raw_data['alice_bits']
        alice_bases = raw_data['alice_bases']
        bob_bases = raw_data['bob_bases']
        bob_results = raw_data['bob_results']
        
        # Basis reconciliation
        matching = alice_bases == bob_bases
        sifted_alice = alice_bits[matching]
        sifted_bob = bob_results[matching]
        
        sifted_length = len(sifted_alice)
        raw_key_rate = sifted_length / len(alice_bits)
        
        # Error estimation (10% sample)
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
        """Calculate secure key rate using GLLP bound"""
        if qber >= 0.11:
            return 0.0
        
        if 0 < qber < 1:
            h = lambda x: -x * np.log2(x) - (1-x) * np.log2(1-x) if x > 0 else 0
            secure_fraction = max(0, 1 - 2.2 * h(qber))
        else:
            secure_fraction = 1.0
        
        return raw_key_rate * secure_fraction