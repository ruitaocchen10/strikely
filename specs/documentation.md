# 4.03.2026

9:20 PM

- Started with building out a general plan for the MVP, including the problem statement, a proposed solution, and MVP plan. Going to focus on just boxing and single-person training for simplicity, and work on implementing FastAPI routes and an MCP server for specific tool use. The UX will just be upload a video and get AI-generated feedback for now, until we're able to implement better features.
- Creating the FastAPI entry point first which includes routers from other modules and any middleware.
- Creating schema using Pydantic which defines data and has type validation. Built on top of FastAPI. Schema basically defines strikes and issues, a session analysis for the agent to read, and a agent review.
- Going to use a mock SessionAnalysis for now to test the MCP integration and the Agent response, because I think the CV writing is going to be the hardest part, and I want to focus more on MCP and FastAPI anyways.
- MCP integration is next. For now, we're really just including some basic tools like getting an analysis, flag list, strike list, etc. but I'm hoping this might be more useful in the future if I can allow a user to chat with the agent about more specifics in their training footage.

# 4.04.2026

10:02 AM

- Figuring the real value of MCP:
  - For a short session/our MVP, MCP is overkill. But the value is when we get longer sessions and it becomes more difficult to dump all of the data straight to an agent. Once we start to implement the chat feature, it also allows us to query specific elements without having to re-inject all of the raw data into every message
  - Also, the MCP server is a stable layer between the data and AI layers. If we, update the data layer, all we have to do is update the MCP tool implementations instead of the entire agent.
- I was able to write a basic MCP server that returns specific Python tools and structured data responses for the AI to use.
- Had some thoughts: How do we get to the point where we can build a flexible system that isn't just a rule-based vision review. We don't need to create something that just says "Keep your chin down and your hands up" - those things can be helpful for beginners but aren't really huge insights. Some ideas for this maybe:
  - Reviewing different aspects: mechanics, technique, movement, etc.
  - Connecting outcome to techniques: Would be for later if we implement sparring
  - Having objective rules as well as some more flexible rules
