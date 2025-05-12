import time
import random
from abc import ABC, abstractmethod

class DelayStrategy(ABC):
    """
    지연 전략 추상 클래스
    
    다양한 지연 시나리오를 구현하기 위한 기본 클래스
    """
    
    @abstractmethod
    def get_delay(self):
        """
        현재 지연 시간(초) 반환
        
        Returns:
            float: 지연 시간(초)
        """
        pass
    
    @abstractmethod
    def update(self):
        """
        전략 상태 업데이트
        
        일부 전략은 시간이 지남에 따라 지연 시간이 변경될 수 있음
        """
        pass
    
    def get_config(self):
        """
        현재 전략 설정 반환
        
        Returns:
            dict: 전략 설정 정보
        """
        return {
            'strategy': self.__class__.__name__,
            'params': {}
        }


class FixedDelayStrategy(DelayStrategy):
    """
    고정 지연 전략
    
    항상 동일한 지연 시간을 반환
    """
    
    def __init__(self, delay_seconds=1.0):
        """
        고정 지연 전략 초기화
        
        Args:
            delay_seconds (float, optional): 지연 시간(초)
        """
        self.delay_seconds = delay_seconds
    
    def get_delay(self):
        return self.delay_seconds
    
    def update(self):
        # 고정 지연은 업데이트가 필요 없음
        pass
    
    def get_config(self):
        config = super().get_config()
        config['params'] = {'delay_seconds': self.delay_seconds}
        return config


class ProgressiveIncreaseDelayStrategy(DelayStrategy):
    """
    점진적 증가 지연 전략
    
    시간이 지남에 따라 지연 시간이 점진적으로 증가
    """
    
    def __init__(self, initial_delay=0.0, increment=0.5, interval=5.0, max_steps=10):
        """
        점진적 증가 지연 전략 초기화
        
        Args:
            initial_delay (float, optional): 초기 지연 시간(초)
            increment (float, optional): 증가량(초)
            interval (float, optional): 증가 간격(초)
            max_steps (int, optional): 최대 증가 단계 수
        """
        self.initial_delay = initial_delay
        self.increment = increment
        self.interval = interval
        self.max_steps = max_steps
        
        self.current_delay = initial_delay
        self.current_step = 0
        self.last_update_time = time.time()
    
    def get_delay(self):
        return self.current_delay
    
    def update(self):
        current_time = time.time()
        elapsed = current_time - self.last_update_time
        
        if elapsed >= self.interval and self.current_step < self.max_steps:
            self.current_step += 1
            self.current_delay = self.initial_delay + (self.increment * self.current_step)
            self.last_update_time = current_time
    
    def get_config(self):
        config = super().get_config()
        config['params'] = {
            'initial_delay': self.initial_delay,
            'increment': self.increment,
            'interval': self.interval,
            'max_steps': self.max_steps,
            'current_step': self.current_step,
            'current_delay': self.current_delay
        }
        return config


class ProgressiveDecreaseDelayStrategy(DelayStrategy):
    """
    점진적 감소 지연 전략
    
    시간이 지남에 따라 지연 시간이 점진적으로 감소
    """
    
    def __init__(self, initial_delay=5.0, decrement=0.5, interval=5.0, min_delay=0.0):
        """
        점진적 감소 지연 전략 초기화
        
        Args:
            initial_delay (float, optional): 초기 지연 시간(초)
            decrement (float, optional): 감소량(초)
            interval (float, optional): 감소 간격(초)
            min_delay (float, optional): 최소 지연 시간(초)
        """
        self.initial_delay = initial_delay
        self.decrement = decrement
        self.interval = interval
        self.min_delay = min_delay
        
        self.current_delay = initial_delay
        self.last_update_time = time.time()
    
    def get_delay(self):
        return self.current_delay
    
    def update(self):
        current_time = time.time()
        elapsed = current_time - self.last_update_time
        
        if elapsed >= self.interval and self.current_delay > self.min_delay:
            new_delay = self.current_delay - self.decrement
            self.current_delay = max(new_delay, self.min_delay)
            self.last_update_time = current_time
    
    def get_config(self):
        config = super().get_config()
        config['params'] = {
            'initial_delay': self.initial_delay,
            'decrement': self.decrement,
            'interval': self.interval,
            'min_delay': self.min_delay,
            'current_delay': self.current_delay
        }
        return config


