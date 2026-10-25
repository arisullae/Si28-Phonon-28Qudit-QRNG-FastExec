"""
Silicon-28 Phonon Dynamics & Hunminjeongeum 28-Qudit Topological QRNG
Quantum Seed Generator Module (generate_seed.py)
"""
import os
import sys
import re
import shutil
import numpy as np

# 동일 디렉토리 내 si28_qrng.py 메인 양자 엔진 모듈 임포트
try:
    from si28_qrng import CirqPhononQRNGEngine, ExecutionMode
except ImportError as e:
    print(f"❌ [오류] si28_qrng 모듈 임포트 실패: {e}")
    sys.exit(1)

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
        print("📝 [Sync] README.md 1,000개 샘플 난수 텍스트 자동 업데이트 완료")
    except Exception as err:
        print(f"⚠️ [Warning] README 업데이트 건너뜀: {err}")

def generate_and_save_si28_seed(bit_length: int = 1_000_000, num_runs: int = 1):
    print("================================================")
    print(" [*] Si-28 Phonon Cirq 5-Qubit 양자 시드 생성 파이프라인 가동")
    print("================================================")

    # 1. Cirq 5-Qubit 양자 엔트로피 엔진 가동 (Mode 2)
    engine = CirqPhononQRNGEngine(mode=ExecutionMode.MODE_2_CIRQ_SIMULATION)
    result = engine.generate_quantum_entropy_bits(bit_length=bit_length, num_runs=num_runs)

    if not result.get("success", False):
        print(f"❌ [오류] 양자 엔트로피 생성 실패: {result.get('error')}")
        return

    # 2. 정직한 양자 엔트로피 비트스트림 추출 및 1차원 배열 병합
    raw_bits = np.concatenate(result["entropy_streams"])

    # 3. 데이터 저장 디렉토리(data/) 확보
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)

    # 4. NumPy 파일(.npy) 형태로 영구 아카이빙
    output_path = os.path.join(output_dir, "verified_si28_bits.npy")
    np.save(output_path, raw_bits)

    print(f"[+] 진성 양자 시드 발행 완료 및 파일 저장 성공")
    print(f"    * 저장 경로 : {output_path}")
    print(f"    * 총 비트 수: {len(raw_bits):,} bits")
    print("================================================")

    # 5. README.md 상의 샘플 1,000비트 동적 업데이트
    update_readme_sample_bits(raw_bits, readme_path="README.md", sample_size=1000)

    # 6. 상대 경로를 통한 qrng-dqi-optimizer 및 상위 data/ 폴더로 안전하게 전달
    target_dirs = ["../data", "../qrng-dqi-optimizer/data"]
    for target in target_dirs:
        try:
            if os.path.exists(os.path.dirname(target)):
                os.makedirs(target, exist_ok=True)
                shutil.copy(output_path, os.path.join(target, "verified_si28_bits.npy"))
                print(f"    * 양자 시드 전달 완료 -> {target}")
        except Exception:
            pass

    print("✨ [Complete] 양자 시드 생성 및 전달 완료\n")

if __name__ == "__main__":
    generate_and_save_si28_seed(bit_length=1_000_000, num_runs=1)
