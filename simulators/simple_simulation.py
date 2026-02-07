"""Comprehensive QKD Simulation"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from protocols.bb84 import BB84Protocol
from braket.devices import LocalSimulator
import numpy as np
import pandas as pd
import json
from datetime import datetime

def load_noise_model(platform):
    """Load platform noise specifications"""
    with open(f'noise_models/{platform}_noise_model.json', 'r') as f:
        return json.load(f)

def calculate_channel_loss(distance_km):
    """Fiber optic loss (0.2 dB/km)"""
    loss_db = 0.2 * distance_km
    transmission = 10 ** (-loss_db / 10)
    return transmission

def simulate_one_config(platform, distance, noise_factor, run_num):
    """Run single simulation configuration"""
    device = LocalSimulator()
    noise_model = load_noise_model(platform)
    
    # Channel loss
    transmission = calculate_channel_loss(distance)
    effective_qubits = max(10, int(500 * transmission))
    
    # Run BB84
    bb84 = BB84Protocol(n_qubits=effective_qubits)
    raw_data = bb84.run_protocol(device, shots=1)
    processed = bb84.post_processing(raw_data)
    
    # Add hardware noise
    base_qber = processed['qber']
    hw_noise = (1 - noise_model['single_qubit_fidelity']) * noise_factor
    total_qber = min(0.5, base_qber + hw_noise)
    
    # Calculate secure key rate
    secure_key_rate = bb84.calculate_secure_key_rate(total_qber, processed['raw_key_rate'])
    
    return {
        'protocol': 'BB84',
        'platform': platform,
        'platform_type': noise_model['type'],
        'distance_km': distance,
        'noise_factor': noise_factor,
        'run': run_num,
        'transmission': transmission,
        'effective_qubits': effective_qubits,
        'sifted_length': processed['sifted_length'],
        'raw_key_rate': processed['raw_key_rate'],
        'qber': total_qber,
        'secure_key_rate': secure_key_rate,
        'single_qubit_fidelity': noise_model['single_qubit_fidelity'],
        'two_qubit_fidelity': noise_model['two_qubit_fidelity'],
        'T1': noise_model['T1'],
        'T2': noise_model['T2']
    }

def main():
    print("\n" + "="*70)
    print(" "*20 + "QKD SIMULATION")
    print("="*70)
    
    # Parameters
    platforms = ['ionq_aria', 'ionq_harmony', 'rigetti_aspen_m3', 'oqc_lucy']
    distances = [10, 20, 30, 50, 75, 100, 150, 200]
    noise_factors = [1.0, 1.5, 2.0]
    n_runs = 5
    
    total = len(platforms) * len(distances) * len(noise_factors) * n_runs
    
    print(f"\n📊 Configuration:")
    print(f"  Protocols: BB84")
    print(f"  Platforms: {len(platforms)}")
    print(f"  Distances: {len(distances)}")
    print(f"  Noise levels: {len(noise_factors)}")
    print(f"  Runs per config: {n_runs}")
    print(f"\n  Total simulations: {total}")
    print(f"  Estimated time: {total * 0.5 / 60:.1f} minutes")
    
    print("\n" + "-"*70)
    print("Starting simulation...\n")
    
    results = []
    count = 0
    
    for platform in platforms:
        for distance in distances:
            for noise_factor in noise_factors:
                for run in range(n_runs):
                    count += 1
                    
                    if count % 20 == 0 or count == 1:
                        progress = count / total * 100
                        print(f"  [{count:3d}/{total}] {progress:5.1f}% | {platform} @ {distance}km")
                    
                    result = simulate_one_config(platform, distance, noise_factor, run)
                    results.append(result)
    
    # Save results
    df = pd.DataFrame(results)
    os.makedirs('data', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'data/simulation_{timestamp}.csv'
    df.to_csv(filename, index=False)
    
    # Summary statistics
    print("\n" + "="*70)
    print(" "*25 + "✅ COMPLETE!")
    print("="*70)
    print(f"\n📁 Results saved: {filename}")
    print(f"📊 Total samples: {len(df):,}")
    
    print(f"\n📈 Summary Statistics:")
    print(f"  Average QBER: {df['qber'].mean():.3%}")
    print(f"  Average Secure Key Rate: {df['secure_key_rate'].mean():.4f}")
    print(f"  Average Raw Key Rate: {df['raw_key_rate'].mean():.4f}")
    
    print(f"\n🏆 Best Performance:")
    best_platform = df.groupby('platform')['secure_key_rate'].mean().idxmax()
    best_rate = df.groupby('platform')['secure_key_rate'].mean().max()
    print(f"  Platform: {best_platform} ({best_rate:.4f})")
    
    max_dist = df[df['qber'] < 0.11]['distance_km'].max()
    print(f"  Max Distance (QBER<11%): {max_dist:.0f} km")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()