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
            
            // 이미지 데이터 설정 (실제로는 카메라에서 캡처한 이미지 사용)
            // framePacket.SetImageFromTexture(captureTexture);
            
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
