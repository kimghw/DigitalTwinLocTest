"""
지연 시뮬레이터 테스트
"""

import time
import pytest
from app.services.delay_simulator import DelaySimulator

def test_fixed_delay():
    """
    고정 지연 테스트
    """
    # 지연 시뮬레이터 생성
    simulator = DelaySimulator()
    
    # 고정 지연 설정 (0.1초)
    simulator.set_fixed_delay(0.1)
    
    # 설정 확인
    config = simulator.get_config()
    assert config['strategy'] == 'FixedDelayStrategy'
    assert config['params']['delay_seconds'] == 0.1
    
    # 지연 적용 시간 측정
    start_time = time.time()
    simulator.apply_delay()
    elapsed_time = time.time() - start_time
    
    # 지연 시간 확인 (오차 허용)
    assert 0.05 <= elapsed_time <= 0.15

def test_progressive_increase_delay():
    """
    점진적 증가 지연 테스트
    """
    # 지연 시뮬레이터 생성
    simulator = DelaySimulator()
    
    # 점진적 증가 지연 설정
    simulator.set_progressive_increase_delay(
        initial_delay=0.1,
        increment=0.1,
        interval=0.1,  # 빠른 테스트를 위해 짧은 간격 사용
        max_steps=3
    )
    
    # 설정 확인
    config = simulator.get_config()
    assert config['strategy'] == 'ProgressiveIncreaseDelayStrategy'
    assert config['params']['initial_delay'] == 0.1
    
    # 초기 지연 확인
    start_time = time.time()
    simulator.apply_delay()
    elapsed_time = time.time() - start_time
    assert 0.05 <= elapsed_time <= 0.15
    
    # 잠시 대기하여 간격 경과
    time.sleep(0.2)
    
    # 두 번째 지연 확인 (증가된 지연)
    start_time = time.time()
    simulator.apply_delay()
    elapsed_time = time.time() - start_time
    assert 0.15 <= elapsed_time <= 0.25

def test_progressive_decrease_delay():
    """
    점진적 감소 지연 테스트
    """
    # 지연 시뮬레이터 생성
    simulator = DelaySimulator()
    
    # 점진적 감소 지연 설정
    simulator.set_progressive_decrease_delay(
        initial_delay=0.3,
        decrement=0.1,
        interval=0.1,  # 빠른 테스트를 위해 짧은 간격 사용
        min_delay=0.1
    )
    
    # 설정 확인
    config = simulator.get_config()
    assert config['strategy'] == 'ProgressiveDecreaseDelayStrategy'
    assert config['params']['initial_delay'] == 0.3
    
    # 초기 지연 확인
    start_time = time.time()
    simulator.apply_delay()
    elapsed_time = time.time() - start_time
    assert 0.25 <= elapsed_time <= 0.35
    
    # 잠시 대기하여 간격 경과
    time.sleep(0.2)
    
    # 두 번째 지연 확인 (감소된 지연)
    start_time = time.time()
    simulator.apply_delay()
    elapsed_time = time.time() - start_time
    assert 0.15 <= elapsed_time <= 0.25

def test_step_delay():
    """
    계단식 지연 테스트
    """
    # 지연 시뮬레이터 생성
    simulator = DelaySimulator()
    
    # 계단식 지연 설정
    simulator.set_step_delay(
        normal_delay=0.1,
        high_delay=0.3,
        normal_duration=0.1,  # 빠른 테스트를 위해 짧은 간격 사용
        high_duration=0.1,
        step_increment=0.1,
        total_duration=1.0
    )
    
    # 설정 확인
    config = simulator.get_config()
    assert config['strategy'] == 'StepDelayStrategy'
    
    # 초기 지연 확인 (정상 지연)
    start_time = time.time()
    simulator.apply_delay()
    elapsed_time = time.time() - start_time
    assert 0.05 <= elapsed_time <= 0.15
    
    # 잠시 대기하여 간격 경과
    time.sleep(0.2)
    
    # 두 번째 지연 확인 (높은 지연)
    start_time = time.time()
    simulator.apply_delay()
    elapsed_time = time.time() - start_time
    assert 0.25 <= elapsed_time <= 0.35

def test_no_response_delay():
    """
    무응답 시뮬레이션 테스트
    """
    # 지연 시뮬레이터 생성
    simulator = DelaySimulator()
    
    # 무응답 시뮬레이션 설정 (짧은 시간으로 설정)
    simulator.set_no_response(0.2)
    
    # 설정 확인
    config = simulator.get_config()
    assert config['strategy'] == 'NoResponseDelayStrategy'
    assert config['params']['no_response_duration'] == 0.2
    
    # 지연 적용 시간 측정
    start_time = time.time()
    simulator.apply_delay()
    elapsed_time = time.time() - start_time
    
    # 지연 시간 확인 (오차 허용)
    assert 0.15 <= elapsed_time <= 0.25

def test_random_delay():
    """
    랜덤 지연 테스트
    """
    # 지연 시뮬레이터 생성
    simulator = DelaySimulator()
    
    # 랜덤 지연 설정
    simulator.set_random_delay(
        min_delay=0.1,
        max_delay=0.3,
        change_interval=0.1,  # 빠른 테스트를 위해 짧은 간격 사용
        total_duration=1.0
    )
    
    # 설정 확인
    config = simulator.get_config()
    assert config['strategy'] == 'RandomDelayStrategy'
    assert config['params']['min_delay'] == 0.1
    assert config['params']['max_delay'] == 0.3
    
    # 지연 적용 시간 측정
    start_time = time.time()
    simulator.apply_delay()
    elapsed_time = time.time() - start_time
    
    # 지연 시간 확인 (범위 내에 있는지)
    assert 0.05 <= elapsed_time <= 0.35
