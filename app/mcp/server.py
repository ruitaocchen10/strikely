from mcp.server.fastmcp import FastMCP
from app.schemas import SessionAnalysis


def get_tool_functions(analysis: SessionAnalysis) -> dict:
    def get_session_summary() -> dict:
        strike_type_counts = {}
        for strike in analysis.detected_strikes:
            key = strike.type.value
            strike_type_counts[key] = strike_type_counts.get(key, 0) + 1

        flag_type_counts = {}
        for flag in analysis.quality_flags:
            key = flag.flag_type.value
            flag_type_counts[key] = flag_type_counts.get(key, 0) + 1

        return {
            "duration_seconds": analysis.duration_seconds,
            "total_strikes": len(analysis.detected_strikes),
            "strikes_by_type": strike_type_counts,
            "total_flags": len(analysis.quality_flags),
            "flags_by_type": flag_type_counts,
        }

    def get_strike_list() -> list:
        flags_per_strike = {}
        for flag in analysis.quality_flags:
            flags_per_strike[flag.strike_id] = flags_per_strike.get(flag.strike_id, 0) + 1

        return [
            {
                "id": strike.id,
                "type": strike.type.value,
                "hand": strike.hand.value,
                "timestamp": strike.timestamp,
                "flag_count": flags_per_strike.get(strike.id, 0),
            }
            for strike in analysis.detected_strikes
        ]

    def get_strike_detail(strike_id: str) -> dict:
        strike = next((s for s in analysis.detected_strikes if s.id == strike_id), None)
        if strike is None:
            return {"error": f"No strike found with id '{strike_id}'"}

        flags = [
            {
                "flag_type": flag.flag_type.value,
                "severity": flag.severity.value,
                "description": flag.description,
            }
            for flag in analysis.quality_flags
            if flag.strike_id == strike_id
        ]

        return {
            "id": strike.id,
            "type": strike.type.value,
            "hand": strike.hand.value,
            "timestamp": strike.timestamp,
            "start_frame": strike.start_frame,
            "peak_frame": strike.peak_frame,
            "end_frame": strike.end_frame,
            "flags": flags,
        }

    def get_flag_list(flag_type: str | None = None) -> list:
        strike_timestamps = {s.id: s.timestamp for s in analysis.detected_strikes}

        flags = list(analysis.quality_flags)
        if flag_type is not None:
            flags = [f for f in flags if f.flag_type.value == flag_type]

        return [
            {
                "strike_id": flag.strike_id,
                "timestamp": strike_timestamps.get(flag.strike_id),
                "flag_type": flag.flag_type.value,
                "severity": flag.severity.value,
                "description": flag.description,
            }
            for flag in flags
        ]

    return {
        "get_session_summary": get_session_summary,
        "get_strike_list": get_strike_list,
        "get_strike_detail": get_strike_detail,
        "get_flag_list": get_flag_list,
    }


def create_mcp_server(analysis: SessionAnalysis) -> FastMCP:
    mcp = FastMCP("strikely")
    fns = get_tool_functions(analysis)

    for fn in fns.values():
        mcp.tool()(fn)

    return mcp
