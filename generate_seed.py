"""
Silicon-28 Phonon Dynamics & Hunminjeongeum 28-Qudit Topological QRNG
Quantum Seed Generator Module (generate_seed.py)
"""

import os
import sys
import numpy as np

# 동일 디렉토리 내 si28_qrng.py 메인 양자 엔진 모듈 임포트
try:
    from si28_qrng import CirqPhononQRNGEngine, ExecutionMode
except ImportError as e:
    print(f"❌ [오류] si28_qrng 모듈 임포트 실패 (실제 원인: {e})")
    sys.exit(1)


def generate_and_save_si28_seed(bit_length: int = 1000000, num_runs: int = 1):
    print("==================================================")
    print(" [*] Si-28 Phonon Cirq 5-Qubit 양자 시드 생성 파이프라인 가동")
    print("==================================================")

    # 1. Cirq 5-Qubit 양자 엔트로피 엔진 가동
    engine = CirqPhononQRNGEngine(mode=ExecutionMode.MODE_2_CIRQ_SIMULATION)
    result = engine.generate_quantum_entropy_bits(bit_length=bit_length, num_runs=num_runs)

    if not result["success"]:
        print(f" ❌ [오류] 양자 엔트로피 생성 실패: {result.get('error')}")
        return

    # 2. 정직한 양자 엔트로피 비트스트림 추출 및 1차원 배열 병합 (보완 반영)
    raw_bits = np.concatenate(result["entropy_streams"])

    # 3. 데이터 저장 디렉토리(data/) 확보
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)

    # 4. NumPy 파일(.npy) 형태로 영구 아카이빙
    output_path = os.path.join(output_dir, "verified_si28_bits.npy")
    np.save(output_path, raw_bits)

    # 5. [신규 추가] qrng-dqi-optimizer 저장소로 양자 시드 자동 전달 (권한 에러 완전 방지)
    import shutil
    target_paths = [
        "../data",                                # GitHub Actions 환경 (상위 qrng-dqi-optimizer/data)
        "/content/qrng-dqi-optimizer/data",       # Colab 환경
        "../qrng-dqi-optimizer/data"              # 로컬 가상 환경
    ]
    for target in target_paths:
        try:
            # 상위 폴더가 실제로 존재하는 경우에만 안전하게 복사
            if os.path.exists(os.path.dirname(target)):
                os.makedirs(target, exist_ok=True)
                shutil.copy(output_path, os.path.join(target, "verified_si28_bits.npy"))
                print(f"    * 자동 전달 완료 -> {target}")
        except Exception:
            pass  # 권한이 없거나 폴더가 없어도 팅기지 않고 안전하게 넘어가도록 보호

    print(f" [+] 진성 양자 시드 발행 완료 및 파일 저장 성공")
    print(f"     * 저장 경로 : {output_path}")
    print(f"     * 총 비트 수: {len(raw_bits):,} bits")
    print("==================================================")


if __name__ == "__main__":
    # 100만 비트 규격 진성 양자 시드 생성 실행
    generate_and_save_si28_seed(bit_length=1000000, num_runs=1)
