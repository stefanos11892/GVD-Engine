import asyncio
from typing import List, Tuple, Any

class AgentOrchestrator:
    """
    Manages the parallel execution of multiple agents.
    """
    
    @staticmethod
    async def run_parallel(tasks: List[Tuple[Any, str, str]]) -> dict:
        """
        Runs multiple agent tasks in parallel.
        
        Args:
            tasks: A list of tuples, where each tuple is (AgentInstance, prompt, context).
                   Example: [(analyst, "Analyze X", context), (radar, "Scan Y", context)]
                   
        Returns:
            A dictionary mapping agent names to their outputs.
            { "Analyst": "Report...", "Radar": "News..." }
        """
        async def run_agent_task(agent, prompt, context):
            print(f"--- [ORCHESTRATOR] Spawning Task: {agent.name} ---")
            result = await agent.run_async(prompt, context)
            print(f"--- [ORCHESTRATOR] Completed Task: {agent.name} ---")
            return agent.name, result

        # Create awaitable objects for each task
        coroutines = [run_agent_task(agent, prompt, context) for agent, prompt, context in tasks]
        
        # Run all coroutines concurrently
        results = await asyncio.gather(*coroutines)
        
        # Convert list of tuples to dictionary
        return dict(results)
