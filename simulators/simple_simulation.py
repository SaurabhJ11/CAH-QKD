"""
FINAL QKD SIMULATION - Optimized Distance Ranges
Fair comparison: Same chips, same distances for ALL protocols
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from protocols.bb84 import BB84Protocol
from protocols.e91 import E91Protocol
from protocols.b92 import B92Protocol
from protocols.six_state import SixStateProtocol
from protocols.bbm92 import BBM92Protocol
from protocols.sarg04 import SARG04Protocol
from protocols.decoy_bb84 import DecoyBB84Protocol

from braket.devices import LocalSimulator
import numpy as np
import pandas as pd
import json
from datetime import datetime
import hashlib

# ============================================================================
# FIXED PARAMETERS - IDENTICAL FOR ALL PROTOCOLS
# ============================================================================
FIXED_N_QUBITS = 500
FIXED_N_PAIRS = 500

# DISTANCE CATEGORIES (km) - SAME FOR ALL PROTOCOLS & CHIPS
DISTANCE_CATEGORIES = {
    'extremely_near': [5, 10],           # 0-10 km: Urban/Campus
    'very_near': [15, 20, 25, 30],       # 10-30 km: Metropolitan
    'near': [40, 50, 60],                # 30-60 km: City-to-city
    'medium': [75, 90, 100],             # 60-100 km: Regional
    'far': [120, 140, 150],              # 100-150 km: Long-haul
    'very_far': [170, 180, 200],         # 150-200 km: Extreme range
    'extremely_far': [220, 250]          # 200+ km: Theoretical limit
}

# Flatten to single list
ALL_DISTANCES = []
for category, dists in DISTANCE_CATEGORIES.items():
    ALL_DISTANCES.extend(dists)

# QUANTUM PLATFORMS - SAME FOR ALL PROTOCOLS
ALL_PLATFORMS = ['ionq_aria', 'ionq_harmony', 'rigetti_aspen_m3', 'oqc_lucy']

# ============================================================================

def load_noise_model(platform):
    """Load chip-specific noise parameters"""
    with open(f'noise_models/{platform}_noise_model.json', 'r') as f:
        return json.load(f)

def calculate_channel_qber(distance_km):
    """Calculate QBER from channel loss (0.2 dB/km fiber)"""
    loss_db = 0.2 * distance_km
    transmission = 10 ** (-loss_db / 10)
    channel_qber = (1 - transmission) * 0.01
    return channel_qber, transmission

def categorize_distance(distance_km):
    """Return distance category for a given distance"""
    for category, distances in DISTANCE_CATEGORIES.items():
        if distance_km in distances:
            return category
    return 'unknown'

def generate_config_id(protocol_name, platform, distance, noise_factor, run_num):
    """Generate unique ID for each configuration"""
    config_str = f"{protocol_name}_{platform}_{distance}_{noise_factor}_{run_num}"
    return hashlib.md5(config_str.encode()).hexdigest()[:12]

def load_completed_configs(csv_file):
    """Load already completed configuration IDs"""
    if os.path.exists(csv_file):
        try:
            df = pd.read_csv(csv_file)
            if 'config_id' in df.columns:
                return set(df['config_id'].values)
        except:
            pass
    return set()

def simulate_protocol(protocol_class, protocol_name, platform, distance, noise_factor, run_num):
    """
    Run single simulation with IDENTICAL CONDITIONS
    - Fixed qubits: 500 for ALL protocols
    - Fixed chip: same for this run
    - Fixed distance: same for this run
    """
    device = LocalSimulator()
    noise_model = load_noise_model(platform)
    
    channel_qber, transmission = calculate_channel_qber(distance)
    
    # ALL PROTOCOLS USE SAME QUBIT/PAIR COUNT
    if protocol_name in ["E91", "BBM92"]:
        protocol = protocol_class(n_pairs=FIXED_N_PAIRS)
        raw_data = protocol.run_protocol(device, shots=1, noise_model=noise_model)
    else:
        protocol = protocol_class(n_qubits=FIXED_N_QUBITS)
        if protocol_name in ["B92", "Six-State"]:
            raw_data = protocol.run_protocol(device, shots=1, noise_model=noise_model)
        else:
            raw_data = protocol.run_protocol(device, shots=1)
    
    processed = protocol.post_processing(raw_data)
    base_qber = processed['qber']
    
    hw_noise = (1 - noise_model['single_qubit_fidelity']) * noise_factor
    total_qber = min(0.5, base_qber + hw_noise + channel_qber)
    
    secure_key_rate = protocol.calculate_secure_key_rate(total_qber, processed['raw_key_rate'])
    
    effective_key_bits = processed['sifted_length'] * transmission
    effective_secure_bits = effective_key_bits * (secure_key_rate / processed['raw_key_rate']) if processed['raw_key_rate'] > 0 else 0
    
    config_id = generate_config_id(protocol_name, platform, distance, noise_factor, run_num)
    
    result = {
        'config_id': config_id,
        'protocol': protocol_name,
        'platform': platform,
        'platform_type': noise_model['type'],
        'distance_km': distance,
        'distance_category': categorize_distance(distance),
        'noise_factor': noise_factor,
        'run': run_num,
        'timestamp': datetime.now().isoformat(),
        
        # FIXED CONDITIONS
        'n_qubits': FIXED_N_QUBITS if protocol_name not in ["E91", "BBM92"] else FIXED_N_PAIRS,
        'protocol_type': 'entanglement' if protocol_name in ["E91", "BBM92"] else 'prepare-measure',
        
        # Channel
        'transmission': transmission,
        'channel_loss_db': 0.2 * distance,
        
        # Performance
        'sifted_length': processed['sifted_length'],
        'raw_key_rate': processed['raw_key_rate'],
        'secure_key_rate': secure_key_rate,
        'effective_key_bits': effective_key_bits,
        'effective_secure_bits': effective_secure_bits,
        
        # QBER breakdown
        'qber_base': base_qber,
        'qber_hardware': hw_noise,
        'qber_channel': channel_qber,
        'qber_total': total_qber,
        
        # Platform specs
        'single_qubit_fidelity': noise_model['single_qubit_fidelity'],
        'two_qubit_fidelity': noise_model['two_qubit_fidelity'],
        'T1': noise_model['T1'],
        'T2': noise_model['T2'],
        'readout_fidelity': noise_model['readout_fidelity'],
        'depolarizing_1q': noise_model['depolarizing_1q'],
        'depolarizing_2q': noise_model['depolarizing_2q'],
        'calibration_method': 'published_specs'
    }
    
    if protocol_name in ["E91", "BBM92"]:
        result['bell_parameter'] = processed.get('bell_parameter', 0)
        result['entanglement_verified'] = processed.get('entanglement_verified', False)
    
    return result

def append_to_csv(result, csv_file):
    """Append single result to CSV immediately"""
    df_new = pd.DataFrame([result])
    
    if os.path.exists(csv_file):
        df_new.to_csv(csv_file, mode='a', header=False, index=False)
    else:
        df_new.to_csv(csv_file, mode='w', header=True, index=False)

def print_configuration_table():
    """Print detailed configuration table"""
    print("\n" + "="*80)
    print(" "*25 + "CONFIGURATION SUMMARY")
    print("="*80)
    
    print(f"\n🔧 Fixed Parameters (SAME for ALL protocols):")
    print(f"  • Qubits/Pairs: {FIXED_N_QUBITS}")
    print(f"  • Platforms: {len(ALL_PLATFORMS)}")
    print(f"  • Distance points: {len(ALL_DISTANCES)}")
    
    print(f"\n🌍 Distance Categories:")
    total_distances = 0
    for category, distances in DISTANCE_CATEGORIES.items():
        print(f"  • {category:20s}: {distances} ({len(distances)} points)")
        total_distances += len(distances)
    print(f"  {'='*40}")
    print(f"  Total distance points: {total_distances}")
    
    print(f"\n💻 Quantum Platforms (SAME for all protocols):")
    for i, platform in enumerate(ALL_PLATFORMS, 1):
        nm = load_noise_model(platform)
        print(f"  {i}. {nm['name']:25s} ({nm['type']:15s}) f1q={nm['single_qubit_fidelity']:.4f}, f2q={nm['two_qubit_fidelity']:.3f}")
    
    print("="*80)

def main():
    print("\n" + "="*80)
    print(" "*20 + "FINAL QKD SIMULATION")
    print(" "*10 + "Fair Comparison: Same Chips, Same Distances")
    print("="*80)
    
    protocols = [
        (BB84Protocol, "BB84"),
        (E91Protocol, "E91"),
        (B92Protocol, "B92"),
        (SixStateProtocol, "Six-State"),
        (BBM92Protocol, "BBM92"),
        (SARG04Protocol, "SARG04"),
        (DecoyBB84Protocol, "Decoy-BB84")
    ]
    
    noise_factors = [1.0, 1.2, 1.5, 2.0, 2.5]
    n_runs = 10
    
    total_configs = len(protocols) * len(ALL_PLATFORMS) * len(ALL_DISTANCES) * len(noise_factors) * n_runs
    
    print_configuration_table()
    
    print(f"\n📊 Simulation Scale:")
    print(f"  Protocols: {len(protocols)}")
    print(f"  Platforms: {len(ALL_PLATFORMS)} (same for all)")
    print(f"  Distances: {len(ALL_DISTANCES)} (same for all)")
    print(f"  Noise levels: {len(noise_factors)}")
    print(f"  Runs per config: {n_runs}")
    print(f"\n  ⭐ Total samples: {total_configs:,}")
    print(f"  ⏱️  Estimated time: {total_configs * 0.5 / 60:.1f} minutes (~{total_configs * 0.5 / 3600:.1f} hours)")
    
    os.makedirs('data', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_file = f'data/qkd_final_{timestamp}.csv'
    
    completed_configs = load_completed_configs(csv_file)
    
    if completed_configs:
        print(f"\n💾 Resuming: {len(completed_configs):,} completed")
    else:
        print(f"\n🆕 Starting fresh: {csv_file}")
    
    print("\n" + "-"*80)
    print("Starting simulation...\n")
    
    count = 0
    completed_count = len(completed_configs)
    last_progress = 0
    
    try:
        for protocol_class, protocol_name in protocols:
            for platform in ALL_PLATFORMS:
                for distance in ALL_DISTANCES:
                    for noise_factor in noise_factors:
                        for run in range(n_runs):
                            count += 1
                            config_id = generate_config_id(protocol_name, platform, distance, noise_factor, run)
                            
                            if config_id in completed_configs:
                                continue
                            
                            completed_count += 1
                            progress = int(completed_count / total_configs * 100)
                            
                            if progress != last_progress and progress % 5 == 0:
                                category = categorize_distance(distance)
                                print(f"  [{completed_count:5d}/{total_configs:5d}] {progress:3d}% | "
                                      f"{protocol_name:12s} | {platform:20s} | {distance:3d}km ({category})")
                                last_progress = progress
                            
                            result = simulate_protocol(
                                protocol_class, protocol_name,
                                platform, distance, noise_factor, run
                            )
                            
                            append_to_csv(result, csv_file)
                            completed_configs.add(config_id)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted!")
        print(f"✅ Saved: {completed_count:,}/{total_configs:,}")
        print(f"💾 File: {csv_file}")
        return
    
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        print(f"✅ Saved: {completed_count:,}")
        print(f"💾 File: {csv_file}")
        import traceback
        traceback.print_exc()
        return
    
    df = pd.read_csv(csv_file)
    
    print("\n" + "="*80)
    print(" "*30 + "✅ COMPLETE!")
    print("="*80)
    print(f"\n📁 Dataset: {csv_file}")
    print(f"  Size: {os.path.getsize(csv_file) / (1024*1024):.2f} MB")
    print(f"  Rows: {len(df):,}")
    
    print(f"\n📊 Fair Comparison Verified:")
    print(f"  ✅ All protocols: {df['protocol'].nunique()} protocols")
    print(f"  ✅ All platforms: {df['platform'].nunique()} platforms")
    print(f"  ✅ All distances: {df['distance_km'].nunique()} points ({df['distance_km'].min():.0f}-{df['distance_km'].max():.0f} km)")
    print(f"  ✅ All use {FIXED_N_QUBITS} qubits/pairs")
    
    print(f"\n🏆 Top 3 Protocols (by avg secure key rate):")
    top_protocols = df.groupby('protocol')['secure_key_rate'].mean().sort_values(ascending=False).head(3)
    for i, (protocol, rate) in enumerate(top_protocols.items(), 1):
        print(f"  {i}. {protocol:12s}: {rate:.4f}")
    
    print(f"\n🏆 Top 3 Platforms (by avg secure key rate):")
    top_platforms = df.groupby('platform')['secure_key_rate'].mean().sort_values(ascending=False).head(3)
    for i, (platform, rate) in enumerate(top_platforms.items(), 1):
        print(f"  {i}. {platform:20s}: {rate:.4f}")
    
    print(f"\n📈 By Distance Category:")
    category_perf = df.groupby('distance_category')['secure_key_rate'].mean().sort_values(ascending=False)
    for category, rate in category_perf.items():
        print(f"  {category:20s}: {rate:.4f}")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
