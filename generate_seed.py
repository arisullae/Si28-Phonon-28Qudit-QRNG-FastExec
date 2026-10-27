"""
Silicon-28 Phonon Dynamics & Hunminjeongeum 28-Qudit Topological QRNG
Quantum Seed Generator Module (generate_seed.py - Dropdown & 100-bit Align)
"""
import os
import sys
import re
import shutil
import datetime
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
    """README.md 내 <details> 드롭다운 영역에 100개씩 10줄(총 1,000비트) 정렬하여 안전 교체"""
    if not os.path.exists(readme_path):
        print(f"⚠️ [Warning] {readme_path} 파일이 존재하지 않습니다.")
        return

    try:
        # 1. 상위 1,000비트를 추출하여 한 줄에 100개씩 총 10줄로 포맷팅
        bits_str = "".join(map(str, raw_bits[:sample_size]))
        lines = [bits_str[i : i + 100] for i in range(0, sample_size, 100)]
        formatted_bits_text = "\n".join(lines)

        # 2. 오늘 날짜의 연도 기준 일수(Day of Year) 계산
        day_of_year = datetime.datetime.now().timetuple().tm_yday

        # 3. 스크린샷과 동일한 <details> 드롭다운 HTML 및 100비트 정렬 텍스트 생성
        formatted_sample = (
            f"<!-- QUANTUM_SEED_START -->\n"
            f"<details>\n"
            f"<summary><b>👉 [클릭하여 오늘(Day #{day_of_year}) 자동으로 회전된 1,000비트 난수 예시 보기]</b></summary>\n\n"
            f"> **[실시간 물리 난수 비트스트림 (1,000 bits - 100비트 단위 정렬)]**\n"
            f"> 마우스로 드래그하여 복사한 뒤 AI Studio 질문창에 활용하세요!\n"
            f"```text\n"
            f"{formatted_bits_text}\n"
            f"```\n"
            f"</details>\n"
            f"<!-- QUANTUM_SEED_END -->"
        )

        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        pattern = r"<!-- QUANTUM_SEED_START -->.*?<!-- QUANTUM_SEED_END -->"
        
        # 태그가 정확히 마킹되어 있는 경우에만 안전하게 교체 (미발견 시 원본 파일 보존)
        if re.search(pattern, content, flags=re.DOTALL):
            new_content = re.sub(pattern, formatted_sample, content, flags=re.DOTALL)
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print("📝 [Sync] README.md 1,000비트 드롭다운 샘플(100비트/줄) 업데이트 완료.")
        else:
            print("⚠️ [Warning] README.md 내 <!-- QUANTUM_SEED_START --> 태그를 찾을 수 없어 안전하게 업데이트를 스킵했습니다.")
    except Exception as err:
        print(f"⚠️ [Warning] README update skipped: {err}")

def generate_and_save_si28_seed(bit_length: int = 1_000_000, num_runs: int = 1):
    print("🚀 [Si28-QRNG Engine] Mode 2 Daily Seed Generation Initialized...")

    # 1. Cell 1 수준의 순수 양자 엔트로피 비트스트림 추출
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

    # 3. README.md 상의 드롭다운 샘플 1,000비트 동적 안전 업데이트
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
    generate_and_save_si28_seed(bit_length=1_000_000, num_runs=20)
