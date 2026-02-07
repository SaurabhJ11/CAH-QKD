from protocols.bb84 import BB84Protocol
import numpy as np

class SARG04Protocol(BB84Protocol):
    def __init__(self, n_qubits=500):
        super().__init__(n_qubits)
        self.protocol_name = "SARG04"
    
    def calculate_secure_key_rate(self, qber, raw_key_rate):
        """SARG04 is more resistant to noise"""
        if qber >= 0.146:  # Higher threshold than BB84
            return 0.0
        
        if 0 < qber < 1:
            h = lambda x: -x * np.log2(x) - (1-x) * np.log2(1-x) if x > 0 else 0
            secure_fraction = max(0, 1 - 2.2 * h(qber))
        else:
            secure_fraction = 1.0
        
        return raw_key_rate * secure_fraction * 0.85  # SARG04 penalty