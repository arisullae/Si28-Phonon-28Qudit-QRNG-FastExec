"""
Si28-Phonon QRNG Seed Generator (Export & README Sync Mode)
"""
import os
import sys
import shutil
import re
import numpy as np

def update_readme_sample_bits(raw_bits, readme_path="README.md", sample_size=1000):
    """README.md 내의 1,000개 예시 난수 텍스트를 최신 양자 비트로 자동 교체"""
    if not os.path.exists(readme_path):
        return

    try:
        sample_bits = raw_bits[:sample_size].tolist()
        formatted_sample = f"<!-- QUANTUM_SEED_START -->\n```python\n# Daily Verified Si28 Quantum Entropy Sample (First 1,000 bits)\nSI28_QUANTUM_SEED_SAMPLE = {sample_bits}\n```\n<!-- QUANTUM_SEED_END -->"

        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 주석 태그(QUANTUM_SEED_START ~ END) 기준 자동 교체
        pattern = r"<!-- QUANTUM_SEED_START -->.*?<!-- QUANTUM_SEED_END -->"
        if re.search(pattern, content, flags=re.DOTALL):
            new_content = re.sub(pattern, formatted_sample, content, flags=re.DOTALL)
        else:
            new_content = content + f"\n\n## ⚛️ Daily Quantum Seed Sample (1,000 Bits)\n{formatted_sample}\n"

        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("📝 [Sync] README.md 1,000-bit sample updated successfully.")
    except Exception as err:
        print(f"⚠️ [Warning] README update skipped: {err}")

def run_seed_generation():
    print("🚀 [Si28-QRNG Engine] Quantum Seed Generation & Sync Initialized...")
    
    try:
        from si28_qrng import PhononQRNG
    except ImportError as e:
        print(f"❌ [Error] si28_qrng import failed: {e}")
        sys.exit(1)

    # 1. 1,000,000 비트 양자 엔트로피 생성
    qrng = PhononQRNG()
    raw_bits = qrng.generate_bits(length=1_000_000)
    print(f"✅ Generated Real Quantum Entropy: {len(raw_bits):,} bits")

    # 2. data/verified_si28_bits.npy 바이너리 아카이빙
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "verified_si28_bits.npy")
    np.save(output_path, raw_bits)
    print(f"📦 Archived Seed File: {output_path}")

    # 3. README.md 상의 샘플 1,000비트 동적 업데이트
    update_readme_sample_bits(raw_bits, readme_path="README.md", sample_size=1000)

    # 4. 상대 경로를 통한 qrng-dqi-optimizer 전달
    target_dirs = ["../data", "../qrng-dqi-optimizer/data"]
    for target in target_dirs:
        try:
            if os.path.exists(os.path.dirname(target)):
                os.makedirs(target, exist_ok=True)
                shutil.copy(output_path, os.path.join(target, "verified_si28_bits.npy"))
                print(f"   ↳ Auto-bound to target path: {target}")
        except Exception:
            pass

    print("✨ [Complete] Quantum Seed Generation & README Sync Complete.\n")

if __name__ == "__main__":
    run_seed_generation()
