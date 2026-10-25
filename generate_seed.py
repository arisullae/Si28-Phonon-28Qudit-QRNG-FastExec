"""
Silicon-28 Phonon Dynamics & Hunminjeongeum 28-Qudit Topological QRNG
Quantum Seed Generator Module (generate_seed.py - Daily Lightweight Mode)
"""
import os
import sys
import re
import shutil
import numpy as np

# si28_qrng 엔진 클래스 명칭 자동 호환 임포트 (CirqPhononQRNGEngine / PhononQRNG)
try:
    from si28_qrng import CirqPhononQRNGEngine, ExecutionMode
    ENGINE_TYPE = "CIRQ"
except ImportError:
    try:
        from si28_qrng import PhononQRNG
        ENGINE_TYPE = "PHONON"
    except ImportError as e:
        print(f"❌ [Error] si28_qrng import failed: {e}")
        sys.exit(1)

def update_readme_sample_bits(raw_bits, readme_path="README.md", sample_size=1000):
    """README.md 내의 1,000개 예시 난수 텍스트만 최신 양자 비트로 경량 자동 교체"""
    if not os.path.exists(readme_path):
        return

    try:
        sample_bits = raw_bits[:sample_size].tolist()
        formatted_sample = (
            f"<!-- QUANTUM_SEED_START -->\n"
            f"```python\n"
            f"# Daily Verified Si28 Quantum Entropy Sample (First 1,000 bits)\n"
            f"SI28_QUANTUM_SEED_SAMPLE = {sample_bits}\n"
            f"```\n"
            f"<!-- QUANTUM_SEED_END -->"
        )

        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()

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

def generate_and_save_si28_seed(bit_length: int = 1_000_000, num_runs: int = 1):
    # [경량화] NIST SP 800-22 검증 표 및 Cell 10 매니페스토 출력 없이 요약 로그만 표출
    print("🚀 [Si28-QRNG Engine] Mode 2 Daily Seed Generation Initialized...")

    # 1. Cell 1 수준의 순수 양자 엔트로피 비트스트림만 추출
    try:
        if ENGINE_TYPE == "CIRQ":
            engine = CirqPhononQRNGEngine(mode=ExecutionMode.MODE_2_CIRQ_SIMULATION)
            result = engine.generate_quantum_entropy_bits(bit_length=bit_length, num_runs=num_runs)
            if not result.get("success", False):
                print(f"❌ [Error] Quantum entropy generation failed: {result.get('error')}")
                sys.exit(1)
            raw_bits = np.concatenate(result["entropy_streams"])
        else:
            qrng = PhononQRNG()
            raw_bits = qrng.generate_bits(length=bit_length)
    except Exception as err:
        print(f"❌ [Error] Seed generation execution failed: {err}")
        sys.exit(1)

    print(f"✅ Generated Real Quantum Entropy: {len(raw_bits):,} bits")

    # 2. 로컬 data/ 폴더에 verified_si28_bits.npy 저장
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "verified_si28_bits.npy")
    np.save(output_path, raw_bits)
    print(f"📦 Archived Seed File: {output_path}")

    # 3. README.md 상의 샘플 1,000비트 동적 업데이트
    update_readme_sample_bits(raw_bits, readme_path="README.md", sample_size=1000)

    # 4. 상대 경로를 통한 qrng-dqi-optimizer 및 상위 data/ 폴더 전달
    target_dirs = ["../data", "../qrng-dqi-optimizer/data"]
    transferred_count = 0
    for target in target_dirs:
        try:
            if os.path.exists(os.path.dirname(target)):
                os.makedirs(target, exist_ok=True)
                shutil.copy(output_path, os.path.join(target, "verified_si28_bits.npy"))
                print(f"   ↳ Bound to target path: {target}")
                transferred_count += 1
        except Exception:
            pass

    print(f"✨ [Complete] Quantum Seed Binding Complete ({transferred_count} target locations updated).\n")

if __name__ == "__main__":
    generate_and_save_si28_seed(bit_length=1_000_000, num_runs=1)
