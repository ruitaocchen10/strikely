from app.schemas import (
    SessionAnalysis, Strike, QualityFlag,
    StrikeType, Hand, FlagType, Severity,
)

MOCK_SESSION = SessionAnalysis(
    video_path="mock/shadow_boxing_3min.mp4",
    fps=30.0,
    frame_count=5400,
    duration_seconds=180.0,
    detected_strikes=[
        Strike(id="s1",  type=StrikeType.JAB,       hand=Hand.LEFT,  timestamp=4.2,   start_frame=114, peak_frame=118, end_frame=122),
        Strike(id="s2",  type=StrikeType.CROSS,      hand=Hand.RIGHT, timestamp=4.8,   start_frame=132, peak_frame=136, end_frame=141),
        Strike(id="s3",  type=StrikeType.JAB,        hand=Hand.LEFT,  timestamp=8.1,   start_frame=231, peak_frame=235, end_frame=239),
        Strike(id="s4",  type=StrikeType.CROSS,      hand=Hand.RIGHT, timestamp=8.7,   start_frame=249, peak_frame=254, end_frame=259),
        Strike(id="s5",  type=StrikeType.HOOK,       hand=Hand.LEFT,  timestamp=9.3,   start_frame=267, peak_frame=272, end_frame=278),
        Strike(id="s6",  type=StrikeType.JAB,        hand=Hand.LEFT,  timestamp=15.0,  start_frame=448, peak_frame=452, end_frame=456),
        Strike(id="s7",  type=StrikeType.CROSS,      hand=Hand.RIGHT, timestamp=15.6,  start_frame=466, peak_frame=471, end_frame=476),
        Strike(id="s8",  type=StrikeType.UPPERCUT,   hand=Hand.RIGHT, timestamp=16.2,  start_frame=484, peak_frame=489, end_frame=494),
        Strike(id="s9",  type=StrikeType.JAB,        hand=Hand.LEFT,  timestamp=22.4,  start_frame=670, peak_frame=674, end_frame=678),
        Strike(id="s10", type=StrikeType.JAB,        hand=Hand.LEFT,  timestamp=23.0,  start_frame=688, peak_frame=692, end_frame=696),
        Strike(id="s11", type=StrikeType.CROSS,      hand=Hand.RIGHT, timestamp=23.5,  start_frame=703, peak_frame=708, end_frame=714),
        Strike(id="s12", type=StrikeType.HOOK,       hand=Hand.RIGHT, timestamp=24.1,  start_frame=721, peak_frame=727, end_frame=733),
        Strike(id="s13", type=StrikeType.JAB,        hand=Hand.LEFT,  timestamp=31.8,  start_frame=952, peak_frame=956, end_frame=960),
        Strike(id="s14", type=StrikeType.CROSS,      hand=Hand.RIGHT, timestamp=32.4,  start_frame=970, peak_frame=975, end_frame=981),
        Strike(id="s15", type=StrikeType.JAB,        hand=Hand.LEFT,  timestamp=45.2,  start_frame=1354, peak_frame=1358, end_frame=1362),
        Strike(id="s16", type=StrikeType.CROSS,      hand=Hand.RIGHT, timestamp=45.9,  start_frame=1375, peak_frame=1380, end_frame=1386),
        Strike(id="s17", type=StrikeType.HOOK,       hand=Hand.LEFT,  timestamp=46.5,  start_frame=1393, peak_frame=1399, end_frame=1405),
        Strike(id="s18", type=StrikeType.UPPERCUT,   hand=Hand.LEFT,  timestamp=47.0,  start_frame=1408, peak_frame=1413, end_frame=1419),
        Strike(id="s19", type=StrikeType.JAB,        hand=Hand.LEFT,  timestamp=60.3,  start_frame=1807, peak_frame=1811, end_frame=1815),
        Strike(id="s20", type=StrikeType.CROSS,      hand=Hand.RIGHT, timestamp=60.9,  start_frame=1825, peak_frame=1830, end_frame=1836),
        Strike(id="s21", type=StrikeType.JAB,        hand=Hand.LEFT,  timestamp=90.1,  start_frame=2701, peak_frame=2705, end_frame=2709),
        Strike(id="s22", type=StrikeType.CROSS,      hand=Hand.RIGHT, timestamp=90.7,  start_frame=2719, peak_frame=2724, end_frame=2730),
        Strike(id="s23", type=StrikeType.HOOK,       hand=Hand.LEFT,  timestamp=91.3,  start_frame=2737, peak_frame=2743, end_frame=2749),
        Strike(id="s24", type=StrikeType.JAB,        hand=Hand.LEFT,  timestamp=120.5, start_frame=3613, peak_frame=3617, end_frame=3621),
        Strike(id="s25", type=StrikeType.CROSS,      hand=Hand.RIGHT, timestamp=121.1, start_frame=3631, peak_frame=3636, end_frame=3642),
    ],
    quality_flags=[
        # Guard drops on jabs (most common issue)
        QualityFlag(strike_id="s1",  flag_type=FlagType.GUARD_DROPPED,        severity=Severity.HIGH,   description="Right hand dropped well below chin level at full extension — guard open for a counter right hand."),
        QualityFlag(strike_id="s3",  flag_type=FlagType.GUARD_DROPPED,        severity=Severity.MEDIUM, description="Right hand dipped below chin during extension. Minor but consistent pattern emerging."),
        QualityFlag(strike_id="s6",  flag_type=FlagType.GUARD_DROPPED,        severity=Severity.HIGH,   description="Right hand dropped significantly. Guard was open for over 4 frames at peak extension."),
        QualityFlag(strike_id="s9",  flag_type=FlagType.GUARD_DROPPED,        severity=Severity.MEDIUM, description="Right hand dipped below chin at extension. Recurring issue on jabs."),
        QualityFlag(strike_id="s13", flag_type=FlagType.GUARD_DROPPED,        severity=Severity.LOW,    description="Slight guard dip on right hand. Improved compared to earlier in session."),
        QualityFlag(strike_id="s15", flag_type=FlagType.GUARD_DROPPED,        severity=Severity.MEDIUM, description="Guard hand dropped during jab. Issue persisting into second half of session."),
        QualityFlag(strike_id="s19", flag_type=FlagType.GUARD_DROPPED,        severity=Severity.LOW,    description="Minor guard dip. Showing gradual improvement across session."),

        # Chin exposure on crosses
        QualityFlag(strike_id="s2",  flag_type=FlagType.CHIN_EXPOSED,         severity=Severity.HIGH,   description="Head rose and tilted back during cross — chin fully exposed at peak extension."),
        QualityFlag(strike_id="s7",  flag_type=FlagType.CHIN_EXPOSED,         severity=Severity.HIGH,   description="Significant head rise on cross. Chin exposed for 5 frames at peak."),
        QualityFlag(strike_id="s11", flag_type=FlagType.CHIN_EXPOSED,         severity=Severity.MEDIUM, description="Moderate chin exposure on cross. Head rising with the rotation."),
        QualityFlag(strike_id="s14", flag_type=FlagType.CHIN_EXPOSED,         severity=Severity.MEDIUM, description="Chin exposed during cross extension. Consistent with earlier pattern."),
        QualityFlag(strike_id="s20", flag_type=FlagType.CHIN_EXPOSED,         severity=Severity.LOW,    description="Slight chin rise on cross. Noticeable improvement from start of session."),

        # Hip rotation on crosses
        QualityFlag(strike_id="s4",  flag_type=FlagType.HIP_ROTATION_LIMITED, severity=Severity.MEDIUM, description="Hip rotation on cross was 30% below expected range — punch losing power at the source."),
        QualityFlag(strike_id="s7",  flag_type=FlagType.HIP_ROTATION_LIMITED, severity=Severity.HIGH,   description="Minimal hip rotation detected. Cross appears to be arm-only, losing significant power."),
        QualityFlag(strike_id="s11", flag_type=FlagType.HIP_ROTATION_LIMITED, severity=Severity.MEDIUM, description="Hip rotation limited. Cross not fully loaded from the ground up."),
        QualityFlag(strike_id="s16", flag_type=FlagType.HIP_ROTATION_LIMITED, severity=Severity.LOW,    description="Slightly limited hip rotation. Improved from earlier crosses but still not full rotation."),

        # Overextension on hooks
        QualityFlag(strike_id="s5",  flag_type=FlagType.OVEREXTENDED,         severity=Severity.HIGH,   description="Elbow angle exceeded safe range at hook extension — arm straightening, losing the arc and risking elbow hyperextension."),
        QualityFlag(strike_id="s12", flag_type=FlagType.OVEREXTENDED,         severity=Severity.MEDIUM, description="Hook slightly overextended. Arc breaking down at the end of the punch."),
        QualityFlag(strike_id="s17", flag_type=FlagType.OVEREXTENDED,         severity=Severity.MEDIUM, description="Overextension on left hook. Punch going past the target plane."),
    ],
)
