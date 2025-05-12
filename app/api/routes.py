from flask import Blueprint, request, jsonify, render_template_string
import time
import json
from app.services.image_processor import process_image
from app.services.delay_simulator import DelaySimulator

# API 블루프린트 생성
api_bp = Blueprint('api', __name__, url_prefix='/api')

# 루트 블루프린트 생성
root_bp = Blueprint('root', __name__)

# 지연 시뮬레이터 인스턴스 생성
delay_simulator = DelaySimulator()

# 최근 요청과 응답 정보 저장 (최대 20개)
recent_requests = []
MAX_RECENT_REQUESTS = 20

@root_bp.route('/')
def index():
    """
    루트 경로 핸들러
    
    API 사용 방법에 대한 기본 정보 제공
    """
    # 최근 요청 정보 가져오기
    global recent_requests
    
    # 최근 요청 정보를 HTML로 변환
    recent_requests_html = ""
    if recent_requests:
        for i, req in enumerate(recent_requests):
            # 요청 시간 포맷팅
            request_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(req['request_time']))
            
            # ID 정보 추출
            id_info = None
            if 'ID' in req['request_data']:
                id_info = req['request_data']['ID']
            elif 'metadata' in req['request_data'] and 'id' in req['request_data']['metadata']:
                id_info = {'imageID': req['request_data']['metadata']['id']}
            else:
                id_info = {'imageID': 'Unknown'}
            
            # 포즈 정보 추출
            request_pose = None
            if 'pose' in req['request_data']:
                request_pose = req['request_data']['pose']
            else:
                request_pose = {'position_m': [0, 0, 0], 'quaternion': [0, 0, 0, 1]}
            
            response_pose = req['response_data']['pose']
            
            # 지연 정보 추출
            delay_config = req['delay_config']
            strategy_name = delay_config['strategy']
            delay_params = delay_config['params']
            
            # 시간 차이 계산
            time_arrive = req['response_data']['time_stamps'][0]
            time_depart = req['response_data']['time_stamps'][1]
            time_diff_ns = time_depart - time_arrive
            time_diff_s = time_diff_ns / 1_000_000_000
            
            recent_requests_html += f"""
            <div class="request-item">
                <h4>요청 {i+1} - {request_time_str}</h4>
                <div class="request-details">
                    <div class="request-id">
                        <h5>ID 정보</h5>
                        <pre>{json.dumps(id_info, indent=2, ensure_ascii=False)}</pre>
                    </div>
                    <div class="request-pose">
                        <h5>요청 포즈</h5>
                        <pre>{json.dumps(request_pose, indent=2, ensure_ascii=False)}</pre>
                    </div>
                    <div class="response-pose">
                        <h5>응답 포즈</h5>
                        <pre>{json.dumps(response_pose, indent=2, ensure_ascii=False)}</pre>
                    </div>
                    <div class="delay-info">
                        <h5>지연 정보</h5>
                        <p>전략: {strategy_name}</p>
                        <p>지연 시간: {time_diff_s:.6f}초</p>
                        <pre>{json.dumps(delay_params, indent=2, ensure_ascii=False)}</pre>
                    </div>
                </div>
            </div>
            """
    else:
        recent_requests_html = "<p>아직 요청이 없습니다.</p>"
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>DigitalTwinLocTest API Server</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                max-width: 800px;
                margin: 0 auto;
            }
            h1 {
                color: #333;
                border-bottom: 1px solid #ddd;
                padding-bottom: 10px;
            }
            h2 {
                color: #444;
                margin-top: 20px;
            }
            pre {
                background-color: #f5f5f5;
                padding: 10px;
                border-radius: 5px;
                overflow-x: auto;
            }
            code {
                font-family: monospace;
                background-color: #f5f5f5;
                padding: 2px 4px;
                border-radius: 3px;
            }
            .endpoint {
                margin-bottom: 20px;
            }
            .method {
                font-weight: bold;
                color: #0066cc;
            }
            .request-item {
                margin-bottom: 30px;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 15px;
                background-color: #f9f9f9;
            }
            .request-item h4 {
                margin-top: 0;
                border-bottom: 1px solid #eee;
                padding-bottom: 10px;
            }
            .request-details {
                display: grid;
                grid-template-columns: 1fr 1fr;
                grid-gap: 15px;
            }
            .request-id, .request-pose, .response-pose, .delay-info {
                background-color: white;
                padding: 10px;
                border-radius: 5px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            .request-id h5, .request-pose h5, .response-pose h5, .delay-info h5 {
                margin-top: 0;
                color: #555;
            }
        </style>
    </head>
    <body>
        <h1>DigitalTwinLocTest API Server</h1>
        <p>유니티 앱에서 서버로 이미지를 전송하고 그 이미지에서 추출한 데이터를 다시 수신 받는 테스트를 위한 REST API 서버입니다.</p>
        
        <h2>API 엔드포인트</h2>
        
        <div class="endpoint">
            <h3><span class="method">POST</span> /api/image</h3>
            <p>이미지 업로드 및 처리 API</p>
            <h4>요청 본문 (새 형식):</h4>
            <pre>
{
  "ID": {
    "imageID": 1,
    "shipID": 1,
    "UserID": 1,
    "cameraId": 0
  },
  "timestamp_ns": 1620000000000000000,
  "camera": {
    "width": 1920,
    "height": 1080,
    "format": "jpeg",
    "focal_px": [1000.0, 1000.0],
    "principal_px": [960.0, 540.0],
    "exposure_us": 10000,
    "iso": 100
  },
  "pose": {
    "position_m": [0.0, 0.0, 0.0],
    "quaternion": [0.0, 0.0, 0.0, 1.0],
    "zone": {
      "deck": 1,
      "compartment": "Main",
      "zone_id": 1
    }
  },
  "image": "base64로 인코딩된 이미지 데이터"
}</pre>
            <h4>요청 본문 (기존 형식 - 호환성 유지):</h4>
            <pre>
{
  "image_data": "base64로 인코딩된 이미지 데이터",
  "metadata": {
    "id": 1,
    "timestamp": 1620000000.0
  }
}</pre>
            <h4>응답:</h4>
            <pre>
{
  "ID": {
    "imageID": 1,
    "shipID": 1,
    "UserID": 1,
    "cameraId": 0
  },
  "timestamp_ns": 1620000000000000000,
  "time_stamps": [1620000001000000000, 1620000002000000000],
  "pose": {
    "position_m": [0.96, 0.54, 0.0],
    "quaternion": [0.0, 0.0, 0.0, 1.0],
    "zone": {
      "deck": 1,
      "compartment": "Main",
      "zone_id": 1
    }
  }
}</pre>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">GET</span> /api/delay/config</h3>
            <p>현재 지연 설정 조회 API</p>
            <h4>응답:</h4>
            <pre>
{
  "strategy": "FixedDelayStrategy",
  "params": {
    "delay_seconds": 1.0
  }
}</pre>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">POST</span> /api/delay/config</h3>
            <p>지연 설정 변경 API</p>
            <h4>요청 본문:</h4>
            <pre>
{
  "strategy": "FixedDelayStrategy",
  "params": {
    "delay_seconds": 1.0
  }
}</pre>
            <h4>응답:</h4>
            <pre>
{
  "message": "지연 설정이 변경되었습니다."
}</pre>
        </div>
        
        <h2>지연 시나리오 엔드포인트</h2>
        
        <div class="endpoint">
            <h3><span class="method">POST</span> /api/delay/fixed/{delay_seconds}</h3>
            <p>고정 지연 설정 API</p>
            <p>예: <code>POST /api/delay/fixed/1.0</code> - 1초 고정 지연 설정</p>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">POST</span> /api/delay/progressive-increase</h3>
            <p>점진적 증가 지연 설정 API</p>
            <h4>요청 본문 (선택적):</h4>
            <pre>
{
  "initial_delay": 0.0,
  "increment": 0.5,
  "interval": 5.0,
  "max_steps": 10
}</pre>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">POST</span> /api/delay/progressive-decrease</h3>
            <p>점진적 감소 지연 설정 API</p>
            <h4>요청 본문 (선택적):</h4>
            <pre>
{
  "initial_delay": 5.0,
  "decrement": 0.5,
  "interval": 5.0,
  "min_delay": 0.0
}</pre>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">POST</span> /api/delay/step</h3>
            <p>계단식 지연 설정 API</p>
            <h4>요청 본문 (선택적):</h4>
            <pre>
{
  "normal_delay": 0.0,
  "high_delay": 5.0,
  "normal_duration": 5.0,
  "high_duration": 5.0,
  "step_increment": 5.0,
  "total_duration": 300.0
}</pre>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">POST</span> /api/delay/no-response/{duration}</h3>
            <p>무응답 시뮬레이션 설정 API</p>
            <p>예: <code>POST /api/delay/no-response/10.0</code> - 10초 무응답 설정</p>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">POST</span> /api/delay/random</h3>
            <p>랜덤 지연 설정 API</p>
            <h4>요청 본문 (선택적):</h4>
            <pre>
{
  "min_delay": 0.5,
  "max_delay": 5.0,
  "change_interval": 5.0,
  "total_duration": 300.0
}</pre>
        </div>
        
        <h2>테스트 시나리오 엔드포인트</h2>
        
        <div class="endpoint">
            <h3><span class="method">POST</span> /api/delay/scenario/1?delay={seconds}</h3>
            <p>시나리오 1: 고정 지연 (0.2, 0.5, 1, 3, 5, 10초)</p>
            <p>예: <code>POST /api/delay/scenario/1?delay=1.0</code></p>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">POST</span> /api/delay/scenario/2</h3>
            <p>시나리오 2: 점진적 증가 지연 (초기 5초부터 0.5초씩 5초 간격으로 10단계 증가)</p>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">POST</span> /api/delay/scenario/3</h3>
            <p>시나리오 3: 점진적 감소 지연 (5000→0ms로 500ms씩 10단계 감소)</p>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">POST</span> /api/delay/scenario/4</h3>
            <p>시나리오 4: 계단식 지연 (5초 정상 5초 지연 5초 정상 10초 지연 5초 정상 15초 지연 5분간)</p>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">POST</span> /api/delay/scenario/5?duration={seconds}</h3>
            <p>시나리오 5: 무응답 (10, 30, 60초 무응답)</p>
            <p>예: <code>POST /api/delay/scenario/5?duration=10</code></p>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">POST</span> /api/delay/scenario/6</h3>
            <p>시나리오 6: 랜덤 지연 (5분간 0.5에서 5초를 랜덤하게 지연)</p>
        </div>
        
        <h2>지원하는 지연 전략</h2>
        <ul>
            <li><code>FixedDelayStrategy</code>: 고정 지연</li>
            <li><code>ProgressiveIncreaseDelayStrategy</code>: 점진적 증가 지연</li>
            <li><code>ProgressiveDecreaseDelayStrategy</code>: 점진적 감소 지연</li>
            <li><code>StepDelayStrategy</code>: 계단식 지연</li>
            <li><code>NoResponseDelayStrategy</code>: 무응답 시뮬레이션</li>
            <li><code>RandomDelayStrategy</code>: 랜덤 지연</li>
        </ul>
        
        <p>자세한 사용법은 <a href="https://github.com/yourusername/DigitalTwinLocTest">GitHub 저장소</a>를 참조하세요.</p>
        
        <h2>지연 시나리오 프로파일</h2>
        <div id="current-strategy" style="background-color: #4285F4; color: white; padding: 10px 15px; border-radius: 5px; margin-bottom: 20px; font-weight: bold;">
            현재 지연 전략: {delay_simulator.get_config()['strategy']}
        </div>
        <div class="charts-container" style="display: grid; grid-template-columns: 1fr 1fr; grid-gap: 20px;">
            <div>
                <h3>시나리오 1: 고정 지연</h3>
                <canvas id="scenario1Chart"></canvas>
            </div>
            <div>
                <h3>시나리오 2: 점진적 증가 지연</h3>
                <canvas id="scenario2Chart"></canvas>
            </div>
            <div>
                <h3>시나리오 3: 점진적 감소 지연</h3>
                <canvas id="scenario3Chart"></canvas>
            </div>
            <div>
                <h3>시나리오 4: 계단식 지연</h3>
                <canvas id="scenario4Chart"></canvas>
            </div>
            <div>
                <h3>시나리오 5: 무응답</h3>
                <canvas id="scenario5Chart"></canvas>
            </div>
            <div>
                <h3>시나리오 6: 랜덤 지연</h3>
                <canvas id="scenario6Chart"></canvas>
            </div>
        </div>
        
        <p><a href="/monitor" target="_blank" style="display: inline-block; padding: 10px 20px; background-color: #4285F4; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px;">최근 요청 모니터링 페이지 열기</a></p>
        
        <script>
            // 차트 생성 함수
            function createChart(canvasId, labels, data, label, color) {
                const ctx = document.getElementById(canvasId).getContext('2d');
                return new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: label,
                            data: data,
                            backgroundColor: color + '33', // 투명도 추가
                            borderColor: color,
                            borderWidth: 2,
                            fill: true,
                            tension: 0.1
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true,
                                title: {
                                    display: true,
                                    text: '지연 시간 (초)'
                                }
                            },
                            x: {
                                title: {
                                    display: true,
                                    text: '시간 (초)'
                                }
                            }
                        }
                    }
                });
            }
            
            // 시나리오 1: 고정 지연 (1초)
            const scenario1Labels = Array.from({length: 60}, (_, i) => i);
            const scenario1Data = Array.from({length: 60}, () => 1.0);
            createChart('scenario1Chart', scenario1Labels, scenario1Data, '고정 지연 (1초)', '#4285F4');
            
            // 시나리오 2: 점진적 증가 지연
            const scenario2Labels = Array.from({length: 60}, (_, i) => i);
            const scenario2Data = scenario2Labels.map(i => {
                const step = Math.floor(i / 5);
                return step <= 10 ? step * 0.5 : 5.0;
            });
            createChart('scenario2Chart', scenario2Labels, scenario2Data, '점진적 증가 지연', '#EA4335');
            
            // 시나리오 3: 점진적 감소 지연
            const scenario3Labels = Array.from({length: 60}, (_, i) => i);
            const scenario3Data = scenario3Labels.map(i => {
                const step = Math.floor(i / 5);
                return Math.max(0, 5.0 - step * 0.5);
            });
            createChart('scenario3Chart', scenario3Labels, scenario3Data, '점진적 감소 지연', '#FBBC05');
            
            // 시나리오 4: 계단식 지연
            const scenario4Labels = Array.from({length: 60}, (_, i) => i);
            const scenario4Data = scenario4Labels.map(i => {
                const cycle = i % 30;
                if (cycle < 5) return 0;
                else if (cycle < 10) return 5;
                else if (cycle < 15) return 0;
                else if (cycle < 20) return 10;
                else if (cycle < 25) return 0;
                else return 15;
            });
            createChart('scenario4Chart', scenario4Labels, scenario4Data, '계단식 지연', '#34A853');
            
            // 시나리오 5: 무응답 (10초)
            const scenario5Labels = Array.from({length: 60}, (_, i) => i);
            const scenario5Data = scenario5Labels.map(i => {
                return i >= 10 && i < 20 ? 10 : 0;
            });
            createChart('scenario5Chart', scenario5Labels, scenario5Data, '무응답 (10초)', '#673AB7');
            
            // 시나리오 6: 랜덤 지연
            const scenario6Labels = Array.from({length: 60}, (_, i) => i);
            const scenario6Data = [];
            let lastValue = 2.5;
            for (let i = 0; i < 60; i++) {
                if (i % 5 === 0) {
                    lastValue = 0.5 + Math.random() * 4.5;
                }
                scenario6Data.push(lastValue);
            }
            createChart('scenario6Chart', scenario6Labels, scenario6Data, '랜덤 지연', '#FF6D00');
            
            // 실시간 데이터 업데이트 (5초마다)
            // 그래프는 유지하면서 최근 요청 정보만 업데이트
            let updateTimer = null;
            
            function startUpdates() {
                updateTimer = setInterval(function() {
                    // 최근 요청 정보만 AJAX로 가져오기
                    fetch('/api/recent-requests')
                        .then(response => response.json())
                        .then(data => {
                            // 현재 지연 전략 업데이트
                            document.getElementById('current-strategy').textContent = 
                                '현재 지연 전략: ' + data.current_strategy;
                            
                            // 최근 요청 목록 업데이트
                            if(data.recent_requests_html) {
                                document.getElementById('recent-requests').innerHTML = 
                                    data.recent_requests_html;
                            }
                        })
                        .catch(error => console.error('Error fetching updates:', error));
                }, 5000);
            }
            
            // 페이지 로드 시 업데이트 시작
            startUpdates();
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

