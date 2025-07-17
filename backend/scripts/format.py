#!/usr/bin/env python3
"""
코드 포맷팅 스크립트
black, isort, toml-sort를 순차적으로 실행합니다.
"""

import subprocess
import sys
from pathlib import Path


def run_command(command: list[str], description: str) -> bool:
    """명령어를 실행하고 결과를 출력합니다."""
    print(f"\n🔧 {description}...")
    print(f"실행 명령어: {' '.join(command)}")
    
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent  # backend 폴더를 작업 디렉토리로 설정
        )
        print(f"✅ {description} 완료")
        if result.stdout:
            print(f"출력: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 실패")
        print(f"오류: {e.stderr}")
        return False


def main():
    """메인 함수"""
    print("🚀 코드 포맷팅 시작")
    
    # backend 디렉토리 확인 (scripts 폴더의 부모 폴더)
    backend_dir = Path(__file__).parent.parent
    src_dir = backend_dir / "src"
    
    if not src_dir.exists():
        print(f"❌ src 디렉토리를 찾을 수 없습니다: {src_dir}")
        sys.exit(1)
    
    success = True
    
    # 1. isort 실행 - import 정렬
    isort_cmd = [
        "isort",
        "--profile", "black",  # black과 호환되는 프로필
        "--line-length", "120",  # black과 동일한 라인 길이
        "--multi-line", "3",  # trailing comma 스타일
        "--force-grid-wrap", "0",
        "--use-parentheses",
        "--ensure-newline-before-comments",
        "src/"
    ]
    success &= run_command(isort_cmd, "isort (import 정렬)")
    
    # 2. black 실행 - 코드 포맷팅
    black_cmd = [
        "black",
        "--line-length", "120",  # pyproject.toml과 동일
        "--target-version", "py312",
        "src/"
    ]
    success &= run_command(black_cmd, "black (코드 포맷팅)")
    
    # 3. toml-sort 실행 - TOML 파일 정렬
    toml_sort_cmd = [
        "toml-sort",
        "--all",  # 모든 섹션 정렬
        "--in-place",  # 원본 파일 수정
        "pyproject.toml"
    ]
    success &= run_command(toml_sort_cmd, "toml-sort (TOML 파일 정렬)")
    
    # 결과 출력
    if success:
        print("\n🎉 모든 포맷팅이 성공적으로 완료되었습니다!")
    else:
        print("\n💥 일부 포맷팅 작업이 실패했습니다.")
        sys.exit(1)


if __name__ == "__main__":
    main() 