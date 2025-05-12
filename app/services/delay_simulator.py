import time
from app.services.delay_strategies import (
    DelayStrategy,
    FixedDelayStrategy,
    ProgressiveIncreaseDelayStrategy,
    ProgressiveDecreaseDelayStrategy,
    StepDelayStrategy,
    NoResponseDelayStrategy,
    RandomDelayStrategy
)

class DelaySimulator:
    """
    지연 시뮬레이터
    
    다양한 지연 시나리오를 시뮬레이션하기 위한 클래스
    """
    
    def __init__(self, strategy=None):
        """
        지연 시뮬레이터 초기화
        
        Args:
            strategy (DelayStrategy, optional): 초기 지연 전략
        """
        self.strategy = strategy or FixedDelayStrategy(0.0)  # 기본값: 지연 없음
    
    def apply_delay(self):
        """
        현재 전략에 따라 지연 적용
        """
        # 전략 상태 업데이트
        self.strategy.update()
        
        # 지연 시간 계산
        delay_seconds = self.strategy.get_delay()
        
        # 지연 적용
        if delay_seconds > 0:
            time.sleep(delay_seconds)
    
    def set_strategy(self, strategy_name, params=None):
        """
        지연 전략 설정
        
        Args:
            strategy_name (str): 전략 이름
            params (dict, optional): 전략 매개변수
        
        Raises:
            ValueError: 유효하지 않은 전략 이름
        """
        params = params or {}
        
        # 전략 이름에 따라 적절한 전략 객체 생성
        if strategy_name == 'FixedDelayStrategy':
            self.strategy = FixedDelayStrategy(
                delay_seconds=params.get('delay_seconds', 1.0)
            )
        elif strategy_name == 'ProgressiveIncreaseDelayStrategy':
            self.strategy = ProgressiveIncreaseDelayStrategy(
                initial_delay=params.get('initial_delay', 0.0),
                increment=params.get('increment', 0.5),
                interval=params.get('interval', 5.0),
                max_steps=params.get('max_steps', 10)
            )
        elif strategy_name == 'ProgressiveDecreaseDelayStrategy':
            self.strategy = ProgressiveDecreaseDelayStrategy(
                initial_delay=params.get('initial_delay', 5.0),
                decrement=params.get('decrement', 0.5),
                interval=params.get('interval', 5.0),
                min_delay=params.get('min_delay', 0.0)
            )
        elif strategy_name == 'StepDelayStrategy':
            self.strategy = StepDelayStrategy(
                normal_delay=params.get('normal_delay', 0.0),
                high_delay=params.get('high_delay', 5.0),
                normal_duration=params.get('normal_duration', 5.0),
                high_duration=params.get('high_duration', 5.0),
                step_increment=params.get('step_increment', 5.0),
                total_duration=params.get('total_duration', 300.0)
            )
        elif strategy_name == 'NoResponseDelayStrategy':
            self.strategy = NoResponseDelayStrategy(
                no_response_duration=params.get('no_response_duration', 10.0)
            )
        elif strategy_name == 'RandomDelayStrategy':
            self.strategy = RandomDelayStrategy(
                min_delay=params.get('min_delay', 0.5),
                max_delay=params.get('max_delay', 5.0),
                change_interval=params.get('change_interval', 5.0),
                total_duration=params.get('total_duration', 300.0)
            )
        else:
            raise ValueError(f"유효하지 않은 전략 이름: {strategy_name}")
    
    def get_config(self):
        """
        현재 지연 설정 조회
        
        Returns:
            dict: 현재 지연 설정 정보
        """
        return self.strategy.get_config()
    
    # 편의 메서드: 특정 시나리오를 쉽게 설정할 수 있는 메서드들
    
    def set_fixed_delay(self, delay_seconds):
        """
        고정 지연 설정
        
        Args:
            delay_seconds (float): 지연 시간(초)
        """
        self.set_strategy('FixedDelayStrategy', {'delay_seconds': delay_seconds})
    
    def set_progressive_increase_delay(self, initial_delay=0.0, increment=0.5, interval=5.0, max_steps=10):
        """
        점진적 증가 지연 설정
        
        Args:
            initial_delay (float, optional): 초기 지연 시간(초)
            increment (float, optional): 증가량(초)
            interval (float, optional): 증가 간격(초)
            max_steps (int, optional): 최대 증가 단계 수
        """
        self.set_strategy('ProgressiveIncreaseDelayStrategy', {
            'initial_delay': initial_delay,
            'increment': increment,
            'interval': interval,
            'max_steps': max_steps
        })
    
    def set_progressive_decrease_delay(self, initial_delay=5.0, decrement=0.5, interval=5.0, min_delay=0.0):
        """
        점진적 감소 지연 설정
        
        Args:
            initial_delay (float, optional): 초기 지연 시간(초)
            decrement (float, optional): 감소량(초)
            interval (float, optional): 감소 간격(초)
            min_delay (float, optional): 최소 지연 시간(초)
        """
        self.set_strategy('ProgressiveDecreaseDelayStrategy', {
            'initial_delay': initial_delay,
            'decrement': decrement,
            'interval': interval,
            'min_delay': min_delay
        })
    
    def set_step_delay(self, normal_delay=0.0, high_delay=5.0, normal_duration=5.0, high_duration=5.0, step_increment=5.0, total_duration=300.0):
        """
        계단식 지연 설정
        
        Args:
            normal_delay (float, optional): 정상 지연 시간(초)
            high_delay (float, optional): 높은 지연 시간(초)
            normal_duration (float, optional): 정상 지연 지속 시간(초)
            high_duration (float, optional): 높은 지연 지속 시간(초)
            step_increment (float, optional): 높은 지연 증가량(초)
            total_duration (float, optional): 총 지속 시간(초)
        """
        self.set_strategy('StepDelayStrategy', {
            'normal_delay': normal_delay,
            'high_delay': high_delay,
            'normal_duration': normal_duration,
            'high_duration': high_duration,
            'step_increment': step_increment,
            'total_duration': total_duration
        })
    
    def set_no_response(self, duration=10.0):
        """
        무응답 시뮬레이션 설정
        
        Args:
            duration (float, optional): 무응답 지속 시간(초)
        """
        self.set_strategy('NoResponseDelayStrategy', {'no_response_duration': duration})
    
    def set_random_delay(self, min_delay=0.5, max_delay=5.0, change_interval=5.0, total_duration=300.0):
        """
        랜덤 지연 설정
        
        Args:
            min_delay (float, optional): 최소 지연 시간(초)
            max_delay (float, optional): 최대 지연 시간(초)
            change_interval (float, optional): 지연 시간 변경 간격(초)
            total_duration (float, optional): 총 지속 시간(초)
        """
        self.set_strategy('RandomDelayStrategy', {
            'min_delay': min_delay,
            'max_delay': max_delay,
            'change_interval': change_interval,
            'total_duration': total_duration
        })
