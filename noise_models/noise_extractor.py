import json
import os

PLATFORM_SPECS = {
    'ionq_aria': {
        'name': 'IonQ Aria',
        'type': 'trapped_ion',
        'single_qubit_fidelity': 0.9995,
        'two_qubit_fidelity': 0.987,
        'T1': 10000,
        'T2': 1000,
        'depolarizing_1q': 0.0005,
        'depolarizing_2q': 0.013
    },
    'ionq_harmony': {
        'name': 'IonQ Harmony',
        'type': 'trapped_ion',
        'single_qubit_fidelity': 0.999,
        'two_qubit_fidelity': 0.975,
        'T1': 8000,
        'T2': 800,
        'depolarizing_1q': 0.001,
        'depolarizing_2q': 0.025
    },
    'rigetti_aspen_m3': {
        'name': 'Rigetti Aspen-M-3',
        'type': 'superconducting',
        'single_qubit_fidelity': 0.998,
        'two_qubit_fidelity': 0.952,
        'T1': 50,
        'T2': 30,
        'depolarizing_1q': 0.002,
        'depolarizing_2q': 0.048
    },
    'oqc_lucy': {
        'name': 'OQC Lucy',
        'type': 'superconducting',
        'single_qubit_fidelity': 0.997,
        'two_qubit_fidelity': 0.945,
        'T1': 45,
        'T2': 25,
        'depolarizing_1q': 0.003,
        'depolarizing_2q': 0.055
    }
}

def create_all_platform_noise_models():
    """Create noise models for all platforms"""
    print("\nCreating noise models...")
    
    for platform, specs in PLATFORM_SPECS.items():
        print(f"\n  {specs['name']}:")
        print(f"    Type: {specs['type']}")
        print(f"    f1q: {specs['single_qubit_fidelity']}")
        print(f"    f2q: {specs['two_qubit_fidelity']}")
        print(f"    T1: {specs['T1']} μs")
        
        
        filename = f'noise_models/{platform}_noise_model.json'
        with open(filename, 'w') as f:
            json.dump(specs, f, indent=2)
        print(f"    ✅ Saved: {filename}")
    
    print("\n✅ All noise models created!")

if __name__ == "__main__":
    create_all_platform_noise_models()