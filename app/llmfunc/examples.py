"""
Examples and demonstrations of LangGraph functionality.
Run this file to see all the LangGraph components in action.
"""

import asyncio
from typing import Dict, Any
from .simple_agent import SimpleAgent, simple_agent_example
from .multi_agent_system import MultiAgentWorkflow, multi_agent_example
from .product_analyzer import ProductAnalyzer, product_analyzer_example

async def run_simple_agent_demo():
    """Demonstrate the simple agent functionality."""
    print("=" * 60)
    print("SIMPLE AGENT DEMO")
    print("=" * 60)
    
    agent = SimpleAgent()
    
    # Example tasks
    tasks = [
        "Explain the benefits of microservices architecture",
        "What are the best practices for API design?",
        "How can I optimize database queries for better performance?"
    ]
    
    for i, task in enumerate(tasks, 1):
        print(f"\n--- Task {i}: {task} ---")
        result = agent.run(task)
        print(f"Result: {result['result'][:200]}...")
        print(f"Iterations: {result['iteration_count']}")

async def run_multi_agent_demo():
    """Demonstrate the multi-agent system."""
    print("\n" + "=" * 60)
    print("MULTI-AGENT SYSTEM DEMO")
    print("=" * 60)
    
    workflow = MultiAgentWorkflow()
    
    # Example queries
    queries = [
        "Research the latest trends in AI and machine learning for business applications",
        "Analyze the impact of remote work on software development productivity"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n--- Query {i}: {query} ---")
        result = workflow.run(query)
        print(f"Final Result: {result['final_result'][:200]}...")
        print(f"Research Phase: {result['researcher_output'][:100]}...")
        print(f"Analysis Phase: {result['analyst_output'][:100]}...")

async def run_product_analyzer_demo():
    """Demonstrate the product analyzer."""
    print("\n" + "=" * 60)
    print("PRODUCT ANALYZER DEMO")
    print("=" * 60)
    
    analyzer = ProductAnalyzer()
    
    # Example products
    products = [
        {
            "name": "Smart Fitness Tracker",
            "category": "Wearables",
            "description": "Advanced fitness tracker with heart rate monitoring and GPS",
            "price": 199.99,
            "brand": "FitTech"
        },
        {
            "name": "Organic Coffee Beans",
            "category": "Food & Beverages", 
            "description": "Premium organic coffee beans from sustainable farms",
            "price": 24.99,
            "brand": "GreenBean Co"
        }
    ]
    
    for i, product in enumerate(products, 1):
        print(f"\n--- Product {i}: {product['name']} ---")
        result = analyzer.analyze_product(product)
        print(f"Confidence Score: {result['confidence_score']}%")
        print(f"Market Analysis: {result['market_analysis'][:150]}...")
        print(f"Recommendations: {result['recommendations'][:150]}...")

async def run_all_demos():
    """Run all LangGraph demonstrations."""
    print("🚀 Starting LangGraph Demonstrations")
    print("This will showcase all the AI workflows in the workmate backend")
    
    try:
        # Run each demo
        await run_simple_agent_demo()
        await run_multi_agent_demo() 
        await run_product_analyzer_demo()
        
        print("\n" + "=" * 60)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nLangGraph components are ready for integration with your workmate backend.")
        print("You can now use these AI workflows in your FastAPI endpoints.")
        
    except Exception as e:
        print(f"\n❌ Error running demos: {str(e)}")
        print("Make sure to set your OPENAI_API_KEY environment variable.")

def create_langgraph_routes():
    """Create FastAPI routes for all LangGraph functionality."""
    from fastapi import APIRouter, HTTPException
    from pydantic import BaseModel
    
    router = APIRouter(prefix="/ai", tags=["AI & LangGraph"])
    
    # Request models
    class SimpleTaskRequest(BaseModel):
        task: str
        model_name: str = None
    
    class MultiAgentRequest(BaseModel):
        query: str
        model_name: str = None
    
    class ProductAnalysisRequest(BaseModel):
        product_data: Dict[str, Any]
        analysis_type: str = "comprehensive"
    
    # Simple Agent endpoints
    @router.post("/simple-agent")
    async def run_simple_agent(request: SimpleTaskRequest):
        """Run a simple AI agent task."""
        try:
            agent = SimpleAgent(request.model_name)
            result = agent.run(request.task)
            return {"success": True, "result": result}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    # Multi-Agent endpoints
    @router.post("/multi-agent")
    async def run_multi_agent(request: MultiAgentRequest):
        """Run a multi-agent workflow."""
        try:
            workflow = MultiAgentWorkflow(request.model_name)
            result = workflow.run(request.query)
            return {"success": True, "result": result}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    # Product Analyzer endpoints
    @router.post("/analyze-product")
    async def analyze_product(request: ProductAnalysisRequest):
        """Analyze a product using AI."""
        try:
            analyzer = ProductAnalyzer()
            result = analyzer.analyze_product(
                request.product_data, 
                request.analysis_type
            )
            return {"success": True, "analysis": result}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/analyze-product/{product_id}")
    async def analyze_product_by_id(product_id: str):
        """Analyze a product by its ID."""
        try:
            analyzer = ProductAnalyzer()
            result = analyzer.analyze_product_by_id(product_id)
            return {"success": True, "analysis": result}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return router

# Main execution
if __name__ == "__main__":
    print("🎯 LangGraph Examples for Workmate Backend")
    print("This demonstrates AI-powered workflows using LangGraph")
    print("\nTo run the demos, execute:")
    print("python -m app.llmfunc.examples")
    print("\nOr run individual components:")
    print("- Simple Agent: from app.llmfunc.simple_agent import simple_agent_example")
    print("- Multi-Agent: from app.llmfunc.multi_agent_system import multi_agent_example") 
    print("- Product Analyzer: from app.llmfunc.product_analyzer import product_analyzer_example")
    
    # Uncomment to run demos (requires OPENAI_API_KEY)
    # asyncio.run(run_all_demos()) 