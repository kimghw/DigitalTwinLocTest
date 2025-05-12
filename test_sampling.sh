#!/bin/bash

# 1초에 1개씩 최대 100개까지 이미지 업로드 API 호출 테스트

echo "1초에 1개씩 최대 100개까지 이미지 업로드 API 호출 테스트 시작"
echo "현재 지연 전략: $(curl -s http://localhost:5000/api/delay/config | jq -r '.strategy')"
echo ""

for i in {1..100}
do
    echo "요청 $i 전송 중..."
    curl -s -X POST -H "Content-Type: application/json" -d @test_frame_packet.json http://localhost:5000/api/image > /dev/null
    echo "요청 $i 완료"
    sleep 1
done

echo "테스트 완료"
