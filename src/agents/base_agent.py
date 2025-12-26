from src.utils.llm import generate_text, generate_text_async

class BaseAgent:
    def __init__(self, name, role, system_instruction, temperature=0.7):
        self.name = name
        self.role = role
        self.system_instruction = system_instruction
        self.temperature = temperature
        self.history = []

    def run(self, user_input, context=None):
        """
        Executes the agent's logic based on user input and optional context.
        """
        # Construct the full prompt
        full_prompt = f"""
System Instruction:
{self.system_instruction}

Context:
{context if context else "No additional context provided."}

User Input:
{user_input}
"""
        # Call LLM
        response = generate_text(full_prompt, temperature=self.temperature)
        
        # Update history (simple in-memory history for now)
        self.history.append({"user": user_input, "agent": response})
        
        return response

    def get_history(self):
        return self.history

    async def run_async(self, user_input, context=None):
        """
        Asynchronously executes the agent's logic.
        """
        full_prompt = f"""
System Instruction:
{self.system_instruction}

Context:
{context if context else "No additional context provided."}

User Input:
{user_input}
"""
        # Call Async LLM Wrapper
        response = await generate_text_async(full_prompt)
        
        self.history.append({"user": user_input, "agent": response})
        return response