@api_bp.route('/image', methods=['POST'])
def upload_image():
    """
    이미지 업로드 및 처리 API
    
    클라이언트로부터 이미지를 수신하고, 처리 후 결과 데이터를 반환
    """
    global recent_requests
    
    try:
        # 요청 데이터 파싱
        image_data = request.json
        
        # 요청 시간 기록
        request_time = time.time()
        
        # 이미지 처리
        result = process_image(image_data)
        
        # 설정된 지연 적용
        delay_simulator.apply_delay()
        
        # PosePacket 객체 생성 (결과에서 복원)
        from app.models.pose_packet import PosePacket
        pose_packet = PosePacket.from_dict(result)
        
        # 출발 시간 설정 (서버에서 응답을 보내는 시간)
        pose_packet.set_departure_time()
        
        # 응답 데이터 생성
        response_data = pose_packet.to_dict()
        
        # 최근 요청 및 응답 정보 저장
        request_info = {
            'request_time': request_time,
            'request_data': image_data,
            'response_data': response_data,
            'delay_config': delay_simulator.get_config()
        }
        
        # 최근 요청 목록 업데이트 (최대 MAX_RECENT_REQUESTS개 유지)
        recent_requests.insert(0, request_info)
        if len(recent_requests) > MAX_RECENT_REQUESTS:
            recent_requests = recent_requests[:MAX_RECENT_REQUESTS]
        
        # 업데이트된 결과 반환
        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/delay/config', methods=['GET'])
