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
        
        <div style="margin-bottom: 20px;">
            <a href="/unity-code" class="back-link" style="background-color: #4CAF50; margin-right: 10px;">유니티 코드 페이지</a>
            <a href="/monitor" class="back-link" style="background-color: #2196F3;">모니터링 페이지</a>
        </div>
        
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
        
        <p>자세한 사용법은 <a href="https://github.com/kimghw/DigitalTwinLocTest.git">GitHub 저장소</a>를 참조하세요.</p>
        
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

@root_bp.route('/unity-code/download/json-serializer')
def download_json_serializer():
    """
    UnityJsonSerializer.cs 파일 다운로드
    """
    try:
        with open('UnityJsonSerializer.cs', 'r') as file:
            content = file.read()
        
        from flask import Response
        response = Response(content, mimetype='text/plain')
        response.headers['Content-Disposition'] = 'attachment; filename=UnityJsonSerializer.cs'
        return response
    except Exception as e:
        return f"파일을 찾을 수 없습니다: {str(e)}", 404

@root_bp.route('/unity-code/download/data-models')
def download_data_models():
    """
    UnityDataModels.cs 파일 다운로드
    """
    try:
        with open('UnityDataModels.cs', 'r') as file:
            content = file.read()
        
        from flask import Response
        response = Response(content, mimetype='text/plain')
        response.headers['Content-Disposition'] = 'attachment; filename=UnityDataModels.cs'
        return response
    except Exception as e:
        return f"파일을 찾을 수 없습니다: {str(e)}", 404

