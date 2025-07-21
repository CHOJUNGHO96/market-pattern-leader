#!/usr/bin/env python3
"""백엔드 서버 실행 스크립트"""

import sys
import os

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 이제 메인 애플리케이션 실행
if __name__ == "__main__":
    try:
        import uvicorn
        from main import app
        
        print("🚀 PatternLeader 백엔드 서버 시작")
        print("📍 주소: http://localhost:8000")
        print("📖 API 문서: http://localhost:8000/docs")
        print("❤️ 헬스체크: http://localhost:8000/health")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ 임포트 오류: {e}")
        print("💡 다음을 확인하세요:")
        print("   1. 가상환경이 활성화되었는지")
        print("   2. requirements.txt가 설치되었는지")
        print("   3. 현재 디렉토리가 backend인지")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ 서버 시작 실패: {e}")
        sys.exit(1)