def get_delay_config():
    """
    현재 지연 설정 조회 API
    """
    config = delay_simulator.get_config()
    return jsonify(config), 200

@api_bp.route('/delay/config', methods=['POST'])
def set_delay_config():
    """
    지연 설정 변경 API
    """
    try:
        config = request.json
        delay_simulator.set_strategy(config.get('strategy'), config.get('params', {}))
        return jsonify({"message": "지연 설정이 변경되었습니다."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# 지연 시나리오별 엔드포인트

@api_bp.route('/delay/fixed/<float:delay_seconds>', methods=['POST'])
def set_fixed_delay(delay_seconds):
    """
    고정 지연 설정 API
    
    Args:
        delay_seconds (float): 지연 시간(초)
    """
    try:
        delay_simulator.set_fixed_delay(delay_seconds)
        return jsonify({
            "message": f"고정 지연이 {delay_seconds}초로 설정되었습니다.",
            "config": delay_simulator.get_config()
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@api_bp.route('/delay/progressive-increase', methods=['POST'])
def set_progressive_increase_delay():
    """
    점진적 증가 지연 설정 API
    """
    try:
        data = request.json or {}
        delay_simulator.set_progressive_increase_delay(
            initial_delay=data.get('initial_delay', 0.0),
            increment=data.get('increment', 0.5),
            interval=data.get('interval', 5.0),
            max_steps=data.get('max_steps', 10)
        )
        return jsonify({
            "message": "점진적 증가 지연이 설정되었습니다.",
            "config": delay_simulator.get_config()
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@api_bp.route('/delay/progressive-decrease', methods=['POST'])
def set_progressive_decrease_delay():
    """
    점진적 감소 지연 설정 API
    """
    try:
        data = request.json or {}
        delay_simulator.set_progressive_decrease_delay(
            initial_delay=data.get('initial_delay', 5.0),
            decrement=data.get('decrement', 0.5),
            interval=data.get('interval', 5.0),
            min_delay=data.get('min_delay', 0.0)
        )
        return jsonify({
            "message": "점진적 감소 지연이 설정되었습니다.",
            "config": delay_simulator.get_config()
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@api_bp.route('/delay/step', methods=['POST'])
def set_step_delay():
    """
    계단식 지연 설정 API
    """
    try:
        data = request.json or {}
        delay_simulator.set_step_delay(
            normal_delay=data.get('normal_delay', 0.0),
            high_delay=data.get('high_delay', 5.0),
            normal_duration=data.get('normal_duration', 5.0),
            high_duration=data.get('high_duration', 5.0),
            step_increment=data.get('step_increment', 5.0),
            total_duration=data.get('total_duration', 300.0)
        )
        return jsonify({
            "message": "계단식 지연이 설정되었습니다.",
            "config": delay_simulator.get_config()
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@api_bp.route('/delay/no-response/<float:duration>', methods=['POST'])
def set_no_response(duration):
    """
    무응답 시뮬레이션 설정 API
    
    Args:
        duration (float): 무응답 지속 시간(초)
    """
    try:
        delay_simulator.set_no_response(duration)
        return jsonify({
            "message": f"무응답 시뮬레이션이 {duration}초로 설정되었습니다.",
            "config": delay_simulator.get_config()
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@api_bp.route('/delay/random', methods=['POST'])
def set_random_delay():
    """
    랜덤 지연 설정 API
    """
    try:
        data = request.json or {}
        delay_simulator.set_random_delay(
            min_delay=data.get('min_delay', 0.5),
            max_delay=data.get('max_delay', 5.0),
            change_interval=data.get('change_interval', 5.0),
            total_duration=data.get('total_duration', 300.0)
        )
        return jsonify({
            "message": "랜덤 지연이 설정되었습니다.",
            "config": delay_simulator.get_config()
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# 시나리오별 간편 엔드포인트 (기본 설정 사용)

@api_bp.route('/delay/scenario/1', methods=['POST'])
def set_scenario_1():
    """
    시나리오 1: 고정 지연 (0.2, 0.5, 1, 3, 5, 10초)
    """
    try:
        delay_seconds = float(request.args.get('delay', 1.0))
        if delay_seconds not in [0.2, 0.5, 1.0, 3.0, 5.0, 10.0]:
            delay_seconds = 1.0
        
        delay_simulator.set_fixed_delay(delay_seconds)
        return jsonify({
            "message": f"시나리오 1: 고정 지연이 {delay_seconds}초로 설정되었습니다.",
            "config": delay_simulator.get_config()
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@api_bp.route('/delay/scenario/2', methods=['POST'])
def set_scenario_2():
    """
    시나리오 2: 점진적 증가 지연 (초기 5초부터 0.5초씩 5초 간격으로 10단계 증가)
    """
    try:
        delay_simulator.set_progressive_increase_delay(
            initial_delay=0.0,
            increment=0.5,
            interval=5.0,
            max_steps=10
        )
        return jsonify({
            "message": "시나리오 2: 점진적 증가 지연이 설정되었습니다.",
            "config": delay_simulator.get_config()
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@api_bp.route('/delay/scenario/3', methods=['POST'])
def set_scenario_3():
    """
    시나리오 3: 점진적 감소 지연 (5000→0ms로 500ms씩 10단계 감소)
    """
    try:
        delay_simulator.set_progressive_decrease_delay(
            initial_delay=5.0,
            decrement=0.5,
            interval=5.0,
            min_delay=0.0
        )
        return jsonify({
            "message": "시나리오 3: 점진적 감소 지연이 설정되었습니다.",
            "config": delay_simulator.get_config()
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@api_bp.route('/delay/scenario/4', methods=['POST'])
def set_scenario_4():
    """
    시나리오 4: 계단식 지연 (5초 정상 5초 지연 5초 정상 10초 지연 5초 정상 15초 지연 5분간)
    """
    try:
        delay_simulator.set_step_delay(
            normal_delay=0.0,
            high_delay=5.0,
            normal_duration=5.0,
            high_duration=5.0,
            step_increment=5.0,
            total_duration=300.0
        )
        return jsonify({
            "message": "시나리오 4: 계단식 지연이 설정되었습니다.",
            "config": delay_simulator.get_config()
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@api_bp.route('/delay/scenario/5', methods=['POST'])
def set_scenario_5():
    """
    시나리오 5: 무응답 (10, 30, 60초 무응답)
    """
    try:
        duration = int(request.args.get('duration', 10))
        if duration not in [10, 30, 60]:
            duration = 10
        
        delay_simulator.set_no_response(duration)
        return jsonify({
            "message": f"시나리오 5: 무응답이 {duration}초로 설정되었습니다.",
            "config": delay_simulator.get_config()
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@api_bp.route('/delay/scenario/6', methods=['POST'])
def set_scenario_6():
    """
    시나리오 6: 랜덤 지연 (5분간 0.5에서 5초를 랜덤하게 지연)
    """
    try:
        delay_simulator.set_random_delay(
            min_delay=0.5,
            max_delay=5.0,
            change_interval=5.0,
            total_duration=300.0
        )
        return jsonify({
            "message": "시나리오 6: 랜덤 지연이 설정되었습니다.",
            "config": delay_simulator.get_config()
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@api_bp.route('/recent-requests', methods=['GET'])
def get_recent_requests():
    """
    최근 요청 정보 API
    
    AJAX를 통해 최근 요청 정보를 가져오기 위한 API
    """
    global recent_requests
    
    # 최근 요청 정보를 HTML로 변환
    recent_requests_html = ""
    if recent_requests:
        for i, req in enumerate(recent_requests):
            # 요청 시간 포맷팅
            request_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(req['request_time']))
            
            # ID 정보 추출
            id_info = None
            if 'ID' in req['request_data']:
                id_info = req['request_data']['ID']
            elif 'metadata' in req['request_data'] and 'id' in req['request_data']['metadata']:
                id_info = {'imageID': req['request_data']['metadata']['id']}
            else:
                id_info = {'imageID': 'Unknown'}
            
            # 포즈 정보 추출
            request_pose = None
            if 'pose' in req['request_data']:
                request_pose = req['request_data']['pose']
            else:
                request_pose = {'position_m': [0, 0, 0], 'quaternion': [0, 0, 0, 1]}
            
            response_pose = req['response_data']['pose']
            
            # 지연 정보 추출
            delay_config = req['delay_config']
            strategy_name = delay_config['strategy']
            delay_params = delay_config['params']
            
            # 시간 차이 계산
            time_arrive = req['response_data']['time_stamps'][0]
            time_depart = req['response_data']['time_stamps'][1]
            time_diff_ns = time_depart - time_arrive
            time_diff_s = time_diff_ns / 1_000_000_000
            
            recent_requests_html += f"""
            <div class="request-item">
                <h4>요청 {i+1} - {request_time_str}</h4>
                <div class="request-details">
                    <div class="request-id">
                        <h5>ID 정보</h5>
                        <pre>{json.dumps(id_info, indent=2, ensure_ascii=False)}</pre>
                    </div>
                    <div class="request-pose">
                        <h5>요청 포즈</h5>
                        <pre>{json.dumps(request_pose, indent=2, ensure_ascii=False)}</pre>
                    </div>
                    <div class="response-pose">
                        <h5>응답 포즈</h5>
                        <pre>{json.dumps(response_pose, indent=2, ensure_ascii=False)}</pre>
                    </div>
                    <div class="delay-info">
                        <h5>지연 정보</h5>
                        <p>전략: {strategy_name}</p>
                        <p>지연 시간: {time_diff_s:.6f}초</p>
                        <pre>{json.dumps(delay_params, indent=2, ensure_ascii=False)}</pre>
                    </div>
                </div>
            </div>
            """
    else:
        recent_requests_html = "<p>아직 요청이 없습니다.</p>"
    
    # 현재 지연 전략 정보 가져오기
    strategy_name = delay_simulator.get_config()['strategy']
    
    return jsonify({
        'current_strategy': strategy_name,
        'recent_requests_html': recent_requests_html
    })

@root_bp.route('/monitor')
def monitor():
    """
    최근 요청 모니터링 페이지
    """
    global recent_requests
    
    # 최근 요청 정보를 HTML로 변환
    recent_requests_html = ""
    if recent_requests:
        for i, req in enumerate(recent_requests):
            # 요청 시간 포맷팅
            request_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(req['request_time']))
            
            # ID 정보 추출
            id_info = None
            if 'ID' in req['request_data']:
                id_info = req['request_data']['ID']
            elif 'metadata' in req['request_data'] and 'id' in req['request_data']['metadata']:
                id_info = {'imageID': req['request_data']['metadata']['id']}
            else:
                id_info = {'imageID': 'Unknown'}
            
            # 포즈 정보 추출
            request_pose = None
            if 'pose' in req['request_data']:
                request_pose = req['request_data']['pose']
            else:
                request_pose = {'position_m': [0, 0, 0], 'quaternion': [0, 0, 0, 1]}
            
            response_pose = req['response_data']['pose']
            
            # 지연 정보 추출
            delay_config = req['delay_config']
            strategy_name = delay_config['strategy']
            delay_params = delay_config['params']
            
            # 시간 차이 계산
            time_arrive = req['response_data']['time_stamps'][0]
            time_depart = req['response_data']['time_stamps'][1]
            time_diff_ns = time_depart - time_arrive
            time_diff_s = time_diff_ns / 1_000_000_000
            
            recent_requests_html += f"""
            <div class="request-item">
                <h4>요청 {i+1} - {request_time_str}</h4>
                <div class="request-details">
                    <div class="request-id">
                        <h5>ID 정보</h5>
                        <pre>{json.dumps(id_info, indent=2, ensure_ascii=False)}</pre>
                    </div>
                    <div class="request-pose">
                        <h5>요청 포즈</h5>
                        <pre>{json.dumps(request_pose, indent=2, ensure_ascii=False)}</pre>
                    </div>
                    <div class="response-pose">
                        <h5>응답 포즈</h5>
                        <pre>{json.dumps(response_pose, indent=2, ensure_ascii=False)}</pre>
                    </div>
                    <div class="delay-info">
                        <h5>지연 정보</h5>
                        <p>전략: {strategy_name}</p>
                        <p>지연 시간: {time_diff_s:.6f}초</p>
                        <pre>{json.dumps(delay_params, indent=2, ensure_ascii=False)}</pre>
                    </div>
                </div>
            </div>
            """
    else:
        recent_requests_html = "<p>아직 요청이 없습니다.</p>"
    
    # 현재 지연 전략 정보 가져오기
    strategy_name = delay_simulator.get_config()['strategy']
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>요청 모니터링 - DigitalTwinLocTest API Server</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                max-width: 1200px;
                margin: 0 auto;
                background-color: #f5f5f5;
            }}
            h1 {{
                color: #333;
                border-bottom: 1px solid #ddd;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #444;
                margin-top: 20px;
            }}
            pre {{
                background-color: #f5f5f5;
                padding: 10px;
                border-radius: 5px;
                overflow-x: auto;
            }}
            .request-item {{
                margin-bottom: 30px;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 15px;
                background-color: white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .request-item h4 {{
                margin-top: 0;
                border-bottom: 1px solid #eee;
                padding-bottom: 10px;
                color: #4285F4;
            }}
            .request-details {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                grid-gap: 15px;
            }}
            .request-id, .request-pose, .response-pose, .delay-info {{
                background-color: #f9f9f9;
                padding: 15px;
                border-radius: 5px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }}
            .request-id h5, .request-pose h5, .response-pose h5, .delay-info h5 {{
                margin-top: 0;
                color: #555;
                border-bottom: 1px solid #eee;
                padding-bottom: 5px;
            }}
            .current-strategy {{
                background-color: #4285F4;
                color: white;
                padding: 10px 15px;
                border-radius: 5px;
                margin-bottom: 20px;
                font-weight: bold;
            }}
            .back-link {{
                display: inline-block;
                margin-top: 20px;
                padding: 10px 15px;
                background-color: #555;
                color: white;
                text-decoration: none;
                border-radius: 5px;
            }}
            .back-link:hover {{
                background-color: #333;
            }}
        </style>
    </head>
    <body>
        <h1>최근 요청 모니터링</h1>
        
        <div class="current-strategy">
            현재 지연 전략: {strategy_name}
        </div>
        
        <div id="recent-requests">
            {recent_requests_html}
        </div>
        
        <a href="/" class="back-link">메인 페이지로 돌아가기</a>
        
        <script>
            // 2초마다 페이지 새로고침
            setTimeout(function() {{
                location.reload();
            }}, 2000);
        </script>
    </body>
    </html>
    """
    
    return render_template_string(html)
