# 코드 포맷팅 스크립트

이 프로젝트에서 사용하는 코드 포맷팅 도구들을 일괄 실행하는 스크립트입니다.

## 📁 파일 위치

모든 포맷팅 스크립트는 `backend/scripts/` 폴더에 있습니다:
- `format.py` - Python 스크립트 (크로스 플랫폼)
- `format.bat` - Windows 배치 파일
- `format.sh` - Linux/Mac 쉘 스크립트

## 포함된 도구들

### 1. **isort** - Import 문 정렬
- **프로필**: `black` (black과 호환)
- **라인 길이**: 120자
- **스타일**: trailing comma, parentheses 사용

### 2. **black** - 코드 포맷팅
- **라인 길이**: 120자
- **타겟 버전**: Python 3.12
- **대상**: `src/` 디렉토리

### 3. **toml-sort** - TOML 파일 정렬
- **대상**: `pyproject.toml`
- **옵션**: 모든 섹션 정렬, 원본 파일 수정

## 사용법

### Windows
```bash
# backend/scripts 폴더에서 배치 파일 실행 (더블클릭으로도 가능)
cd backend/scripts
format.bat

# 또는 backend 폴더에서 Python 스크립트
cd backend
python scripts/format.py
```

### Linux/Mac
```bash
# backend/scripts 폴더에서 쉘 스크립트 실행
cd backend/scripts
./format.sh

# 또는 backend 폴더에서 Python 스크립트
cd backend
python scripts/format.py
```

### Poetry 환경에서
```bash
# backend 폴더에서 가상환경 활성화 후
cd backend
poetry shell
python scripts/format.py
```

## 실행 순서

1. **isort**: import 문 정렬
2. **black**: 코드 포맷팅
3. **toml-sort**: TOML 파일 정렬

## 에러 처리

- 각 단계에서 오류가 발생하면 스크립트가 중단됩니다
- 오류 메시지가 출력되어 문제를 확인할 수 있습니다

## 설정 파일

관련 설정은 다음 파일들에서 확인할 수 있습니다:
- `backend/pyproject.toml`: 라인 길이, 타겟 버전 등
- `backend/src/.pre-commit-config.yaml`: pre-commit 훅 설정

## 개별 실행

필요한 경우 backend 폴더에서 개별 도구를 직접 실행할 수도 있습니다:

```bash
# backend 폴더에서 실행
cd backend

# isort만 실행
isort --profile black --line-length 120 src/

# black만 실행
black --line-length 120 --target-version py312 src/

# toml-sort만 실행
toml-sort --all --in-place pyproject.toml
```

## 폴더 구조

```
backend/
├── scripts/          # 포맷팅 스크립트 폴더
│   ├── format.py
│   ├── format.bat
│   ├── format.sh
│   └── FORMAT_README.md
├── src/              # 소스 코드
├── pyproject.toml    # 프로젝트 설정
└── ...
``` 