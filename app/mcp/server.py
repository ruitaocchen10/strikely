from mcp.server.fastmcp import FastMCP
from app.schemas import SessionAnalysis

def create_mcp_server(analysis: SessionAnalysis) -> FastMCP:
    mcp = FastMCP("strikely")

    @mcp.tool()
    def get_session_summary() -> dict:
        """
        Returns overall stats for the training session: duration, total strike count,
        breakdown by strike type, and a count of technique flags by type.
        """
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
    
    @mcp.tool()
    def get_strike_list() -> list:
        """
        Returns all detected strikes in the session. Each entry includes the strike id,
        type, hand, timestamp, and number of technique flags. Use get_strike_detail(id)   
        to get full flag details for a specific strike.                                   
        """                                                                               
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

    @mcp.tool()
    def get_strike_detail(strike_id: str) -> dict:
        """
        Returns full details for a single strike by id, including its type, hand,
        timing, and all associated technique flags with severity and descriptions.
        Returns an error key if the strike id is not found.
        """
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

    @mcp.tool()
    def get_flag_list(flag_type: str | None = None) -> list:
        """
        Returns all technique flags raised in the session. Optionally filter by
        flag_type (guard_dropped, chin_exposed, overextended, hip_rotation_limited).
        Each entry includes the strike id, timestamp, flag type, severity, and description.
        """
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

    return mcp
