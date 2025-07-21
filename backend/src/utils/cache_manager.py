"""캐시 관리 모듈"""

import json
import time
from typing import Optional, Any, Dict
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import logging

from src.core.config import settings
from src.core.logging import get_logger


class CacheInterface(ABC):
    """캐시 인터페이스"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """캐시에서 값 조회"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """캐시에 값 저장"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """캐시에서 값 삭제"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """키 존재 여부 확인"""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """전체 캐시 삭제"""
        pass


class MemoryCache(CacheInterface):
    """인메모리 캐시 구현"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self._cache: Dict[str, Dict] = {}  # {key: {'value': value, 'expire_time': timestamp}}
        self.default_ttl = settings.DATA_CACHE_TTL
    
    async def get(self, key: str) -> Optional[Any]:
        """
        캐시에서 값 조회
        
        Args:
            key: 캐시 키
            
        Returns:
            캐시된 값 또는 None
        """
        try:
            if key not in self._cache:
                return None
            
            cache_item = self._cache[key]
            
            # 만료 시간 확인
            if cache_item['expire_time'] < time.time():
                # 만료된 캐시 삭제
                del self._cache[key]
                self.logger.debug(f"만료된 캐시 삭제: {key}")
                return None
            
            self.logger.debug(f"캐시 조회 성공: {key}")
            return cache_item['value']
            
        except Exception as e:
            self.logger.error(f"캐시 조회 실패: {key}, 오류: {str(e)}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """
        캐시에 값 저장
        
        Args:
            key: 캐시 키
            value: 저장할 값
            ttl: 생존 시간 (초)
            
        Returns:
            저장 성공 여부
        """
        try:
            ttl = ttl or self.default_ttl
            expire_time = time.time() + ttl
            
            self._cache[key] = {
                'value': value,
                'expire_time': expire_time
            }
            
            self.logger.debug(f"캐시 저장 성공: {key}, TTL: {ttl}초")
            return True
            
        except Exception as e:
            self.logger.error(f"캐시 저장 실패: {key}, 오류: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        캐시에서 값 삭제
        
        Args:
            key: 삭제할 캐시 키
            
        Returns:
            삭제 성공 여부
        """
        try:
            if key in self._cache:
                del self._cache[key]
                self.logger.debug(f"캐시 삭제 성공: {key}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"캐시 삭제 실패: {key}, 오류: {str(e)}")
            return False
    
    async def exists(self, key: str) -> bool:
        """
        키 존재 여부 확인
        
        Args:
            key: 확인할 캐시 키
            
        Returns:
            존재 여부
        """
        value = await self.get(key)
        return value is not None
    
    async def clear(self) -> bool:
        """
        전체 캐시 삭제
        
        Returns:
            삭제 성공 여부
        """
        try:
            self._cache.clear()
            self.logger.info("전체 캐시 삭제 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"전체 캐시 삭제 실패: {str(e)}")
            return False
    
    def cleanup_expired(self) -> int:
        """
        만료된 캐시 정리
        
        Returns:
            삭제된 캐시 개수
        """
        current_time = time.time()
        expired_keys = []
        
        for key, cache_item in self._cache.items():
            if cache_item['expire_time'] < current_time:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            self.logger.debug(f"만료된 캐시 {len(expired_keys)}개 정리 완료")
        
        return len(expired_keys)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        캐시 통계 정보
        
        Returns:
            캐시 통계 딕셔너리
        """
        current_time = time.time()
        active_count = 0
        expired_count = 0
        
        for cache_item in self._cache.values():
            if cache_item['expire_time'] >= current_time:
                active_count += 1
            else:
                expired_count += 1
        
        return {
            'total_keys': len(self._cache),
            'active_keys': active_count,
            'expired_keys': expired_count,
            'cache_type': 'memory'
        }


class CacheManager:
    """캐시 매니저"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self._cache = self._initialize_cache()
    
    def _initialize_cache(self) -> CacheInterface:
        """
        캐시 구현체 초기화
        
        Returns:
            CacheInterface 구현체
        """
        cache_type = settings.CACHE_TYPE.lower()
        
        if cache_type == "redis":
            # Redis 캐시는 추후 구현
            self.logger.warning("Redis 캐시는 아직 구현되지 않았습니다. 메모리 캐시를 사용합니다.")
            return MemoryCache()
        else:
            return MemoryCache()
    
    async def get(self, key: str) -> Optional[Any]:
        """캐시에서 값 조회"""
        return await self._cache.get(key)
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """캐시에 값 저장"""
        return await self._cache.set(key, value, ttl)
    
    async def delete(self, key: str) -> bool:
        """캐시에서 값 삭제"""
        return await self._cache.delete(key)
    
    async def exists(self, key: str) -> bool:
        """키 존재 여부 확인"""
        return await self._cache.exists(key)
    
    async def clear(self) -> bool:
        """전체 캐시 삭제"""
        return await self._cache.clear()
    
    def generate_cache_key(self, symbol: str, market_type: str, period: str) -> str:
        """
        캐시 키 생성
        
        Args:
            symbol: 심볼
            market_type: 시장 타입
            period: 기간
            
        Returns:
            캐시 키
        """
        return f"analysis:{market_type}:{symbol}:{period}"
    
    def is_cache_expired(self, cached_result: Dict, ttl: int = None) -> bool:
        """
        캐시 만료 여부 확인
        
        Args:
            cached_result: 캐시된 결과
            ttl: 생존 시간 (초)
            
        Returns:
            만료 여부
        """
        if not cached_result or 'cached_at' not in cached_result:
            return True
        
        ttl = ttl or settings.DATA_CACHE_TTL
        cached_at = cached_result['cached_at']
        
        # 문자열이면 datetime으로 파싱
        if isinstance(cached_at, str):
            try:
                cached_at = datetime.fromisoformat(cached_at)
            except ValueError:
                return True
        
        expire_time = cached_at + timedelta(seconds=ttl)
        return datetime.utcnow() >= expire_time
    
    def prepare_cache_data(self, data: Any) -> Dict[str, Any]:
        """
        캐시용 데이터 준비
        
        Args:
            data: 캐시할 데이터
            
        Returns:
            캐시용 딕셔너리
        """
        return {
            'data': data,
            'cached_at': datetime.utcnow()
        }
    
    def extract_cache_data(self, cached_result: Dict) -> Any:
        """
        캐시에서 실제 데이터 추출
        
        Args:
            cached_result: 캐시된 결과
            
        Returns:
            실제 데이터
        """
        return cached_result.get('data') if cached_result else None
    
    async def get_or_set(
        self, 
        key: str, 
        value_func,
        ttl: int = None,
        *args, 
        **kwargs
    ) -> Any:
        """
        캐시에서 조회하고, 없으면 함수 실행 후 저장
        
        Args:
            key: 캐시 키
            value_func: 값을 생성하는 함수
            ttl: 생존 시간
            *args, **kwargs: value_func에 전달할 인수
            
        Returns:
            캐시된 값 또는 새로 생성된 값
        """
        # 캐시에서 조회
        cached_result = await self.get(key)
        
        if cached_result and not self.is_cache_expired(cached_result, ttl):
            self.logger.debug(f"캐시 히트: {key}")
            return self.extract_cache_data(cached_result)
        
        # 캐시 미스 - 새로 생성
        self.logger.debug(f"캐시 미스: {key}")
        
        if asyncio.iscoroutinefunction(value_func):
            value = await value_func(*args, **kwargs)
        else:
            value = value_func(*args, **kwargs)
        
        # 캐시에 저장
        cache_data = self.prepare_cache_data(value)
        await self.set(key, cache_data, ttl)
        
        return value
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """
        패턴에 맞는 캐시 키들 무효화
        
        Args:
            pattern: 무효화할 키 패턴 (예: "analysis:crypto:*")
            
        Returns:
            무효화된 키 개수
        """
        # 메모리 캐시에서는 모든 키를 확인해야 함
        if isinstance(self._cache, MemoryCache):
            invalidated_count = 0
            keys_to_delete = []
            
            # 패턴 매칭을 위한 간단한 구현 (와일드카드 지원)
            pattern_prefix = pattern.replace('*', '')
            
            for key in self._cache._cache.keys():
                if key.startswith(pattern_prefix):
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                if await self.delete(key):
                    invalidated_count += 1
            
            self.logger.info(f"패턴 '{pattern}'에 맞는 {invalidated_count}개 캐시 무효화")
            return invalidated_count
        
        return 0