from protocols.bb84 import BB84Protocol
import numpy as np

class DecoyBB84Protocol(BB84Protocol):
    def __init__(self, n_qubits=500):
        super().__init__(n_qubits)
        self.protocol_name = "Decoy-BB84"
        self.signal_intensity = 0.5
        self.decoy_intensity = 0.1
    
    def calculate_secure_key_rate(self, qber, raw_key_rate):
        """Decoy states improve long-distance performance"""
        if qber >= 0.11:
            return 0.0
        
        if 0 < qber < 1:
            h = lambda x: -x * np.log2(x) - (1-x) * np.log2(1-x) if x > 0 else 0
            secure_fraction = max(0, 1 - 2.2 * h(qber))
        else:
            secure_fraction = 1.0
        
        # Decoy states give advantage at long distances
        return raw_key_rate * secure_fraction * 1.1  # 10% boost