class StepDelayStrategy(DelayStrategy):
    """
    계단식 지연 전략
    
    정상 지연과 높은 지연을 번갈아가며 적용
    """
    
    def __init__(self, normal_delay=0.0, high_delay=5.0, normal_duration=5.0, high_duration=5.0, step_increment=5.0, total_duration=300.0):
        """
        계단식 지연 전략 초기화
        
        Args:
            normal_delay (float, optional): 정상 지연 시간(초)
            high_delay (float, optional): 높은 지연 시간(초)
            normal_duration (float, optional): 정상 지연 지속 시간(초)
            high_duration (float, optional): 높은 지연 지속 시간(초)
            step_increment (float, optional): 높은 지연 증가량(초)
            total_duration (float, optional): 총 지속 시간(초)
        """
        self.normal_delay = normal_delay
        self.high_delay = high_delay
        self.normal_duration = normal_duration
        self.high_duration = high_duration
        self.step_increment = step_increment
        self.total_duration = total_duration
        
        self.is_high_delay = False
        self.current_high_delay = high_delay
        self.current_delay = normal_delay
        self.start_time = time.time()
        self.last_switch_time = self.start_time
    
    def get_delay(self):
        return self.current_delay
    
    def update(self):
        current_time = time.time()
        total_elapsed = current_time - self.start_time
        
        if total_elapsed > self.total_duration:
            # 총 지속 시간이 지나면 정상 지연으로 리셋
            self.current_delay = self.normal_delay
            self.is_high_delay = False
            self.current_high_delay = self.high_delay
            self.start_time = current_time
            self.last_switch_time = current_time
            return
        
        elapsed_since_switch = current_time - self.last_switch_time
        
        if self.is_high_delay and elapsed_since_switch >= self.high_duration:
            # 높은 지연에서 정상 지연으로 전환
            self.is_high_delay = False
            self.current_delay = self.normal_delay
            self.last_switch_time = current_time
        elif not self.is_high_delay and elapsed_since_switch >= self.normal_duration:
            # 정상 지연에서 높은 지연으로 전환
            self.is_high_delay = True
            self.current_delay = self.current_high_delay
            self.current_high_delay += self.step_increment
            self.last_switch_time = current_time
    
    def get_config(self):
        config = super().get_config()
        config['params'] = {
            'normal_delay': self.normal_delay,
            'high_delay': self.high_delay,
            'normal_duration': self.normal_duration,
            'high_duration': self.high_duration,
            'step_increment': self.step_increment,
            'total_duration': self.total_duration,
            'is_high_delay': self.is_high_delay,
            'current_high_delay': self.current_high_delay,
            'current_delay': self.current_delay
        }
        return config


class NoResponseDelayStrategy(DelayStrategy):
    """
    무응답 시뮬레이션 전략
    
    지정된 시간 동안 무응답 상태를 시뮬레이션
    """
    
    def __init__(self, no_response_duration=10.0):
        """
        무응답 시뮬레이션 전략 초기화
        
        Args:
            no_response_duration (float, optional): 무응답 지속 시간(초)
        """
        self.no_response_duration = no_response_duration
        self.is_active = True
        self.start_time = time.time()
    
    def get_delay(self):
        if self.is_active:
            return self.no_response_duration
        return 0.0
    
    def update(self):
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        if elapsed >= self.no_response_duration:
            self.is_active = False
    
    def get_config(self):
        config = super().get_config()
        config['params'] = {
            'no_response_duration': self.no_response_duration,
            'is_active': self.is_active,
            'elapsed': time.time() - self.start_time
        }
        return config


class RandomDelayStrategy(DelayStrategy):
    """
    랜덤 지연 전략
    
    지정된 범위 내에서 랜덤한 지연 시간을 반환
    """
    
    def __init__(self, min_delay=0.5, max_delay=5.0, change_interval=5.0, total_duration=300.0):
        """
        랜덤 지연 전략 초기화
        
        Args:
            min_delay (float, optional): 최소 지연 시간(초)
            max_delay (float, optional): 최대 지연 시간(초)
            change_interval (float, optional): 지연 시간 변경 간격(초)
            total_duration (float, optional): 총 지속 시간(초)
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.change_interval = change_interval
        self.total_duration = total_duration
        
        self.current_delay = random.uniform(min_delay, max_delay)
        self.start_time = time.time()
        self.last_change_time = self.start_time
    
    def get_delay(self):
        return self.current_delay
    
    def update(self):
        current_time = time.time()
        total_elapsed = current_time - self.start_time
        
        if total_elapsed > self.total_duration:
            # 총 지속 시간이 지나면 리셋
            self.current_delay = random.uniform(self.min_delay, self.max_delay)
            self.start_time = current_time
            self.last_change_time = current_time
            return
        
        elapsed_since_change = current_time - self.last_change_time
        
        if elapsed_since_change >= self.change_interval:
            self.current_delay = random.uniform(self.min_delay, self.max_delay)
            self.last_change_time = current_time
    
    def get_config(self):
        config = super().get_config()
        config['params'] = {
            'min_delay': self.min_delay,
            'max_delay': self.max_delay,
            'change_interval': self.change_interval,
            'total_duration': self.total_duration,
            'current_delay': self.current_delay
        }
        return config
