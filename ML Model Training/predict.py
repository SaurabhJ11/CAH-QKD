"""Interactive CLI for QKD protocol recommendation."""

from src.config import PLATFORM_DISPLAY, PLATFORM_SPECS
from src.inference import QKDPredictor


def main():
    print("\n+--------------------------------------------------------------+")
    print("|       QKD Protocol Recommendation System (MVP)             |")
    print("+--------------------------------------------------------------+\n")

    # ── Distance ─────────────────────────────────────────────────────────
    distance = float(input("Enter link distance (km, 5-250): "))

    # ── Platform ─────────────────────────────────────────────────────────
    platforms = list(PLATFORM_SPECS.keys())
    print("\nAvailable quantum hardware platforms:")
    for i, key in enumerate(platforms, 1):
        print(f"  {i}. {PLATFORM_DISPLAY[key]}  ({key})")
    choice = int(input("Select platform [1-4]: ")) - 1
    platform = platforms[choice]

    # ── Noise ────────────────────────────────────────────────────────────
    noise = float(input("\nEnvironmental noise factor (1.0=ideal ... 2.5=high): "))

    # ── Predict ──────────────────────────────────────────────────────────
    predictor = QKDPredictor()
    results = predictor.predict_top_protocols(distance, platform, noise, top_n=3)

    # ── Display ──────────────────────────────────────────────────────────
    specs = PLATFORM_SPECS[platform]
    print(f"\n--- Conditions ----------------------------------------------------")
    print(f"  Distance     : {distance} km")
    print(f"  Platform     : {PLATFORM_DISPLAY[platform]}")
    print(f"  Noise factor : {noise}")
    print(f"  1Q fidelity  : {specs['single_qubit_fidelity']}")
    print(f"  2Q fidelity  : {specs['two_qubit_fidelity']}")
    print(f"  T1 / T2      : {specs['T1']} / {specs['T2']} us")

    print(f"\n--- Top 3 Recommended Protocols ------------------------------------")
    for rank, r in enumerate(results, 1):
        print(f"  {rank}. {r['protocol']:<14s}  ->  Secure Key Rate = {r['secure_key_rate']:.6f}")
    print()


if __name__ == "__main__":
    main()
