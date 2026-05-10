import json
from groq import Groq
from utils.agent_tools import (
    tool_find_route,
    tool_calculate_fare,
    tool_list_routes_through_landmark,
    tool_get_route_details,
    TOOL_SCHEMAS
)


def build_agent_system_prompt(tool_schemas: list) -> str:
    """Build the system prompt that tells the LLM about available tools."""
    tools_text = json.dumps(tool_schemas, indent=2)
    return f"""You are RoutaGo, an intelligent and friendly Cebu jeepney navigation agent.
Your personality is warm, helpful, and local. Use Cebuano/Bisaya expressions naturally like "Maayong adlaw!", "Amping!", and "Lugar lang!".
You speak Cebuano when the user speaks Cebuano, and English when they speak English.

AVAILABLE TOOLS:
{tools_text}

AGENT BEHAVIOR RULES:
1. When you need information, respond ONLY with a JSON tool call in this exact format:
   {{"tool": "tool_name", "params": {{"param1": "value1", "param2": "value2"}}}}

2. After receiving tool results, you can call another tool if needed, or provide a final answer.

3. Use tools intelligently:
   - For route questions: call find_route first
   - For fare questions: call find_route first (to get distance), then calculate_fare
   - For "which routes pass through X": call list_routes_through_landmark
   - For "tell me about route XYZ": call get_route_details

4. When you have enough information, respond in natural friendly Cebuano-influenced English.

5. Response formatting:
   - Use bold for jeepney codes (e.g., **01K**, **13B**)
   - List stops clearly and in order
   - For transfers, explain both legs clearly
   - Include estimated distance and fare in your response
   - Use "Lugar lang!" for the passenger signal to alight

6. Maximum 3 tool calls per response to keep things efficient.

7. If a tool returns an error or no results, explain clearly and suggest alternatives.

8. For any calculations or factual route information, ALWAYS use tools first - never guess.
"""


def execute_tool(tool_name: str, params: dict, routes: dict) -> str:
    """Execute a tool and return the result as JSON string."""
    try:
        if tool_name == "find_route":
            result = tool_find_route(
                params.get("origin", ""),
                params.get("destination", ""),
                routes
            )
        elif tool_name == "calculate_fare":
            result = tool_calculate_fare(
                float(params.get("distance_km", 4)),
                params.get("passenger_type", "Regular")
            )
        elif tool_name == "list_routes_through_landmark":
            result = tool_list_routes_through_landmark(
                params.get("landmark", ""),
                routes
            )
        elif tool_name == "get_route_details":
            result = tool_get_route_details(
                params.get("route_code", ""),
                routes
            )
        else:
            result = {"error": f"Unknown tool: {tool_name}"}
    except Exception as e:
        result = {"error": f"Tool execution failed: {str(e)}"}

    return json.dumps(result)


def parse_tool_call(reply: str) -> dict:
    """Extract a tool call from LLM response (handles markdown code fences and mixed text)."""
    try:
        clean = reply.strip()

        # Handle markdown code fences
        if "```json" in clean:
            clean = clean.split("```json")[1].split("```")[0].strip()
        elif "```" in clean:
            clean = clean.split("```")[1].split("```")[0].strip()

        # Always try to extract JSON by brace-matching
        start_idx = clean.find("{")
        if start_idx != -1:
            brace_count = 0
            end_idx = start_idx
            for i in range(start_idx, len(clean)):
                if clean[i] == "{":
                    brace_count += 1
                elif clean[i] == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        end_idx = i + 1
                        break

            if brace_count == 0:
                clean = clean[start_idx:end_idx]

        parsed = json.loads(clean)
        if "tool" in parsed and "params" in parsed:
            return parsed
    except (json.JSONDecodeError, KeyError, IndexError, ValueError):
        pass

    return None


def run_agent(user_message: str, routes: dict, client: Groq, max_steps: int = 3) -> str:
    """
    Main agent loop.
    - Takes a user message
    - Decides which tools to call
    - Executes them
    - Returns final answer
    """
    from utils.helpers import format_response

    system_prompt = build_agent_system_prompt(TOOL_SCHEMAS)

    # Conversation history for this agent run
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    for step in range(max_steps):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                temperature=0.0,
            )

            reply = response.choices[0].message.content.strip()

            # Try to parse a tool call
            tool_call = parse_tool_call(reply)

            # If no tool call, this is the final answer
            if tool_call is None:
                return format_response(reply)

            # Execute the tool
            tool_name = tool_call["tool"]
            params = tool_call["params"]
            tool_result = execute_tool(tool_name, params, routes)

            # Add to conversation history
            messages.append({"role": "assistant", "content": reply})
            messages.append({
                "role": "user",
                "content": f"Tool result for '{tool_name}':\n{tool_result}\n\nContinue reasoning or provide your final answer."
            })

        except Exception as e:
            return f"Error during agent execution: {str(e)}"

    # If max steps reached, ask for final answer
    messages.append({
        "role": "user",
        "content": "Please provide your final answer to the user now based on the tool results above."
    })

    try:
        final = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.0,
        )
        return format_response(final.choices[0].message.content.strip())
    except Exception as e:
        return f"Error generating final answer: {str(e)}"
