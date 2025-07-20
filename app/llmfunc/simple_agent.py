"""
Simple LangGraph agent for basic AI tasks.
"""

from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from .config import config

class AgentState(TypedDict):
    """State definition for the simple agent."""
    messages: List[Dict[str, str]]
    current_task: str
    result: str
    iteration_count: int

class SimpleAgent:
    """A simple LangGraph agent for basic AI tasks."""
    
    def __init__(self, model_name: str = None):
        """Initialize the simple agent."""
        config.validate_config()
        self.llm = ChatOpenAI(**config.get_llm_config(model_name))
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the agent graph."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_task", self._analyze_task)
        workflow.add_node("process_task", self._process_task)
        workflow.add_node("finalize_result", self._finalize_result)
        
        # Add edges
        workflow.set_entry_point("analyze_task")
        workflow.add_edge("analyze_task", "process_task")
        workflow.add_edge("process_task", "finalize_result")
        workflow.add_edge("finalize_result", END)
        
        return workflow.compile()
    
    def _analyze_task(self, state: AgentState) -> AgentState:
        """Analyze the incoming task."""
        task = state["current_task"]
        
        analysis_prompt = f"""
        Analyze this task and determine the best approach:
        Task: {task}
        
        Provide a brief analysis of what needs to be done.
        """
        
        response = self.llm.invoke([
            SystemMessage(content="You are a helpful assistant that analyzes tasks."),
            HumanMessage(content=analysis_prompt)
        ])
        
        state["messages"].append({
            "role": "analysis",
            "content": response.content
        })
        
        return state
    
    def _process_task(self, state: AgentState) -> AgentState:
        """Process the main task."""
        task = state["current_task"]
        analysis = state["messages"][-1]["content"]
        
        processing_prompt = f"""
        Based on the analysis: {analysis}
        
        Now complete this task: {task}
        
        Provide a detailed and helpful response.
        """
        
        response = self.llm.invoke([
            SystemMessage(content="You are a helpful assistant that completes tasks efficiently."),
            HumanMessage(content=processing_prompt)
        ])
        
        state["messages"].append({
            "role": "processing",
            "content": response.content
        })
        
        return state
    
    def _finalize_result(self, state: AgentState) -> AgentState:
        """Finalize the result."""
        processing_result = state["messages"][-1]["content"]
        
        state["result"] = processing_result
        state["iteration_count"] = state.get("iteration_count", 0) + 1
        
        return state
    
    def run(self, task: str) -> Dict[str, Any]:
        """Run the agent with a given task."""
        initial_state = {
            "messages": [],
            "current_task": task,
            "result": "",
            "iteration_count": 0
        }
        
        final_state = self.graph.invoke(initial_state)
        
        return {
            "task": task,
            "result": final_state["result"],
            "messages": final_state["messages"],
            "iteration_count": final_state["iteration_count"]
        }

# Example usage function
async def simple_agent_example():
    """Example of how to use the SimpleAgent."""
    agent = SimpleAgent()
    
    # Example task
    result = agent.run("Explain the benefits of using LangGraph for AI workflows")
    
    print("Task:", result["task"])
    print("Result:", result["result"])
    print("Iterations:", result["iteration_count"])
    
    return result 