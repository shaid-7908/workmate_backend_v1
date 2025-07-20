"""
Multi-agent system using LangGraph for collaborative AI tasks.
"""

from typing import TypedDict, List, Dict, Any, Literal
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from .config import config

class MultiAgentState(TypedDict):
    """State definition for the multi-agent system."""
    original_query: str
    current_task: str
    researcher_output: str
    analyst_output: str
    writer_output: str
    final_result: str
    next_agent: str
    iteration_count: int

class MultiAgentWorkflow:
    """A multi-agent system with specialized agents."""
    
    def __init__(self, model_name: str = None):
        """Initialize the multi-agent workflow."""
        config.validate_config()
        self.llm = ChatOpenAI(**config.get_llm_config(model_name))
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the multi-agent workflow graph."""
        workflow = StateGraph(MultiAgentState)
        
        # Add agent nodes
        workflow.add_node("coordinator", self._coordinator)
        workflow.add_node("researcher", self._researcher)
        workflow.add_node("analyst", self._analyst)
        workflow.add_node("writer", self._writer)
        workflow.add_node("finalizer", self._finalizer)
        
        # Add conditional routing
        workflow.set_entry_point("coordinator")
        workflow.add_conditional_edges(
            "coordinator",
            self._route_next_agent,
            {
                "researcher": "researcher",
                "analyst": "analyst", 
                "writer": "writer",
                "end": END
            }
        )
        
        workflow.add_edge("researcher", "analyst")
        workflow.add_edge("analyst", "writer") 
        workflow.add_edge("writer", "finalizer")
        workflow.add_edge("finalizer", END)
        
        return workflow.compile()
    
    def _coordinator(self, state: MultiAgentState) -> MultiAgentState:
        """Coordinate the workflow and determine next steps."""
        query = state["original_query"]
        
        coordination_prompt = f"""
        You are a coordinator managing a team of AI agents. 
        
        Query: {query}
        
        Determine what type of task this is and set the workflow:
        - If it needs research: start with researcher
        - If it's analytical: start with analyst
        - If it's creative writing: start with writer
        
        Set the current_task and next_agent.
        """
        
        response = self.llm.invoke([
            SystemMessage(content="You are a workflow coordinator."),
            HumanMessage(content=coordination_prompt)
        ])
        
        # Simple logic to determine next agent (in real scenario, you'd parse the LLM response)
        if "research" in query.lower() or "find" in query.lower():
            state["next_agent"] = "researcher"
        elif "analyze" in query.lower() or "compare" in query.lower():
            state["next_agent"] = "analyst"
        else:
            state["next_agent"] = "researcher"  # Default to researcher
            
        state["current_task"] = query
        return state
    
    def _researcher(self, state: MultiAgentState) -> MultiAgentState:
        """Research agent - gathers information."""
        task = state["current_task"]
        
        research_prompt = f"""
        You are a research specialist. Your job is to gather comprehensive information.
        
        Research task: {task}
        
        Provide detailed research findings, key facts, and relevant information.
        Focus on accuracy and completeness.
        """
        
        response = self.llm.invoke([
            SystemMessage(content="You are an expert researcher."),
            HumanMessage(content=research_prompt)
        ])
        
        state["researcher_output"] = response.content
        return state
    
    def _analyst(self, state: MultiAgentState) -> MultiAgentState:
        """Analyst agent - analyzes information."""
        research_data = state.get("researcher_output", "")
        task = state["current_task"]
        
        analysis_prompt = f"""
        You are an analysis specialist. Analyze the research data and provide insights.
        
        Research Data: {research_data}
        Original Task: {task}
        
        Provide detailed analysis, identify patterns, draw conclusions, and make recommendations.
        """
        
        response = self.llm.invoke([
            SystemMessage(content="You are an expert analyst."),
            HumanMessage(content=analysis_prompt)
        ])
        
        state["analyst_output"] = response.content
        return state
    
    def _writer(self, state: MultiAgentState) -> MultiAgentState:
        """Writer agent - creates final output."""
        research_data = state.get("researcher_output", "")
        analysis_data = state.get("analyst_output", "")
        task = state["current_task"]
        
        writing_prompt = f"""
        You are a professional writer. Create a well-structured, comprehensive response.
        
        Research: {research_data}
        Analysis: {analysis_data}
        Original Task: {task}
        
        Write a clear, engaging, and informative response that addresses the original query.
        """
        
        response = self.llm.invoke([
            SystemMessage(content="You are a professional writer."),
            HumanMessage(content=writing_prompt)
        ])
        
        state["writer_output"] = response.content
        return state
    
    def _finalizer(self, state: MultiAgentState) -> MultiAgentState:
        """Finalize the result."""
        state["final_result"] = state["writer_output"]
        state["iteration_count"] = state.get("iteration_count", 0) + 1
        return state
    
    def _route_next_agent(self, state: MultiAgentState) -> Literal["researcher", "analyst", "writer", "end"]:
        """Route to the next agent based on state."""
        next_agent = state.get("next_agent", "researcher")
        if next_agent in ["researcher", "analyst", "writer"]:
            return next_agent
        return "end"
    
    def run(self, query: str) -> Dict[str, Any]:
        """Run the multi-agent workflow."""
        initial_state = {
            "original_query": query,
            "current_task": "",
            "researcher_output": "",
            "analyst_output": "",
            "writer_output": "",
            "final_result": "",
            "next_agent": "",
            "iteration_count": 0
        }
        
        final_state = self.graph.invoke(initial_state)
        
        return {
            "query": query,
            "final_result": final_state["final_result"],
            "researcher_output": final_state["researcher_output"],
            "analyst_output": final_state["analyst_output"],
            "writer_output": final_state["writer_output"],
            "iteration_count": final_state["iteration_count"]
        }

# Example usage function
async def multi_agent_example():
    """Example of how to use the MultiAgentWorkflow."""
    workflow = MultiAgentWorkflow()
    
    # Example query
    result = workflow.run("Research the latest trends in e-commerce and analyze their impact on small businesses")
    
    print("Query:", result["query"])
    print("Final Result:", result["final_result"])
    print("Iterations:", result["iteration_count"])
    
    return result 