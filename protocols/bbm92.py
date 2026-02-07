import numpy as np
from protocols.e91 import E91Protocol

class BBM92Protocol(E91Protocol):
    def __init__(self, n_pairs=500):
        super().__init__(n_pairs)
        self.protocol_name = "BBM92"
        # BBM92 uses only two measurement angles
        self.alice_angles = [0, np.pi/4]
        self.bob_angles = [0, np.pi/4]