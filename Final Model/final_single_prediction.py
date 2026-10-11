from predict import predict_single

architectures = ['IonQ Aria', 'IonQ Harmony', 'Rigetti Aspen-M-3', 'OQC Lucy']
distances     = [50, 100, 150, 200]
noise_levels  = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]

print(f"{'Architecture':<20} {'Distance':>10} {'Noise':>8} {'#1 Protocol':<15} {'Key Rate':>10} {'Transmission':>14}")
print("-" * 80)

for arch in architectures:
    for dist in distances:
        for noise in noise_levels:
            try:
                results = predict_single(arch, dist, noise, verbose=False)
                if results:
                    top = results[0]
                    print(f"{arch:<20} {dist:>10} {noise:>8.1f} {top['protocol']:<15} {top['secure_key_rate']:>10.4f} {top['transmission']:>14.4f}")
            except Exception as e:
                print(f"ERROR — {arch}, {dist}km, noise={noise}: {e}")