"""
Si28-Phonon QRNG Seed Generator (Lightweight Export Mode for DQI Optimizer)
"""
import os
import sys
import shutil
import numpy as np

def run_quiet_seed_generation():
    print("🚀 [Si28-QRNG Engine] Mode 2 Quantum Seed Generation Initialized...")
    
    # 1. si28_qrng 엔진 임포트 (예외 마스킹 해제)
    try:
        from si28_qrng import PhononQRNG
    except ImportError as e:
        print(f"❌ [Error] si28_qrng import failed: {e}")
        sys.exit(1)

    # 2. 양자 비트스트림 생성 (1,000,000 bits)
    qrng = PhononQRNG()
    raw_bits = qrng.generate_bits(length=1_000_000)
    print(f"✅ Generated Real Quantum Entropy: {len(raw_bits):,} bits")

    # 3. 로컬 data/ 폴더에 verified_si28_bits.npy 저장
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "verified_si28_bits.npy")
    np.save(output_path, raw_bits)
    print(f"📦 Archived Seed File: {output_path}")

    # 4. 상대 경로를 통한 qrng-dqi-optimizer 및 상위 data/ 폴더로 자동 전달
    target_dirs = [
        "../data",
        "../qrng-dqi-optimizer/data"
    ]
    
    transferred_count = 0
    for target in target_dirs:
        try:
            if os.path.exists(os.path.dirname(target)):
                os.makedirs(target, exist_ok=True)
                shutil.copy(output_path, os.path.join(target, "verified_si28_bits.npy"))
                print(f"   ↳ Auto-bound to target path: {target}")
                transferred_count += 1
        except Exception as err:
            pass

    print(f"✨ [Complete] Quantum Seed Binding Complete ({transferred_count} target locations updated).\n")

if __name__ == "__main__":
    run_quiet_seed_generation()
