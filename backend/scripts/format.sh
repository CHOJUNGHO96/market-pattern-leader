#!/bin/bash

# scripts 폴더에서 backend 폴더로 이동
cd "$(dirname "$0")/.."

echo "🚀 코드 포맷팅 시작..."

# 오류 발생 시 스크립트 중단
set -e

echo ""
echo "🔧 isort (import 정렬)..."
isort --profile black --line-length 120 --multi-line 3 --force-grid-wrap 0 --use-parentheses --ensure-newline-before-comments src/
echo "✅ isort 완료"

echo ""
echo "🔧 black (코드 포맷팅)..."
black --line-length 120 --target-version py312 src/
echo "✅ black 완료"

echo ""
echo "🔧 toml-sort (TOML 파일 정렬)..."
toml-sort --all --in-place pyproject.toml
echo "✅ toml-sort 완료"

echo ""
echo "🎉 모든 포맷팅이 성공적으로 완료되었습니다!" 