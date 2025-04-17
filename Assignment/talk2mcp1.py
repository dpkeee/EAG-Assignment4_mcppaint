import os
import logging
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import asyncio
from google import genai
from concurrent.futures import TimeoutError
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Access your API key and initialize Gemini client correctly
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

max_iterations = 5

last_response = None
iteration = 0
iteration_response = []

async def generate_with_timeout(client, prompt, timeout=10):
    """Generate content with a timeout"""
    logger.debug("Starting LLM generation...")
    try:
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None, 
                lambda: client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )
            ),
            timeout=timeout
        )
        logger.debug("LLM generation completed")
        return response
    except TimeoutError:
        logger.error("LLM generation timed out!")
        raise
    except Exception as e:
        logger.error(f"Error in LLM generation: {e}")
        raise

def reset_state():
    """Reset all global variables to their initial state"""
    global last_response, iteration, iteration_response
    last_response = None
    iteration = 0
    iteration_response = []

async def main():
    reset_state()  # Reset at the start of main
    logger.info("Starting main execution...")
    try:
        logger.info("Establishing connection to MCP server...")
        server_params = StdioServerParameters(
            command="python",
            args=["paint.py"]
        )

        async with stdio_client(server_params) as (read, write):
            logger.info("Connection established, creating session...")
            async with ClientSession(read, write) as session:
                logger.info("Session created, initializing...")
                await session.initialize()
                
                logger.info("Requesting tool list...")
                tools_result = await session.list_tools()
                tools = tools_result.tools
                logger.info(f"Successfully retrieved {len(tools)} tools")

                logger.info("Creating system prompt...")
                logger.info(f"Number of tools: {len(tools)}")
                
                try: 
                    tools_description = []
                    for i, tool in enumerate(tools):
                        try:
                            params = tool.inputSchema
                            desc = getattr(tool, 'description', 'No description available')
                            name = getattr(tool, 'name', f'tool_{i}')
                            
                            if 'properties' in params:
                                param_details = []
                                for param_name, param_info in params['properties'].items():
                                    param_type = param_info.get('type', 'unknown')
                                    param_details.append(f"{param_name}: {param_type}")
                                params_str = ', '.join(param_details)
                            else:
                                params_str = 'no parameters'

                            tool_desc = f"{i+1}. {name}({params_str}) - {desc}"
                            tools_description.append(tool_desc)
                            logger.debug(f"Added description for tool: {tool_desc}")
                        except Exception as e:
                            logger.error(f"Error processing tool {i}: {e}")
                            tools_description.append(f"{i+1}. Error processing tool")
                
                    tools_description = "\n".join(tools_description)
                    logger.info("Successfully created tools description")
                
                except Exception as e:
                    print(f"Error creating tools description: {e}")
                    tools_description = "Error loading tools"

                logger.info("Created system prompt...")
                system_prompt = f"""You are an AI agent designed to solve the user query through step-by-step reasoning and tool usage.
                and then Open Paint application. Draw a rectangle.Add text box inside the rectangle.Add the FINAL_ANSWER from LLM response inside the text box.
                You are allowed to use the following tools:

Available tools: {tools_description}                
When responding, please format your output as a JSON object with the following structure:

{{
                      "steps": [
                        {{
                          "step_number": 1,
                          "tool_name": "exact_tool_name",
                          "param1": value1, #optional
                          "param2": value2, #optional
                          ...
                        }},
                        {{
                          "step_number": 2,
                          "tool_name": "exact_tool_name",
                          "param1": value1, #optional
                          "param2": value2, #optional   
                          ...
                        }}
                      ],
                      "fallback_response": "Your direct response if no tools are needed"
                    }}


Before selecting the tools to use, follow this reasoning process:

**Example of a correct response:**

```
{{
  "steps": [
    {{
      "step_number": 1,
      "tool_name": "multiply",
      "param1": value1,
      "param2": value2
    }},
    {{
      "step_number": 2,
      "tool_name": "open_paint"
    }}
  ],
  "fallback_response": "Your direct response if no tools are needed"  
}}
```
**Important:**

*   The LLM response MUST be a valid JSON RESPONSE.
*   The `steps` array should contain objects, each representing a step.
*   Each step object MUST have a `step_number` and a `tool_name`.
*   Parameters for the tool (like `a` and `b` for the `multiply` tool) should be included as direct key-value pairs within the step object, **NOT** nested inside another JSON string.
*   Do NOT include any additional text, explanations, or formatting.
*   Do NOT include code block indicators such as ```json or ```.

Before selecting the tools to use, follow this reasoning process:

1.  Understand the User's Request: Carefully analyze the user's query to fully grasp the problem or task.
2.  Decompose the Request: Break down the query into logical components.
3.  Formulate a step-by-step plan with reasoning \[RETRIEVAL, LOGICAL, SEQUENTIAL, ANALYTICAL, CREATIVE, EVALUATIVE]
4.  Select Appropriate Tools: Consider which tools are best suited for each step. Ensure each tool is relevant and matches the need.

Key Verification Points:

*   Tool Name Accuracy: Ensure that each tool used is available and the tool name exactly matches its identifier.
*   Input Format: Confirm that each tool's input format aligns with the expectations of the tool.
*   Logical Flow: The sequence of steps should follow a logical progression—outputs from one step should feed into subsequent steps.

Function call: after every function call, run the verify tool.

Edge Case Handling: Consider and address potential edge cases, ensuring that the plan accommodates them.

FINAL_ANSWER must always be in text format.

Fallback & Error Handling:

If you are unsure about a value, function name, or parameters:

*   Respond with: UNCERTAIN: "Describe what you are unsure about and what additional info is needed."

If a function call fails or returns unexpected results:

*   Recheck the parameters and reasoning.
*   Retry with corrected parameters if possible.
*   If still unresolved, respond with: ERROR: "Describe what failed and suggest possible resolutions or clarify needed info."

Important:

*   Do not fabricate data. If necessary inputs are missing, explain what's needed before proceeding.
*   If a function returns multiple values, process all of them.
*   Only provide the FINAL_ANSWER when all necessary steps are completed and validated. Do not repeat function calls with the same parameters unless it is required to correct an error.

Context Information:

Previous Conversation: {{response_text}}

Current Query: "{{query}}"

Important Instructions:

*   DO NOT include any explanations, intermediate results, or extra text.
*   Strictly follow the provided format and guidelines."""
             
                # query = "what is the sum of 45 and 55"
                query = "multiply 45 and 55"
                logger.info("Starting iteration loop...")
                
                global iteration, last_response
                
                while iteration < max_iterations:
                    logger.info(f"\n--- Iteration {iteration + 1} ---")
                    if last_response is None:
                        current_query = query
                    else:
                        current_query = current_query + "\n\n" + " ".join(iteration_response)
                        current_query = current_query + "  What should I do next?"

                    logger.debug("Preparing to generate LLM response...")
                    prompt = f"{system_prompt}\n\nQuery: {current_query}"
                    try:
                        response = await generate_with_timeout(client, prompt)
                        response_text = response.text.strip()
                        logger.debug(f"LLM Response is this deepika: {response_text}")
                        print('type of response_text', type(response_text))
                    except Exception as e:
                        logger.error(f"Failed to get LLM response: {e}")
                        break

                    if response_text:  # Check if response_text is not empty
                        logger.debug(f"Raw response string: {response_text}")

                        # Remove the code block indicators if present
                        if response_text.startswith("```json"):
                            logger.debug("Found ```json at the beginning")
                            response_text = response_text[7:].strip()  # Remove the ```json part
                            logger.debug(f"Response after removing ```json: {response_text}")
                        if response_text.endswith("```"):
                            logger.debug("Found ``` at the end")
                            response_text = response_text[:-3].strip()  # Remove the ending ```
                            logger.debug(f"Response after removing ending ```: {response_text}")

                        # Check if the response is empty after stripping
                        if not response_text:
                            logger.error("Received an empty response from the LLM.")
                            continue  # Skip to the next iteration or handle the error appropriately

                        try:
                            # Directly parse the JSON response
                            steps = json.loads(response_text)  # Parse the JSON string

                            for step in steps['steps']:
                                tool_name = step['tool_name']
                                # Extract the json_string from the step
                                params_json_string = step.get('json_string')

                                logger.debug(f"Calling tool: {tool_name} with parameters: {params_json_string}")

                                # Call the respective function with the json_string
                                result = await session.call_tool(tool_name, arguments=params_json_string)

                                # Handle the result as needed
                                logger.debug(f"Result from {tool_name}: {result}")

                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to decode JSON from response: {e}")
                        except Exception as e:
                            logger.error(f"An error occurred while processing the LLM response: {e}")

                        iteration += 1

    except Exception as e:
        logger.error(f"Error in main execution: {e}")
    finally:
        reset_state()  # Reset at the end of main

if __name__ == "__main__":
    asyncio.run(main())
    
    
