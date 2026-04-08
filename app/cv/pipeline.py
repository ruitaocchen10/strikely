import os
import urllib.request
import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python as mp_tasks
from mediapipe.tasks.python import vision as mp_vision
from app.schemas import (
    SessionAnalysis, Strike, QualityFlag, StrikeType, Hand, FlagType, Severity
)

_MODEL_PATH = os.path.join(os.path.dirname(__file__), "pose_landmarker.task")
_MODEL_URL  = (
    "https://storage.googleapis.com/mediapipe-models/"
    "pose_landmarker/pose_landmarker_full/float16/1/pose_landmarker_full.task"
)

def _ensure_model() -> str:
    if not os.path.exists(_MODEL_PATH):
        print(f"[pipeline] Downloading pose landmarker model to {_MODEL_PATH}...")
        urllib.request.urlretrieve(_MODEL_URL, _MODEL_PATH)
        print("[pipeline] Model downloaded.")
    return _MODEL_PATH

# MediaPipe landmark indices
NOSE               = 0
L_SHOULDER,R_SHOULDER = 11, 12
L_ELBOW,  R_ELBOW  = 13, 14
L_WRIST,  R_WRIST  = 15, 16
L_HIP,    R_HIP    = 23, 24
L_ANKLE,  R_ANKLE  = 27, 28

VELOCITY_THRESHOLD    = 0.05   # m/frame — minimum wrist speed to open a window
MIN_PEAK_VELOCITY     = 0.10   # m/frame — peak within window must clear this bar
MIN_STRIKE_FRAMES     = 6      # ~200ms at 30fps — ignore short twitches
MAX_STRIKE_FRAMES     = 20     # ~667ms at 30fps — discard sustained arm movement
INTER_STRIKE_COOLDOWN = 20     # frames to ignore a hand after a strike lands


def detect_local_stance(landmarks_per_frame: dict, before_frame: int, window: int = 30) -> Hand:
    left_z, right_z = [], []
    for f in range(max(0, before_frame - window), before_frame):
        lm = landmarks_per_frame.get(f)
        if lm and (lm[L_ANKLE].visibility or 1) >= 0.5 and (lm[R_ANKLE].visibility or 1) >= 0.5:
            left_z.append(lm[L_ANKLE].z)
            right_z.append(lm[R_ANKLE].z)
    if not left_z:
        return Hand.LEFT  # fallback to orthodox
    return Hand.LEFT if np.mean(left_z) < np.mean(right_z) else Hand.RIGHT


def classify_strike(
    landmarks_per_frame: dict,
    start_frame: int,
    peak_frame: int,
    hand: Hand,
) -> StrikeType:
    lead_hand = detect_local_stance(landmarks_per_frame, start_frame)
    wrist_idx = L_WRIST if hand == Hand.LEFT else R_WRIST

    start_lm = landmarks_per_frame.get(start_frame)
    peak_lm  = landmarks_per_frame.get(peak_frame)
    if not start_lm or not peak_lm:
        return StrikeType.JAB  # safe fallback

    sw = start_lm[wrist_idx]
    pw = peak_lm[wrist_idx]

    delta_x = abs(pw.x - sw.x)
    delta_y = sw.y - pw.y        # positive = wrist moved UP (y is top-to-bottom)

    # Uppercut: wrist travels clearly upward
    if delta_y > 0.06:
        return StrikeType.UPPERCUT

    # Hook: displacement is mostly horizontal, not forward
    total = delta_x + abs(delta_y)
    if total > 0 and delta_x / total > 0.65:
        return StrikeType.HOOK

    # Cross vs Jab: lead hand throws a jab, rear hand throws a cross.
    # Hip rotation is a confirming signal — a cross with low visibility
    # on the ankles (stance fallback) can still be caught this way.
    if hand != lead_hand:
        return StrikeType.CROSS

    start_hip_width = abs(start_lm[R_HIP].x - start_lm[L_HIP].x)
    peak_hip_width  = abs(peak_lm[R_HIP].x  - peak_lm[L_HIP].x)
    hip_rotation    = abs(peak_hip_width - start_hip_width)

    if hip_rotation > 0.04:
        return StrikeType.CROSS

    return StrikeType.JAB


