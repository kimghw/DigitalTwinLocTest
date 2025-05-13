using System;
using System.Collections.Generic;
using UnityEngine;
using System.Text;

namespace DigitalTwinLoc
{
    /// <summary>
    /// 이미지 식별 정보를 포함하는 클래스
    /// </summary>
    [Serializable]
    public class IdBlock
    {
        public int imageID;
        public int shipID;
        public int UserID;
        public int cameraId;
    }

    /// <summary>
    /// 카메라 정보를 포함하는 클래스
    /// </summary>
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

    /// <summary>
    /// 위치 영역 정보를 포함하는 클래스
    /// </summary>
    [Serializable]
    public class ZoneBlock
    {
        public int deck;
        public string compartment = "";
        public int zone_id;
    }

    /// <summary>
    /// 위치 및 자세 정보를 포함하는 클래스
    /// </summary>
    [Serializable]
    public class PoseBlock
    {
        public float[] position_m = new float[3];
        public float[] quaternion = new float[4] { 0, 0, 0, 1 };
        public ZoneBlock zone = new ZoneBlock();
    }

    /// <summary>
    /// 유니티 앱에서 서버로 전송되는 이미지 데이터를 표현하는 클래스
    /// </summary>
    [Serializable]
    public class FramePacket
    {
        public IdBlock ID = new IdBlock();
        public long timestamp_ns;
        public CameraBlock camera = new CameraBlock();
        public PoseBlock pose = new PoseBlock();
        public string image = "";

        /// <summary>
        /// 이미지 데이터를 Base64 문자열로 변환
        /// </summary>
        /// <param name="texture">변환할 텍스처</param>
        public void SetImageFromTexture(Texture2D texture)
        {
            if (texture == null)
                return;

            byte[] jpgBytes = texture.EncodeToJPG(90);
            image = Convert.ToBase64String(jpgBytes);
        }

        /// <summary>
        /// 현재 시간을 나노초로 설정
        /// </summary>
        public void SetCurrentTimestamp()
        {
            timestamp_ns = DateTime.UtcNow.Ticks * 100; // Ticks는 100나노초 단위
        }
    }

    /// <summary>
    /// 서버에서 클라이언트로 반환되는 처리된 데이터를 표현하는 클래스
    /// </summary>
    [Serializable]
    public class PosePacket
    {
        public IdBlock ID = new IdBlock();
        public long timestamp_ns;
        public long[] time_stamps = new long[2];
        public PoseBlock pose = new PoseBlock();

        /// <summary>
        /// 지연 시간 계산 (초 단위)
        /// </summary>
        /// <returns>지연 시간(초)</returns>
        public float GetDelaySeconds()
        {
            if (time_stamps == null || time_stamps.Length < 2)
                return 0f;

            return (time_stamps[1] - time_stamps[0]) / 1_000_000_000f;
        }
    }

    /// <summary>
    /// 기존 형식의 이미지 데이터를 표현하는 클래스 (이전 버전과의 호환성 유지)
    /// </summary>
    [Serializable]
    public class LegacyImage
    {
        public string image_data = "";
        public Dictionary<string, object> metadata = new Dictionary<string, object>();

        /// <summary>
        /// 이미지 데이터를 Base64 문자열로 변환
        /// </summary>
        /// <param name="texture">변환할 텍스처</param>
        public void SetImageFromTexture(Texture2D texture)
        {
            if (texture == null)
                return;

            byte[] jpgBytes = texture.EncodeToJPG(90);
            image_data = Convert.ToBase64String(jpgBytes);
        }

        /// <summary>
        /// 메타데이터 설정
        /// </summary>
        /// <param name="id">이미지 ID</param>
        /// <param name="shipID">선박 ID</param>
        /// <param name="userID">사용자 ID</param>
        /// <param name="cameraId">카메라 ID</param>
        public void SetMetadata(int id, int shipID, int userID, int cameraId)
        {
            metadata["id"] = id;
            metadata["shipID"] = shipID;
            metadata["UserID"] = userID;
            metadata["cameraId"] = cameraId;
            metadata["timestamp"] = DateTime.UtcNow.ToOADate();
        }
    }

    /// <summary>
    /// 여러 FramePacket을 저장하기 위한 래퍼 클래스
    /// </summary>
    [Serializable]
    public class FramePacketArray
    {
        public List<FramePacket> packets = new List<FramePacket>();
    }

    /// <summary>
    /// 여러 PosePacket을 저장하기 위한 래퍼 클래스
    /// </summary>
    [Serializable]
    public class PosePacketArray
    {
        public List<PosePacket> packets = new List<PosePacket>();
    }
}