@root_bp.route('/unity-code')
def unity_code():
    """
    유니티 코드 페이지
    
    유니티에서 사용할 데이터 타입과 JSON 직렬화 코드를 제공
    """
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>유니티 코드 - DigitalTwinLocTest API Server</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                max-width: 1200px;
                margin: 0 auto;
                background-color: #f5f5f5;
            }
            h1, h2, h3 {
                color: #333;
                border-bottom: 1px solid #ddd;
                padding-bottom: 10px;
            }
            pre {
                background-color: #f0f0f0;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
                border: 1px solid #ddd;
                font-family: Consolas, Monaco, 'Andale Mono', monospace;
                font-size: 14px;
                line-height: 1.4;
            }
            .code-block {
                margin-bottom: 30px;
                background-color: white;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .back-link {
                display: inline-block;
                margin-top: 20px;
                padding: 10px 15px;
                background-color: #4285F4;
                color: white;
                text-decoration: none;
                border-radius: 5px;
            }
            .back-link:hover {
                background-color: #3367d6;
            }
            .note {
                background-color: #fffde7;
                padding: 15px;
                border-left: 4px solid #ffd600;
                margin-bottom: 20px;
            }
            .tab-container {
                margin-bottom: 20px;
            }
            .tab {
                overflow: hidden;
                border: 1px solid #ccc;
                background-color: #f1f1f1;
                border-radius: 5px 5px 0 0;
            }
            .tab button {
                background-color: inherit;
                float: left;
                border: none;
                outline: none;
                cursor: pointer;
                padding: 14px 16px;
                transition: 0.3s;
                font-size: 16px;
            }
            .tab button:hover {
                background-color: #ddd;
            }
            .tab button.active {
                background-color: #4285F4;
                color: white;
            }
            .tabcontent {
                display: none;
                padding: 20px;
                border: 1px solid #ccc;
                border-top: none;
                border-radius: 0 0 5px 5px;
                background-color: white;
            }
            .tabcontent.active {
                display: block;
            }
        </style>
    </head>
    <body>
        <h1>유니티 코드 - DigitalTwinLocTest API Server</h1>
        
        <div class="note">
            <p>이 페이지는 유니티 클라이언트에서 서버와 통신하기 위한 데이터 타입과 JSON 직렬화 코드를 제공합니다.</p>
            <p>아래 코드를 유니티 프로젝트에 추가하여 서버와 통신할 수 있습니다.</p>
            <p>자세한 사용법은 <a href="https://github.com/kimghw/DigitalTwinLocTest.git" target="_blank">GitHub 저장소</a>를 참조하세요.</p>
            <p>
                <a href="/unity-code/download/data-models" class="download-link" style="display: inline-block; padding: 10px 15px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px; margin-top: 10px; margin-right: 10px;">UnityDataModels.cs 파일 다운로드</a>
                <a href="/unity-code/download/json-serializer" class="download-link" style="display: inline-block; padding: 10px 15px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px; margin-top: 10px;">UnityJsonSerializer.cs 파일 다운로드</a>
            </p>
        </div>
        
        <div class="tab-container">
            <div class="tab">
                <button class="tablinks active" onclick="openTab(event, 'DataModels')">데이터 모델</button>
                <button class="tablinks" onclick="openTab(event, 'ApiClient')">API 클라이언트</button>
                <button class="tablinks" onclick="openTab(event, 'JsonSerializer')">JSON 직렬화</button>
                <button class="tablinks" onclick="openTab(event, 'Usage')">사용 예제</button>
            </div>
            
            <div id="DataModels" class="tabcontent active">
                <h2>데이터 모델 클래스</h2>
                
                <div class="code-block">
                    <h3>데이터 모델 (C#)</h3>
                    <pre>
using System;
using System.Collections.Generic;
using UnityEngine;
using System.Text;

namespace DigitalTwinLoc
{
    [Serializable]
    public class IdBlock
    {
        public int imageID;
        public int shipID;
        public int UserID;
        public int cameraId;
    }

    [Serializable]
    public class CameraBlock
    {
        public int width;
        public int height;
        public string format = "jpeg";
        public float[] focal_px = new float[2];
        public float[] principal_px = new float[2];
        public int exposure_us;
        public int iso;
    }

    [Serializable]
    public class ZoneBlock
    {
        public int deck;
        public string compartment = "";
        public int zone_id;
    }

    [Serializable]
    public class PoseBlock
    {
        public float[] position_m = new float[3];
        public float[] quaternion = new float[4] { 0, 0, 0, 1 };
        public ZoneBlock zone = new ZoneBlock();
    }

    [Serializable]
    public class FramePacket
    {
        public IdBlock ID = new IdBlock();
        public long timestamp_ns;
        public CameraBlock camera = new CameraBlock();
        public PoseBlock pose = new PoseBlock();
        public string image = "";

        // 이미지 데이터를 Base64 문자열로 변환
        public void SetImageFromTexture(Texture2D texture)
        {
            if (texture == null)
                return;

            byte[] jpgBytes = texture.EncodeToJPG(90);
            image = Convert.ToBase64String(jpgBytes);
        }

        // 현재 시간을 나노초로 설정
        public void SetCurrentTimestamp()
        {
            timestamp_ns = DateTime.UtcNow.Ticks * 100; // Ticks는 100나노초 단위
        }
    }

    [Serializable]
    public class PosePacket
    {
        public IdBlock ID = new IdBlock();
        public long timestamp_ns;
        public long[] time_stamps = new long[2];
        public PoseBlock pose = new PoseBlock();

        // 지연 시간 계산 (초 단위)
        public float GetDelaySeconds()
        {
            if (time_stamps == null || time_stamps.Length < 2)
                return 0f;

            return (time_stamps[1] - time_stamps[0]) / 1_000_000_000f;
        }
    }
}
</pre>
                </div>
            </div>
            
            <div id="ApiClient" class="tabcontent">
                <h2>API 클라이언트 클래스</h2>
                
                <div class="code-block">
                    <h3>API 클라이언트 (C#)</h3>
                    <pre>
using System;
using System.Collections;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;

namespace DigitalTwinLoc
{
    public class ApiClient : MonoBehaviour
    {
        [Header("서버 설정")]
        public string serverUrl = "http://localhost:5000";
        
        [Header("상태")]
        public bool isConnected = false;
        public float lastResponseTime = 0f;
        public float lastDelayTime = 0f;
        
        // 이벤트 델리게이트
        public delegate void OnPoseResponseDelegate(PosePacket response);
        public event OnPoseResponseDelegate OnPoseResponse;
        
        public delegate void OnErrorDelegate(string errorMessage);
        public event OnErrorDelegate OnError;
        
        // 싱글톤 인스턴스
        private static ApiClient _instance;
        public static ApiClient Instance
        {
            get
            {
                if (_instance == null)
                {
                    GameObject go = new GameObject("ApiClient");
                    _instance = go.AddComponent<ApiClient>();
                    DontDestroyOnLoad(go);
                }
                return _instance;
            }
        }
        
        private void Awake()
        {
            if (_instance != null && _instance != this)
            {
                Destroy(gameObject);
                return;
            }
            
            _instance = this;
            DontDestroyOnLoad(gameObject);
        }
        
        // 이미지 전송 메서드
        public void SendImage(FramePacket framePacket)
        {
            StartCoroutine(SendImageCoroutine(framePacket));
        }
        
        // 이미지 전송 코루틴
        private IEnumerator SendImageCoroutine(FramePacket framePacket)
        {
            string jsonData = JsonUtility.ToJson(framePacket);
            
            using (UnityWebRequest request = new UnityWebRequest(serverUrl + "/api/image", "POST"))
            {
                byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonData);
                request.uploadHandler = new UploadHandlerRaw(bodyRaw);
                request.downloadHandler = new DownloadHandlerBuffer();
                request.SetRequestHeader("Content-Type", "application/json");
                
                lastResponseTime = Time.time;
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.ConnectionError || 
                    request.result == UnityWebRequest.Result.ProtocolError)
                {
                    isConnected = false;
                    OnError?.Invoke($"Error: {request.error}");
                    Debug.LogError($"API Error: {request.error}");
                }
                else
                {
                    isConnected = true;
                    string responseJson = request.downloadHandler.text;
                    
                    try
                    {
                        PosePacket response = JsonUtility.FromJson<PosePacket>(responseJson);
                        lastDelayTime = response.GetDelaySeconds();
                        OnPoseResponse?.Invoke(response);
                    }
                    catch (Exception e)
                    {
                        OnError?.Invoke($"JSON 파싱 오류: {e.Message}");
                        Debug.LogError($"JSON 파싱 오류: {e.Message}");
                    }
                }
            }
        }
        
        // 지연 설정 변경 메서드
        public void SetDelayConfig(string strategy, Dictionary<string, object> parameters)
        {
            StartCoroutine(SetDelayConfigCoroutine(strategy, parameters));
        }
        
        // 지연 설정 변경 코루틴
        private IEnumerator SetDelayConfigCoroutine(string strategy, Dictionary<string, object> parameters)
        {
            // 딕셔너리를 JSON으로 변환하기 위한 간단한 클래스
            [Serializable]
            class DelayConfig
            {
                public string strategy;
                public string paramsJson;
                
                public string ToJson()
                {
                    return $"{{\"strategy\":\"{strategy}\",\"params\":{paramsJson}}}";
                }
            }
            
            // 파라미터를 JSON 문자열로 변환
            string paramsJson = "{";
            int count = 0;
            foreach (var kvp in parameters)
            {
                if (count > 0) paramsJson += ",";
                
                if (kvp.Value is string)
                    paramsJson += $"\"{kvp.Key}\":\"{kvp.Value}\"";
                else if (kvp.Value is bool)
                    paramsJson += $"\"{kvp.Key}\":{kvp.Value.ToString().ToLower()}";
                else
                    paramsJson += $"\"{kvp.Key}\":{kvp.Value}";
                
                count++;
            }
            paramsJson += "}";
            
            DelayConfig config = new DelayConfig
            {
                strategy = strategy,
                paramsJson = paramsJson
            };
            
            using (UnityWebRequest request = new UnityWebRequest(serverUrl + "/api/delay/config", "POST"))
            {
                byte[] bodyRaw = Encoding.UTF8.GetBytes(config.ToJson());
                request.uploadHandler = new UploadHandlerRaw(bodyRaw);
                request.downloadHandler = new DownloadHandlerBuffer();
                request.SetRequestHeader("Content-Type", "application/json");
                
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.ConnectionError || 
                    request.result == UnityWebRequest.Result.ProtocolError)
                {
                    Debug.LogError($"지연 설정 변경 오류: {request.error}");
                }
                else
                {
                    Debug.Log("지연 설정이 변경되었습니다.");
                }
            }
        }
        
        // 시나리오 설정 메서드
        public void SetScenario(int scenarioNumber, float parameter = 0f)
        {
            StartCoroutine(SetScenarioCoroutine(scenarioNumber, parameter));
        }
        
        // 시나리오 설정 코루틴
        private IEnumerator SetScenarioCoroutine(int scenarioNumber, float parameter)
        {
            string url = serverUrl + $"/api/delay/scenario/{scenarioNumber}";
            
            // 시나리오 1과 5는 추가 파라미터가 필요
            if (scenarioNumber == 1)
                url += $"?delay={parameter}";
            else if (scenarioNumber == 5)
                url += $"?duration={parameter}";
            
            using (UnityWebRequest request = new UnityWebRequest(url, "POST"))
            {
                request.downloadHandler = new DownloadHandlerBuffer();
                
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.ConnectionError || 
                    request.result == UnityWebRequest.Result.ProtocolError)
                {
                    Debug.LogError($"시나리오 설정 오류: {request.error}");
                }
                else
                {
                    Debug.Log($"시나리오 {scenarioNumber}이(가) 설정되었습니다.");
                }
            }
        }
    }
}
</pre>
                </div>
            </div>
            
            <div id="JsonSerializer" class="tabcontent">
                <h2>JSON 직렬화 및 역직렬화</h2>
                
                <div class="code-block">
                    <h3>JSON 파일 관리 (C#)</h3>
                    <pre>
using System;
using System.IO;
using System.Text;
using UnityEngine;
using System.Collections.Generic;

namespace DigitalTwinLoc
{
    /// <summary>
    /// 유니티에서 JSON 직렬화 및 역직렬화를 처리하는 유틸리티 클래스
    /// </summary>
    public static class JsonFileManager
    {
        // 기본 저장 경로 (유니티 프로젝트의 persistentDataPath)
        private static string DefaultSavePath => Application.persistentDataPath;

        #region 직렬화 (객체 -> JSON -> 파일)

        /// <summary>
        /// 객체를 JSON 문자열로 직렬화
        /// </summary>
        /// <typeparam name="T">직렬화할 객체 타입</typeparam>
        /// <param name="obj">직렬화할 객체</param>
        /// <returns>JSON 문자열</returns>
        public static string Serialize<T>(T obj) where T : class
        {
            try
            {
                return JsonUtility.ToJson(obj, true); // true: 보기 좋게 포맷팅
            }
            catch (Exception ex)
            {
                Debug.LogError($"직렬화 오류: {ex.Message}");
                return string.Empty;
            }
        }

        /// <summary>
        /// 객체를 JSON 파일로 저장
        /// </summary>
        /// <typeparam name="T">저장할 객체 타입</typeparam>
        /// <param name="obj">저장할 객체</param>
        /// <param name="fileName">파일 이름 (확장자 포함)</param>
        /// <param name="directory">저장 디렉토리 (기본값: Application.persistentDataPath)</param>
        /// <returns>성공 여부</returns>
        public static bool SaveToFile<T>(T obj, string fileName, string directory = null) where T : class
        {
            try
            {
                // 디렉토리 설정
                string saveDir = directory ?? DefaultSavePath;
                
                // 디렉토리가 없으면 생성
                if (!Directory.Exists(saveDir))
                {
                    Directory.CreateDirectory(saveDir);
                }
                
                // 전체 파일 경로
                string filePath = Path.Combine(saveDir, fileName);
                
                // 객체를 JSON으로 직렬화
                string jsonData = Serialize(obj);
                if (string.IsNullOrEmpty(jsonData))
                {
                    return false;
                }
                
                // 파일에 저장
                File.WriteAllText(filePath, jsonData, Encoding.UTF8);
                
                Debug.Log($"파일 저장 완료: {filePath}");
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"파일 저장 오류: {ex.Message}");
                return false;
            }
        }

        #endregion

        #region 역직렬화 (파일 -> JSON -> 객체)

        /// <summary>
        /// JSON 문자열을 객체로 역직렬화
        /// </summary>
        /// <typeparam name="T">역직렬화할 객체 타입</typeparam>
        /// <param name="jsonData">JSON 문자열</param>
        /// <returns>역직렬화된 객체</returns>
        public static T Deserialize<T>(string jsonData) where T : class
        {
            try
            {
                if (string.IsNullOrEmpty(jsonData))
                {
                    Debug.LogError("역직렬화할 JSON 데이터가 비어 있습니다.");
                    return null;
                }
                
                return JsonUtility.FromJson<T>(jsonData);
            }
            catch (Exception ex)
            {
                Debug.LogError($"역직렬화 오류: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// JSON 파일에서 객체 불러오기
        /// </summary>
        /// <typeparam name="T">불러올 객체 타입</typeparam>
        /// <param name="fileName">파일 이름 (확장자 포함)</param>
        /// <param name="directory">파일 디렉토리 (기본값: Application.persistentDataPath)</param>
        /// <returns>불러온 객체</returns>
        public static T LoadFromFile<T>(string fileName, string directory = null) where T : class
        {
            try
            {
                // 디렉토리 설정
                string loadDir = directory ?? DefaultSavePath;
                
                // 전체 파일 경로
                string filePath = Path.Combine(loadDir, fileName);
                
                // 파일이 존재하는지 확인
                if (!File.Exists(filePath))
                {
                    Debug.LogError($"파일을 찾을 수 없습니다: {filePath}");
                    return null;
                }
                
                // 파일에서 JSON 데이터 읽기
                string jsonData = File.ReadAllText(filePath, Encoding.UTF8);
                
                // JSON 데이터를 객체로 역직렬화
                T obj = Deserialize<T>(jsonData);
                
                Debug.Log($"파일 로드 완료: {filePath}");
                return obj;
            }
            catch (Exception ex)
            {
                Debug.LogError($"파일 로드 오류: {ex.Message}");
                return null;
            }
        }

        #endregion
    }

    /// <summary>
    /// 데이터 저장 및 로드 예제 클래스
    /// </summary>
    public class DataManager : MonoBehaviour
    {
        // 파일 이름 상수
        private const string FRAME_PACKET_FILE = "frame_packet.json";
        private const string POSE_PACKET_FILE = "pose_packet.json";
        
        /// <summary>
        /// FramePacket을 JSON 파일로 저장
        /// </summary>
        /// <param name="framePacket">저장할 FramePacket 객체</param>
        /// <param name="fileName">파일 이름 (기본값: "frame_packet.json")</param>
        /// <returns>성공 여부</returns>
        public bool SaveFramePacket(FramePacket framePacket, string fileName = FRAME_PACKET_FILE)
        {
            return JsonFileManager.SaveToFile(framePacket, fileName);
        }
        
        /// <summary>
        /// JSON 파일에서 FramePacket 불러오기
        /// </summary>
        /// <param name="fileName">파일 이름 (기본값: "frame_packet.json")</param>
        /// <returns>불러온 FramePacket 객체</returns>
        public FramePacket LoadFramePacket(string fileName = FRAME_PACKET_FILE)
        {
            return JsonFileManager.LoadFromFile<FramePacket>(fileName);
        }
        
        /// <summary>
        /// PosePacket을 JSON 파일로 저장
        /// </summary>
        /// <param name="posePacket">저장할 PosePacket 객체</param>
        /// <param name="fileName">파일 이름 (기본값: "pose_packet.json")</param>
        /// <returns>성공 여부</returns>
        public bool SavePosePacket(PosePacket posePacket, string fileName = POSE_PACKET_FILE)
        {
            return JsonFileManager.SaveToFile(posePacket, fileName);
        }
        
        /// <summary>
        /// JSON 파일에서 PosePacket 불러오기
        /// </summary>
        /// <param name="fileName">파일 이름 (기본값: "pose_packet.json")</param>
        /// <returns>불러온 PosePacket 객체</returns>
        public PosePacket LoadPosePacket(string fileName = POSE_PACKET_FILE)
        {
            return JsonFileManager.LoadFromFile<PosePacket>(fileName);
        }
        
        /// <summary>
        /// 사용 예제: FramePacket 생성 및 저장
        /// </summary>
        public void ExampleSaveFramePacket()
        {
            // FramePacket 생성
            FramePacket framePacket = new FramePacket();
            
            // ID 설정
            framePacket.ID.imageID = 12345;
            framePacket.ID.shipID = 1;
            framePacket.ID.UserID = 1;
            framePacket.ID.cameraId = 0;
            
            // 타임스탬프 설정
            framePacket.SetCurrentTimestamp();
            
            // 카메라 정보 설정
            framePacket.camera.width = 1920;
            framePacket.camera.height = 1080;
            framePacket.camera.format = "jpeg";
            framePacket.camera.focal_px[0] = 1000.0f;
            framePacket.camera.focal_px[1] = 1000.0f;
            framePacket.camera.principal_px[0] = 960.0f;
            framePacket.camera.principal_px[1] = 540.0f;
            
            // 포즈 정보 설정
            framePacket.pose.position_m[0] = 1.0f;
            framePacket.pose.position_m[1] = 2.0f;
            framePacket.pose.position_m[2] = 3.0f;
            framePacket.pose.quaternion[0] = 0.0f;
            framePacket.pose.quaternion[1] = 0.0f;
            framePacket.pose.quaternion[2] = 0.0f;
            framePacket.pose.quaternion[3] = 1.0f;
            framePacket.pose.zone.deck = 1;
            framePacket.pose.zone.compartment = "Main";
            framePacket.pose.zone.zone_id = 1;
            
            // 파일로 저장
            bool success = SaveFramePacket(framePacket);
            
            if (success)
            {
                Debug.Log("FramePacket이 성공적으로 저장되었습니다.");
                
                // 저장된 JSON 출력
                string jsonData = JsonFileManager.Serialize(framePacket);
                Debug.Log("저장된 JSON 데이터:");
                Debug.Log(jsonData);
            }
        }
        
        /// <summary>
        /// 사용 예제: FramePacket 불러오기
        /// </summary>
        public void ExampleLoadFramePacket()
        {
            // 파일에서 FramePacket 불러오기
            FramePacket loadedPacket = LoadFramePacket();
            
            if (loadedPacket != null)
            {
                Debug.Log("FramePacket이 성공적으로 로드되었습니다.");
                Debug.Log($"이미지 ID: {loadedPacket.ID.imageID}");
                Debug.Log($"타임스탬프: {loadedPacket.timestamp_ns}");
                Debug.Log($"위치: X={loadedPacket.pose.position_m[0]}, Y={loadedPacket.pose.position_m[1]}, Z={loadedPacket.pose.position_m[2]}");
            }
        }
        
        /// <summary>
        /// 사용 예제: 여러 FramePacket을 배열로 저장
        /// </summary>
        public void ExampleSaveMultipleFramePackets()
        {
            // 여러 FramePacket을 저장하기 위한 래퍼 클래스
            [Serializable]
            class FramePacketArray
            {
                public List<FramePacket> packets = new List<FramePacket>();
            }
            
            // 래퍼 객체 생성
            FramePacketArray packetArray = new FramePacketArray();
            
            // 여러 FramePacket 생성 및 추가
            for (int i = 0; i < 5; i++)
            {
                FramePacket packet = new FramePacket();
                packet.ID.imageID = 1000 + i;
                packet.SetCurrentTimestamp();
                packet.pose.position_m[0] = i * 1.0f;
                packet.pose.position_m[1] = i * 2.0f;
                packet.pose.position_m[2] = i * 3.0f;
                
                packetArray.packets.Add(packet);
            }
            
            // 배열을 파일로 저장
            bool success = JsonFileManager.SaveToFile(packetArray, "frame_packets_array.json");
            
            if (success)
            {
                Debug.Log($"{packetArray.packets.Count}개의 FramePacket이 성공적으로 저장되었습니다.");
            }
        }
        
        /// <summary>
        /// 사용 예제: 여러 FramePacket 불러오기
        /// </summary>
        public void ExampleLoadMultipleFramePackets()
        {
            // 여러 FramePacket을 불러오기 위한 래퍼 클래스
            [Serializable]
            class FramePacketArray
            {
                public List<FramePacket> packets = new List<FramePacket>();
            }
            
            // 파일에서 배열 불러오기
            FramePacketArray loadedArray = JsonFileManager.LoadFromFile<FramePacketArray>("frame_packets_array.json");
            
            if (loadedArray != null && loadedArray.packets != null)
            {
                Debug.Log($"{loadedArray.packets.Count}개의 FramePacket이 성공적으로 로드되었습니다.");
                
                // 각 패킷 정보 출력
                for (int i = 0; i < loadedArray.packets.Count; i++)
                {
                    FramePacket packet = loadedArray.packets[i];
                    Debug.Log($"패킷 {i}: ID={packet.ID.imageID}, 위치=({packet.pose.position_m[0]}, {packet.pose.position_m[1]}, {packet.pose.position_m[2]})");
                }
            }
        }
    }
}
</pre>
                </div>
            </div>
            
            <div id="Usage" class="tabcontent">
                <h2>사용 예제</h2>
                
                <div class="code-block">
                    <h3>기본 사용법 (C#)</h3>
                    <pre>
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using DigitalTwinLoc;

public class ImageSender : MonoBehaviour
{
    [Header("카메라 설정")]
    public Camera captureCamera;
    public int captureWidth = 1280;
    public int captureHeight = 720;
    
    [Header("UI 요소")]
    public Text statusText;
    public Text delayText;
    public RawImage previewImage;
    
    [Header("전송 설정")]
    public float sendInterval = 1.0f;
    public bool autoSend = true;
    
    private float nextSendTime = 0f;
    private Texture2D captureTexture;
    
    void Start()
    {
        // 캡처 텍스처 초기화
        captureTexture = new Texture2D(captureWidth, captureHeight, TextureFormat.RGB24, false);
        
        // API 클라이언트 이벤트 등록
        ApiClient.Instance.OnPoseResponse += OnPoseReceived;
        ApiClient.Instance.OnError += OnApiError;
        
        // 서버 URL 설정
        ApiClient.Instance.serverUrl = "http://localhost:5000";
    }
    
    void Update()
    {
        // 상태 텍스트 업데이트
        if (statusText != null)
        {
            statusText.text = ApiClient.Instance.isConnected ? 
                "상태: 연결됨" : "상태: 연결 안됨";
            
            statusText.color = ApiClient.Instance.isConnected ? 
                Color.green : Color.red;
        }
        
        // 지연 시간 텍스트 업데이트
        if (delayText != null)
        {
            delayText.text = $"지연 시간: {ApiClient.Instance.lastDelayTime * 1000:F1}ms";
        }
        
        // 자동 전송 모드인 경우 일정 간격으로 이미지 전송
        if (autoSend && Time.time >= nextSendTime)
        {
            CaptureAndSendImage();
            nextSendTime = Time.time + sendInterval;
        }
    }
    
    // 이미지 캡처 및 전송
    public void CaptureAndSendImage()
    {
        StartCoroutine(CaptureAndSendCoroutine());
    }
    
    private IEnumerator CaptureAndSendCoroutine()
    {
        // 현재 카메라 뷰를 텍스처에 렌더링
        RenderTexture renderTexture = new RenderTexture(captureWidth, captureHeight, 24);
        captureCamera.targetTexture = renderTexture;
        captureCamera.Render();
        
        RenderTexture.active = renderTexture;
        captureTexture.ReadPixels(new Rect(0, 0, captureWidth, captureHeight), 0, 0);
        captureTexture.Apply();
        
        captureCamera.targetTexture = null;
        RenderTexture.active = null;
        Destroy(renderTexture);
        
        // 미리보기 이미지 업데이트
        if (previewImage != null)
        {
            previewImage.texture = captureTexture;
        }
        
        // 프레임 패킷 생성
        FramePacket framePacket = new FramePacket();
        
        // ID 설정
        framePacket.ID.imageID = Random.Range(1, 10000);
        framePacket.ID.shipID = 1;
        framePacket.ID.UserID = 1;
        framePacket.ID.cameraId = 0;
        
        // 타임스탬프 설정
        framePacket.SetCurrentTimestamp();
        
        // 카메라 정보 설정
        framePacket.camera.width = captureWidth;
        framePacket.camera.height = captureHeight;
        framePacket.camera.format = "jpeg";
        framePacket.camera.focal_px[0] = 1000.0f;
        framePacket.camera.focal_px[1] = 1000.0f;
        framePacket.camera.principal_px[0] = captureWidth / 2.0f;
        framePacket.camera.principal_px[1] = captureHeight / 2.0f;
        
        // 포즈 정보 설정
        Transform cameraTransform = captureCamera.transform;
        
        // 위치 설정 (미터 단위)
        framePacket.pose.position_m[0] = cameraTransform.position.x;
        framePacket.pose.position_m[1] = cameraTransform.position.y;
        framePacket.pose.position_m[2] = cameraTransform.position.z;
        
        // 회전 설정 (쿼터니언)
        framePacket.pose.quaternion[0] = cameraTransform.rotation.x;
        framePacket.pose.quaternion[1] = cameraTransform.rotation.y;
        framePacket.pose.quaternion[2] = cameraTransform.rotation.z;
        framePacket.pose.quaternion[3] = cameraTransform.rotation.w;
        
        // 영역 정보 설정
        framePacket.pose.zone.deck = 1;
        framePacket.pose.zone.compartment = "Main";
        framePacket.pose.zone.zone_id = 1;
        
        // 이미지 데이터 설정
        framePacket.SetImageFromTexture(captureTexture);
        
        // 서버로 전송
        ApiClient.Instance.SendImage(framePacket);
        
        yield return null;
    }
    
    // 포즈 응답 수신 처리
    private void OnPoseReceived(PosePacket posePacket)
    {
        Debug.Log($"포즈 수신: X={posePacket.pose.position_m[0]}, Y={posePacket.pose.position_m[1]}, Z={posePacket.pose.position_m[2]}");
        
        // 여기에서 수신된 포즈 데이터를 활용하는 코드 작성
        // 예: 가상 객체 위치 업데이트, UI 표시 등
    }
    
    // API 오류 처리
    private void OnApiError(string errorMessage)
    {
        Debug.LogError($"API 오류: {errorMessage}");
    }
    
    // 지연 시나리오 설정 메서드들
    public void SetFixedDelay(float delaySeconds)
    {
        ApiClient.Instance.SetScenario(1, delaySeconds);
    }
    
    public void SetProgressiveIncreaseDelay()
    {
        ApiClient.Instance.SetScenario(2);
    }
    
    public void SetProgressiveDecreaseDelay()
    {
        ApiClient.Instance.SetScenario(3);
    }
    
    public void SetStepDelay()
    {
        ApiClient.Instance.SetScenario(4);
    }
    
    public void SetNoResponseDelay(float durationSeconds)
    {
        ApiClient.Instance.SetScenario(5, durationSeconds);
    }
    
    public void SetRandomDelay()
    {
        ApiClient.Instance.SetScenario(6);
    }
}
</pre>
                </div>
            </div>
        </div>
        
        <p>자세한 사용법은 <a href="https://github.com/kimghw/DigitalTwinLocTest.git" target="_blank">GitHub 저장소</a>를 참조하세요.</p>
        
        <a href="/" class="back-link">메인 페이지로 돌아가기</a>
        
        <script>
            // 탭 기능 구현
            function openTab(evt, tabName) {
                var i, tabcontent, tablinks;
                
                // 모든 탭 콘텐츠 숨기기
                tabcontent = document.getElementsByClassName("tabcontent");
                for (i = 0; i < tabcontent.length; i++) {
                    tabcontent[i].className = tabcontent[i].className.replace(" active", "");
                }
                
                // 모든 탭 버튼 비활성화
                tablinks = document.getElementsByClassName("tablinks");
                for (i = 0; i < tablinks.length; i++) {
                    tablinks[i].className = tablinks[i].className.replace(" active", "");
                }
                
                // 선택한 탭 활성화
                document.getElementById(tabName).className += " active";
                evt.currentTarget.className += " active";
            }
        </script>
    </body>
    </html>
    """
    return html

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
            // 5초마다 페이지 새로고침
            setTimeout(function() {{
                location.reload();
            }}, 5000);
            
            // 페이지 로드 시간 표시
            document.addEventListener('DOMContentLoaded', function() {{
                const now = new Date();
                const timeString = now.toLocaleTimeString();
                const dateString = now.toLocaleDateString();
                
                const timeDisplay = document.createElement('div');
                timeDisplay.style.position = 'fixed';
                timeDisplay.style.top = '10px';
                timeDisplay.style.right = '10px';
                timeDisplay.style.padding = '5px 10px';
                timeDisplay.style.backgroundColor = '#333';
                timeDisplay.style.color = 'white';
                timeDisplay.style.borderRadius = '5px';
                timeDisplay.style.fontSize = '12px';
                timeDisplay.innerHTML = '마지막 업데이트: ' + dateString + ' ' + timeString;
                
                document.body.appendChild(timeDisplay);
            }});
        </script>
    </body>
    </html>
    """
    
    return render_template_string(html)