def _angle_at_joint(a, b, c) -> float:
    """Angle in degrees at joint b, between vectors b→a and b→c."""
    v1 = np.array([a.x - b.x, a.y - b.y, a.z - b.z])
    v2 = np.array([c.x - b.x, c.y - b.y, c.z - b.z])
    cos_a = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
    return float(np.degrees(np.arccos(np.clip(cos_a, -1.0, 1.0))))


def compute_flags(landmarks_per_frame: dict, strikes: list[Strike]) -> list[QualityFlag]:
    flags = []

    for strike in strikes:
        lm_start = landmarks_per_frame.get(strike.start_frame)
        lm_peak  = landmarks_per_frame.get(strike.peak_frame)
        if not lm_start or not lm_peak:
            continue

        striking_elbow = L_ELBOW   if strike.hand == Hand.LEFT else R_ELBOW
        striking_shoulder = L_SHOULDER if strike.hand == Hand.LEFT else R_SHOULDER
        striking_wrist = L_WRIST   if strike.hand == Hand.LEFT else R_WRIST
        guard_wrist    = R_WRIST   if strike.hand == Hand.LEFT else L_WRIST

        # --- GUARD_DROPPED ---
        # Non-striking wrist should stay near nose level. In world coords
        # y-axis points up, so a positive gap means the wrist fell below the nose.
        guard_gap = lm_peak[NOSE].y - lm_peak[guard_wrist].y
        if guard_gap > 0.05:
            severity = Severity.HIGH if guard_gap > 0.12 else (
                       Severity.MEDIUM if guard_gap > 0.08 else Severity.LOW)
            side = "Left" if strike.hand == Hand.RIGHT else "Right"
            flags.append(QualityFlag(
                strike_id=strike.id,
                flag_type=FlagType.GUARD_DROPPED,
                severity=severity,
                description=f"{side} guard dropped {guard_gap * 100:.0f}cm below nose level",
            ))

        # --- CHIN_EXPOSED ---
        # Head rising during a punch (nose moves upward from start to peak).
        chin_rise = lm_peak[NOSE].y - lm_start[NOSE].y
        if chin_rise > 0.02:
            severity = Severity.HIGH if chin_rise > 0.06 else (
                       Severity.MEDIUM if chin_rise > 0.04 else Severity.LOW)
            flags.append(QualityFlag(
                strike_id=strike.id,
                flag_type=FlagType.CHIN_EXPOSED,
                severity=severity,
                description=f"Head rose {chin_rise * 100:.0f}cm during punch, exposing chin",
            ))

        # --- OVEREXTENDED ---
        # Elbow angle at peak: full lockout strains the joint.
        elbow_angle = _angle_at_joint(
            lm_peak[striking_shoulder],
            lm_peak[striking_elbow],
            lm_peak[striking_wrist],
        )
        if elbow_angle > 160:
            severity = Severity.HIGH if elbow_angle > 175 else (
                       Severity.MEDIUM if elbow_angle > 168 else Severity.LOW)
            flags.append(QualityFlag(
                strike_id=strike.id,
                flag_type=FlagType.OVEREXTENDED,
                severity=severity,
                description=f"Elbow locked at {elbow_angle:.0f}° — risk of hyperextension",
            ))

        # --- HIP_ROTATION_LIMITED (crosses only) ---
        # On a cross the rear hip should drive forward. Measure how much the
        # hip-to-hip width changes from start to peak in world-space x.
        if strike.type == StrikeType.CROSS:
            start_hip_width = abs(lm_start[R_HIP].x - lm_start[L_HIP].x)
            peak_hip_width  = abs(lm_peak[R_HIP].x  - lm_peak[L_HIP].x)
            rotation_delta  = abs(peak_hip_width - start_hip_width)
            if rotation_delta < 0.03:
                severity = Severity.HIGH if rotation_delta < 0.01 else (
                           Severity.MEDIUM if rotation_delta < 0.02 else Severity.LOW)
                flags.append(QualityFlag(
                    strike_id=strike.id,
                    flag_type=FlagType.HIP_ROTATION_LIMITED,
                    severity=severity,
                    description=f"Hip rotation on cross only {rotation_delta * 100:.0f}cm — drive from the hips",
                ))

    return flags


