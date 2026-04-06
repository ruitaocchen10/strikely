import json
import os
from anthropic import Anthropic
from app.schemas import SessionAnalysis, CoachReport, Issue
from app.mcp.server import create_mcp_server

SYSTEM_PROMPT = """
You are an experienced boxing coach reviewing a student's training footage.

You have access to tools that provide structured analysis of the session — strike detection, technique flags, and timing data extracted from computer vision processing.

Your job:
1. Use the available tools to thoroughly understand the session before forming any opinions.
   Start with get_session_summary(), then explore areas of concern in more detail.
2. Identify the 2-3 most important issues to address. Prioritise by frequency and severity,
   not by exhaustively listing every flag.
3. Note genuine strengths — what the athlete is doing well.
4. Give specific, actionable recommendations. "Keep your guard up" is not useful.
   "Your right hand consistently drops below chin level during jabs — drill the jab-return
   to guard combination at half speed until the return becomes automatic" is useful.

Respond with a JSON object in this exact structure:
{
  "summary": "2-3 sentence overall assessment",
  "strengths": ["strength 1", "strength 2"],
  "issues": [
    {
      "flag_type": "guard_dropped",
      "count": 7,
      "description": "explanation of the issue and why it matters",
      "affected_strikes": ["s1", "s3", "s6"]
    }
  ],
  "recommended_drills": ["drill 1", "drill 2"]
}

Return only the JSON — no preamble, no explanation outside the object."""

TOOLS = [
    {
        "name": "get_session_summary",
        "description": "Returns overall stats for the training session: duration, total strike count, breakdown by strike type, and a count of technique flags by type.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_strike_list",
        "description": "Returns all detected strikes in the session. Each entry includes the strike id, type, hand, timestamp, and number of technique flags. Use get_strike_detail to dig into a specific strike.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_strike_detail",
        "description": "Returns full details for a single strike by id, including all associated technique flags with severity and descriptions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "strike_id": {"type": "string", "description": "The id of the strike to retrieve."}
            },
            "required": ["strike_id"],
        },
    },
    {
        "name": "get_flag_list",
        "description": "Returns all technique flags raised in the session. Optionally filter by flag_type: guard_dropped, chin_exposed, overextended, hip_rotation_limited.",
        "input_schema": {
            "type": "object",
            "properties": {
                "flag_type": {"type": "string", "description": "Optional flag type to filter by."}
            },
            "required": [],
        },
    },
]

def generate_report(analysis: SessionAnalysis) -> CoachReport:
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    mcp = create_mcp_server(analysis)

    tool_functions = {
        "get_session_summary": mcp._tool_manager.tools["get_session_summary"].fn,
        "get_strike_list":     mcp._tool_manager.tools["get_strike_list"].fn,
        "get_strike_detail":   mcp._tool_manager.tools["get_strike_detail"].fn,
        "get_flag_list":       mcp._tool_manager.tools["get_flag_list"].fn,
    }

    messages = [{"role": "user", "content": "Please analyse this training session and produce a coaching report."}]

    max_iterations = 10
    iterations = 0

    while iterations < max_iterations:
        iterations += 1

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            break

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"[tool call] {block.name}({block.input})") # for review/testing
                result = tool_functions[block.name](**block.input)
                print(f"[tool result] {json.dumps(result, indent=2)}") # for review/testing
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result),
                })

        messages.append({"role": "user", "content": tool_results})

    final_text = next(b.text for b in response.content if hasattr(b, "text"))
    data = json.loads(final_text)

    return CoachReport(
        summary=data["summary"],
        strengths=data["strengths"],
        issues=[Issue(**i) for i in data["issues"]],
        recommended_drills=data["recommended_drills"],
    )
