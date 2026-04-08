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

# 4.05.2026

11:06 PM

- I kind of forgot to take notes before, but I'm at the point now where I need to figure out how to make the agent use tools from the MCP server to give a response.

# 4.06.2026

9:49 AM

- Okay, after doing some reading, essentially the way MCP works is that we give our agent a "tool list" at the beginning, which is exactly what it sounds like, a list of tools that the agent can call.
- Once my agent has the list it can decide when and what tools to call. I've essentially now written into my coach.py a list of tools that I have, and a loop for my model to give it the available tools, and then respond to a prompt with the given tools it has until it receives the desired output. I guess this is generally how MCP works.
- Next, I have to write the POST route which actually runs the generate report function on my mock data for now. This should be a really simple POST API route that just returns the generate report function with my mock data as a parameter

9:33 PM

- Created next.js frontend

# 4.06.2026

5:28 PM

- Created a quick test to pair up the backend with the frontend and try my POST /analyze route (literally just a button and a response), but everything is looking good. The route is working and we can start moving onto the actual functionality now.

# 4.08.2026

11:04 AM

- In terms of building the CV pipeline, I ran through a couple choices. Using computer vision tools, we can write rule-based models to identify what type of shots the users are throwing, but these are super brittle and probably will get broken by simple inconsistencies in each video. Training my own model would take a century and I don't know how to do it, so I think we can rule out that option. The last option would be to use a multimodal AI to review the footage. While this option has potential, I have concerns about the cost and the accuracy.
- I can potentially implement a hybrid system where the AI reviews the CV pipeline and is able to review gaps in the footage, but this is probably going to be both costly and high-latency. For now, I think it might be best if we can flag low confidence scores in our CV pipeline to determine what kind of accuracy we're getting.
- First part of the pipeline, we use OpenCV and MediaPipe tools to return the list of landmarks from each frame, which is the raw data that the detection works on.
- Now, we write a rule-based function to classify each strike by using a velocity threshold, and returning a strike if the wrist velocity passes a certain threshold.
- Couple changes: passed in a way to detect stance to make Jab vs. Cross detection easier (also stance is just important to collect), updated to use 3D metrics to get more accurate responses from rotations of the user. Unfortunately, there might still be some weaknesses when the user's back is to the camera, but we added a confidence fallback in this case
- After testing: CV rules have been super inaccurate. Wonder if it might be time to try to use an AI agent instead to identify strikes.
