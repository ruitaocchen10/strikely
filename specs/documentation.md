# 4.03.2026

9:20 PM

- Started with building out a general plan for the MVP, including the problem statement, a proposed solution, and MVP plan. Going to focus on just boxing and single-person training for simplicity, and work on implementing FastAPI routes and an MCP server for specific tool use. The UX will just be upload a video and get AI-generated feedback for now, until we're able to implement better features.
- Creating the FastAPI entry point first which includes routers from other modules and any middleware.
- Creating schema using Pydantic which defines data and has type validation. Built on top of FastAPI. Schema basically defines strikes and issues, a session analysis for the agent to read, and a agent review.
- Going to use a mock SessionAnalysis for now to test the MCP integration and the Agent response, because I think the CV writing is going to be the hardest part, and I want to focus more on MCP and FastAPI anyways.
