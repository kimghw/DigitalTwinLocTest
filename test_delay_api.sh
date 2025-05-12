#!/bin/bash

# 이미지 업로드 API 테스트 (0.1초 간격으로 10번 요청)
echo "이미지 업로드 API 테스트 (0.1초 간격으로 10번 요청)"
for i in {1..10}
do
    echo "요청 $i 전송 중..."
    curl -s -X POST -H "Content-Type: application/json" -d @test_frame_packet.json http://localhost:5000/api/image > /dev/null
    echo "요청 $i 완료"
    sleep 0.1
done
echo "이미지 업로드 API 테스트 완료"
echo ""

# 고정 지연 테스트
echo "고정 지연 테스트 (1초)"
curl -X POST http://localhost:5000/api/delay/fixed/1.0
echo ""
echo "이미지 업로드 API 테스트 (0.1초 간격으로 10번 요청)"
for i in {1..10}
do
    echo "요청 $i 전송 중..."
    curl -s -X POST -H "Content-Type: application/json" -d @test_frame_packet.json http://localhost:5000/api/image > /dev/null
    echo "요청 $i 완료"
    sleep 0.1
done
echo "이미지 업로드 API 테스트 완료"
echo ""

# 점진적 증가 지연 테스트
echo "점진적 증가 지연 테스트"
curl -X POST -H "Content-Type: application/json" -d '{"initial_delay": 0.0, "increment": 0.1, "interval": 1.0, "max_steps": 10}' http://localhost:5000/api/delay/progressive-increase
echo ""
echo "이미지 업로드 API 테스트 (0.1초 간격으로 10번 요청)"
for i in {1..10}
do
    echo "요청 $i 전송 중..."
    curl -s -X POST -H "Content-Type: application/json" -d @test_frame_packet.json http://localhost:5000/api/image > /dev/null
    echo "요청 $i 완료"
    sleep 0.1
done
echo "이미지 업로드 API 테스트 완료"
echo ""

# 점진적 감소 지연 테스트
echo "점진적 감소 지연 테스트"
curl -X POST -H "Content-Type: application/json" -d '{"initial_delay": 1.0, "decrement": 0.1, "interval": 1.0, "min_delay": 0.0}' http://localhost:5000/api/delay/progressive-decrease
echo ""
echo "이미지 업로드 API 테스트 (0.1초 간격으로 10번 요청)"
for i in {1..10}
do
    echo "요청 $i 전송 중..."
    curl -s -X POST -H "Content-Type: application/json" -d @test_frame_packet.json http://localhost:5000/api/image > /dev/null
    echo "요청 $i 완료"
    sleep 0.1
done
echo "이미지 업로드 API 테스트 완료"
echo ""

# 계단식 지연 테스트
echo "계단식 지연 테스트"
curl -X POST -H "Content-Type: application/json" -d '{"normal_delay": 0.0, "high_delay": 1.0, "normal_duration": 1.0, "high_duration": 1.0, "step_increment": 0.5, "total_duration": 10.0}' http://localhost:5000/api/delay/step
echo ""
echo "이미지 업로드 API 테스트 (0.1초 간격으로 10번 요청)"
for i in {1..10}
do
    echo "요청 $i 전송 중..."
    curl -s -X POST -H "Content-Type: application/json" -d @test_frame_packet.json http://localhost:5000/api/image > /dev/null
    echo "요청 $i 완료"
    sleep 0.1
done
echo "이미지 업로드 API 테스트 완료"
echo ""

# 랜덤 지연 테스트
echo "랜덤 지연 테스트"
curl -X POST -H "Content-Type: application/json" -d '{"min_delay": 0.1, "max_delay": 1.0, "change_interval": 1.0, "total_duration": 10.0}' http://localhost:5000/api/delay/random
echo ""
echo "이미지 업로드 API 테스트 (0.1초 간격으로 10번 요청)"
for i in {1..10}
do
    echo "요청 $i 전송 중..."
    curl -s -X POST -H "Content-Type: application/json" -d @test_frame_packet.json http://localhost:5000/api/image > /dev/null
    echo "요청 $i 완료"
    sleep 0.1
done
echo "이미지 업로드 API 테스트 완료"
echo ""

# 시나리오 1 테스트
echo "시나리오 1 테스트 (고정 지연 1초)"
curl -X POST http://localhost:5000/api/delay/scenario/1?delay=1.0
echo ""
echo "이미지 업로드 API 테스트 (0.1초 간격으로 10번 요청)"
for i in {1..10}
do
    echo "요청 $i 전송 중..."
    curl -s -X POST -H "Content-Type: application/json" -d @test_frame_packet.json http://localhost:5000/api/image > /dev/null
    echo "요청 $i 완료"
    sleep 0.1
done
echo "이미지 업로드 API 테스트 완료"
echo ""

# 시나리오 2 테스트
echo "시나리오 2 테스트 (점진적 증가 지연)"
curl -X POST http://localhost:5000/api/delay/scenario/2
echo ""
echo "이미지 업로드 API 테스트 (0.1초 간격으로 10번 요청)"
for i in {1..10}
do
    echo "요청 $i 전송 중..."
    curl -s -X POST -H "Content-Type: application/json" -d @test_frame_packet.json http://localhost:5000/api/image > /dev/null
    echo "요청 $i 완료"
    sleep 0.1
done
echo "이미지 업로드 API 테스트 완료"
echo ""

# 시나리오 3 테스트
echo "시나리오 3 테스트 (점진적 감소 지연)"
curl -X POST http://localhost:5000/api/delay/scenario/3
echo ""
echo "이미지 업로드 API 테스트 (0.1초 간격으로 10번 요청)"
for i in {1..10}
do
    echo "요청 $i 전송 중..."
    curl -s -X POST -H "Content-Type: application/json" -d @test_frame_packet.json http://localhost:5000/api/image > /dev/null
    echo "요청 $i 완료"
    sleep 0.1
done
echo "이미지 업로드 API 테스트 완료"
echo ""

# 시나리오 4 테스트
echo "시나리오 4 테스트 (계단식 지연)"
curl -X POST http://localhost:5000/api/delay/scenario/4
echo ""
echo "이미지 업로드 API 테스트 (0.1초 간격으로 10번 요청)"
for i in {1..10}
do
    echo "요청 $i 전송 중..."
    curl -s -X POST -H "Content-Type: application/json" -d @test_frame_packet.json http://localhost:5000/api/image > /dev/null
    echo "요청 $i 완료"
    sleep 0.1
done
echo "이미지 업로드 API 테스트 완료"
echo ""

# 시나리오 6 테스트
echo "시나리오 6 테스트 (랜덤 지연)"
curl -X POST http://localhost:5000/api/delay/scenario/6
echo ""
echo "이미지 업로드 API 테스트 (0.1초 간격으로 10번 요청)"
for i in {1..10}
do
    echo "요청 $i 전송 중..."
    curl -s -X POST -H "Content-Type: application/json" -d @test_frame_packet.json http://localhost:5000/api/image > /dev/null
    echo "요청 $i 완료"
    sleep 0.1
done
echo "이미지 업로드 API 테스트 완료"
echo ""

echo "모든 테스트 완료"
