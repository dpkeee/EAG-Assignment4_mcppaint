import os
import logging
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import asyncio
import json
from google import genai
from concurrent.futures import TimeoutError
from functools import partial
import pydantic

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

# Define a Pydantic model for the LLM output format
class LLMOutput(pydantic.BaseModel):
    Step_number: int
    reasoning_type: str
    tool_name: str
    parameters: list

def create_tool_parameters_model(schema_properties):
    """Dynamically create a Pydantic model for tool parameters."""
    fields = {}
    for param_name, param_info in schema_properties.items():
        param_type = param_info.get('type', 'string')
        if param_type == 'integer':
            fields[param_name] = (int, ...)
        elif param_type == 'number':
            fields[param_name] = (float, ...)
        elif param_type == 'string':
            fields[param_name] = (str, ...)
        elif param_type == 'array':
            fields[param_name] = (list, ...)
        else:
            fields[param_name] = (str, ...)  # Default to string if type is unknown
    return pydantic.create_model('ToolParameters', **fields)

async def generate_with_timeout(client, prompt, timeout=10):
    """Generate content with a timeout"""
    logger.debug("Starting LLM generation...")
    try:
        # Convert the synchronous generate_content call to run in a thread
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
                
                logger.info("Created system prompt...")
                system_prompt = f""" You are an AI agent designed to solve the user query through step-by-step reasoning and tool usage. 

Before selecting the tools to use, follow this reasoning process:

1.Understand the User's Request: Carefully analyze the user's query to fully grasp the problem or task.

2.Decompose the Request: Break down the query into logical components.

3. Formulate a step by step plan with reasoning [ RETRIEVAL, LOGICAL, SEQUENTIAL, ANALYTICAL, CREATIVE, EVALUATIVE]

4.Select Appropriate Tools: Consider which tools are best suited for each step. Ensure each tool is relevant and matches the need.

5.Construct a Step-by-Step Action Plan in JSON Format

Step by step plan format:

Your final response should be a valid JSON object that follows this structure:


{
  "steps": [
    {  
      "step_number": 1,
      "reasoning_type": "RETRIEVAL",
      "tool_name": "tool_name",
      "parameters": Optional[List[str]]
    },
    {
      "step_number": 2,
      "reasoning_type": "SEQUENTIAL",
      "tool_name": "next_tool_name",
      "parameters": Optional[List[str]]
    }
    .
    .
    .
  ],
  "fallback_response": "Your direct response if no tools are needed"
}

6. Once all the function calls are done successfully in above step by step order, the final result is stored in FINAL_ANSWER in text format.

7. Opens Paint application.

8. Draws Rectangle inside the paint applicaiton opened.

9. Draws textbox inside the Rectangle and print the FINAL_ANSWER inside the textbox.

10. Sends an email to labjuno2022@gmail.com with the FINAL_ANSWER in the body and subject as "Final Answer".


Key Verification Points:
Tool Name Accuracy: Ensure that each tool used is available and the tool name exactly matches its identifier.

Input Format: Confirm that each tool's input format aligns with the expectations of the tool.

Logical Flow: The sequence of steps should follow a logical progression—outputs from one step should feed into subsequent steps. 

Function call : after every function call, run the verify tool.

Edge Case Handling: Consider and address potential edge cases, ensuring that the plan accommodates them.

FINAL_ANSWER must always be in text format.

Ensure all reasoning and output strictly follows the JSON format above.

LLM  JSON Output Rules:
Always include the "tool_name" field as a non-empty string.

Include "parameters" only if required for the tool to work.

Parameter values can be of the following types:
- string (e.g., "text")
- integer (e.g., 42)
- list (e.g., ["a", "b", 1])



Fallback & Error Handling:
If you are unsure about a value, function name, or parameters:
- Respond with: UNCERTAIN: "Describe what you are unsure about and what additional info is needed."

If a function call fails or returns unexpected results:
- Recheck the parameters and reasoning.
- Retry with corrected parameters if possible.
- If still unresolved, respond with: ERROR: "Describe what failed and suggest possible resolutions or clarify needed info."

Important:
- Do not fabricate data. If necessary inputs are missing, explain what's needed before proceeding.
- If a function returns multiple values, process all of them.
- Only provide the FINAL_ANSWER when all necessary steps are completed and validated. Do not repeat function calls with the same parameters unless it is required to correct an error.

Context Information:
Previous Conversation: {{response_text}}

Current Query: "{{query}}"

Important Instructions:
- DO NOT include any explanations, intermediate results, or extra text.
- Strictly follow the provided format and guidelines."""
             
                query = "what is the sum of 45 and 55. "
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
                        logger.debug(f"LLM Response: {response_text}")
                        
                    except Exception as e:
                        logger.error(f"Failed to get LLM response: {e}")
                        break

                    if response_text:  # Check if response_text is not empty
                        logger.debug(f"Raw JSON string: {response_text}")

                        try:
                            # Parse the JSON string directly
                            function_call = json.loads(response_text)

                            # Proceed with the output directly
                            func_name = function_call['tool_name']
                            params = function_call['parameters']
                            
                            logger.debug(f"DEBUG: Function name: {func_name}, Parameters: {params}")

                            # Find the matching tool to get its input schema
                            tool = next((t for t in tools if t.name == func_name), None)
                            if not tool:
                                logger.debug(f"DEBUG: Available tools: {[t.name for t in tools]}")
                                raise ValueError(f"Unknown tool: {func_name}")

                            logger.debug(f"DEBUG: Found tool: {tool.name}")
                            logger.debug(f"DEBUG: Tool schema: {tool.inputSchema}")

                            # Validate if the tool description matches the LLM parameter list
                            expected_params = list(tool.inputSchema.get('properties', {}).keys())
                            provided_params = params

                            # Check if the expected parameters match the provided parameters
                            if len(expected_params) != len(provided_params):
                                logger.error(f"Parameter mismatch: Expected {expected_params}, but got {provided_params}")
                                raise ValueError("Parameter count mismatch between tool and LLM output.")

                            for expected_param in expected_params:
                                if expected_param not in provided_params:
                                    logger.error(f"Missing parameter: {expected_param} is not in the provided parameters.")
                                    raise ValueError(f"Missing parameter: {expected_param} is not in the provided parameters.")

                            logger.debug(f"DEBUG: All parameters match for tool: {func_name}")

                            # Prepare arguments according to the tool's input schema
                            arguments = {}
                            schema_properties = tool.inputSchema.get('properties', {})
                            
                            for param_name, param_info in schema_properties.items():
                                if not params:  # Check if we have enough parameters
                                    raise ValueError(f"Not enough parameters provided for {func_name}")
                                    
                                value = params.pop(0)  # Get and remove the first parameter
                                param_type = param_info.get('type', 'string')
                                
                                # Convert the value to the correct type based on the schema
                                if param_type == 'integer':
                                    arguments[param_name] = int(value)
                                elif param_type == 'number':
                                    arguments[param_name] = float(value)
                                elif param_type == 'array':
                                    # Handle array input
                                    if isinstance(value, str):
                                        value = value.strip('[]').split(',')
                                    arguments[param_name] = [int(x.strip()) for x in value]
                                else:
                                    arguments[param_name] = str(value)

                            logger.debug(f"DEBUG: Final arguments: {arguments}")

                            result = await session.call_tool(func_name, arguments=arguments)
                            logger.debug(f"DEBUG: Raw result: {result}")
                            
                            # Get the full result content
                            if hasattr(result, 'content'):
                                logger.debug(f"DEBUG: Result has content attribute")
                                # Handle multiple content items
                                if isinstance(result.content, list):
                                    iteration_result = [
                                        item.text if hasattr(item, 'text') else str(item)
                                        for item in result.content
                                    ]
                                else:
                                    iteration_result = str(result.content)
                            else:
                                logger.debug(f"DEBUG: Result has no content attribute")
                                iteration_result = str(result)
                                
                            logger.debug(f"DEBUG: Final iteration result: {iteration_result}")
                            
                            # Format the response based on result type
                            if isinstance(iteration_result, list):
                                result_str = f"[{', '.join(iteration_result)}]"
                            else:
                                result_str = str(iteration_result)
                            
                            iteration_response.append(
                                f"In the {iteration + 1} iteration you called {func_name} with {arguments} parameters, "
                                f"and the function returned {result_str}."
                            )
                            last_response = iteration_result

                        except json.JSONDecodeError as je:
                            logger.error(f"JSON decode error: {je}")  # Log JSON parsing errors
                        except Exception as e:
                            logger.error(f"An error occurred while processing the function call: {e}")

                    elif response_text.startswith("FINAL_ANSWER:"):
                        logger.info("\n=== Agent Execution Complete ===")

                    iteration += 1

    except Exception as e:
        logger.error(f"Error in main execution: {e}")
    finally:
        reset_state()  # Reset at the end of main

if __name__ == "__main__":
    asyncio.run(main())