def compute_strikes(landmarks_per_frame: dict, fps: float) -> list[Strike]:
    strikes = []
    strike_id = 0

    for hand, wrist_idx in [(Hand.LEFT, L_WRIST), (Hand.RIGHT, R_WRIST)]:
        frames = sorted(landmarks_per_frame.keys())

        # Build velocity curve: distance wrist moved between consecutive frames
        velocities = {}
        for i in range(1, len(frames)):
            prev_f, curr_f = frames[i - 1], frames[i]
            prev = landmarks_per_frame[prev_f][wrist_idx]
            curr = landmarks_per_frame[curr_f][wrist_idx]
            velocities[curr_f] = np.sqrt(
                (curr.x - prev.x) ** 2 +
                (curr.y - prev.y) ** 2 +
                (curr.z - prev.z) ** 2
            )

        # Scan velocity curve for contiguous high-speed windows
        in_strike = False
        window = []
        last_strike_end = -INTER_STRIKE_COOLDOWN  # allow strikes from frame 0

        for f in frames[1:]:
            if velocities.get(f, 0) >= VELOCITY_THRESHOLD:
                in_strike = True
                window.append(f)
            else:
                if in_strike:
                    peak_frame   = max(window, key=lambda f: velocities[f])
                    peak_vel     = velocities[peak_frame]
                    window_len   = len(window)
                    in_cooldown  = window[0] - last_strike_end < INTER_STRIKE_COOLDOWN

                    if (MIN_STRIKE_FRAMES <= window_len <= MAX_STRIKE_FRAMES
                            and peak_vel >= MIN_PEAK_VELOCITY
                            and not in_cooldown):
                        strike_type = classify_strike(
                            landmarks_per_frame, window[0], peak_frame, hand
                        )
                        strikes.append(Strike(
                            id=f"s{strike_id}",
                            type=strike_type,
                            hand=hand,
                            timestamp=round(window[0] / fps, 3),
                            start_frame=window[0],
                            peak_frame=peak_frame,
                            end_frame=window[-1],
                        ))
                        strike_id += 1
                        last_strike_end = window[-1]

                    in_strike = False
                    window = []

    strikes.sort(key=lambda s: s.start_frame)
    return strikes


def analyze_video(video_path: str) -> SessionAnalysis:
    cap = cv2.VideoCapture(video_path)

    fps         = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    base_options = mp_tasks.BaseOptions(model_asset_path=_ensure_model())
    options = mp_vision.PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=mp_vision.RunningMode.VIDEO,
        min_pose_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    landmarks_per_frame = {}
    frame_idx = 0

    with mp_vision.PoseLandmarker.create_from_options(options) as landmarker:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            rgb        = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image   = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            timestamp  = int(frame_idx * (1000 / fps))
            result     = landmarker.detect_for_video(mp_image, timestamp)

            if result.pose_world_landmarks:
                landmarks_per_frame[frame_idx] = result.pose_world_landmarks[0]

            frame_idx += 1

    cap.release()

    strikes = compute_strikes(landmarks_per_frame, fps)
    flags   = compute_flags(landmarks_per_frame, strikes)

    return SessionAnalysis(
        video_path=video_path,
        fps=fps,
        frame_count=frame_count,
        duration_seconds=frame_count / fps,
        detected_strikes=strikes,
        quality_flags=flags,
    )
