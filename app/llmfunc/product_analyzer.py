"""
Product analyzer using LangGraph for intelligent product analysis and recommendations.
This integrates with the existing product system in the workmate backend.
"""

from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from .config import config
import os

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "test_7908"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"

class ProductAnalysisState(TypedDict):
    """State definition for product analysis workflow."""
    product_data: Dict[str, Any]
    analysis_type: str
    market_analysis: str
    pricing_analysis: str
    recommendation: str
    confidence_score: float
    final_report: str
    
class ProductAnalyzer:
    """LangGraph workflow for intelligent product analysis."""
    
    def __init__(self, model_name: str = None):
        """Initialize the product analyzer."""
        config.validate_config()
        self.llm = ChatOpenAI(**config.get_llm_config(model_name))
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the product analysis workflow graph."""
        workflow = StateGraph(ProductAnalysisState)
        
        # Add analysis nodes
        workflow.add_node("market_analyzer", self._market_analyzer)
        workflow.add_node("pricing_analyzer", self._pricing_analyzer)
        workflow.add_node("recommendation_engine", self._recommendation_engine)
        workflow.add_node("report_generator", self._report_generator)
        
        # Set up the workflow
        workflow.set_entry_point("market_analyzer")
        workflow.add_edge("market_analyzer", "pricing_analyzer")
        workflow.add_edge("pricing_analyzer", "recommendation_engine")
        workflow.add_edge("recommendation_engine", "report_generator")
        workflow.add_edge("report_generator", END)
        
        return workflow.compile()
    
    def _market_analyzer(self, state: ProductAnalysisState) -> ProductAnalysisState:
        """Analyze market position and competition."""
        product = state["product_data"]
        
        market_prompt = f"""
        Analyze the market position for this product:
        
        Product Name: {product.get('name', 'Unknown')}
        Category: {product.get('category', 'Unknown')}
        Description: {product.get('description', 'No description')}
        Current Price: {product.get('price', 'Not specified')}
        
        Provide analysis on:
        1. Market positioning
        2. Target audience
        3. Competitive landscape
        4. Market trends
        5. Unique selling propositions
        
        Be specific and actionable.
        """
        
        response = self.llm.invoke([
            SystemMessage(content="You are a market analysis expert specializing in product positioning."),
            HumanMessage(content=market_prompt)
        ])
        
        state["market_analysis"] = response.content
        return state
    
    def _pricing_analyzer(self, state: ProductAnalysisState) -> ProductAnalysisState:
        """Analyze pricing strategy and recommendations."""
        product = state["product_data"]
        market_analysis = state["market_analysis"]
        
        pricing_prompt = f"""
        Based on the market analysis, analyze the pricing strategy:
        
        Product Details:
        - Name: {product.get('name', 'Unknown')}
        - Current Price: {product.get('price', 'Not specified')}
        - Category: {product.get('category', 'Unknown')}
        
        Market Analysis: {market_analysis}
        
        Provide pricing analysis including:
        1. Price competitiveness
        2. Value proposition assessment
        3. Pricing strategy recommendations
        4. Potential price optimization
        5. Revenue impact projections
        """
        
        response = self.llm.invoke([
            SystemMessage(content="You are a pricing strategy expert with deep knowledge of market dynamics."),
            HumanMessage(content=pricing_prompt)
        ])
        
        state["pricing_analysis"] = response.content
        return state
    
    def _recommendation_engine(self, state: ProductAnalysisState) -> ProductAnalysisState:
        """Generate actionable recommendations."""
        product = state["product_data"]
        market_analysis = state["market_analysis"]
        pricing_analysis = state["pricing_analysis"]
        
        recommendation_prompt = f"""
        Generate comprehensive recommendations based on the analysis:
        
        Product: {product.get('name', 'Unknown')}
        Market Analysis: {market_analysis}
        Pricing Analysis: {pricing_analysis}
        
        Provide specific recommendations for:
        1. Product positioning improvements
        2. Marketing strategies
        3. Pricing adjustments
        4. Feature enhancements
        5. Target market expansion
        6. Risk mitigation strategies
        
        Also provide a confidence score (0-100) for your recommendations.
        """
        
        response = self.llm.invoke([
            SystemMessage(content="You are a strategic business consultant providing actionable recommendations."),
            HumanMessage(content=recommendation_prompt)
        ])
        
        state["recommendation"] = response.content
        
        # Extract confidence score (simplified logic)
        confidence_score = 85.0  # In real implementation, you'd parse this from the LLM response
        state["confidence_score"] = confidence_score
        
        return state
    
    def _report_generator(self, state: ProductAnalysisState) -> ProductAnalysisState:
        """Generate final comprehensive report."""
        product = state["product_data"]
        
        report_prompt = f"""
        Create a comprehensive product analysis report:
        
        Product: {product.get('name', 'Unknown')}
        
        Market Analysis: {state['market_analysis']}
        Pricing Analysis: {state['pricing_analysis']}
        Recommendations: {state['recommendation']}
        Confidence Score: {state['confidence_score']}%
        
        Format as a professional business report with:
        - Executive Summary
        - Key Findings
        - Detailed Analysis
        - Recommendations
        - Implementation Timeline
        - Success Metrics
        """
        
        response = self.llm.invoke([
            SystemMessage(content="You are a business analyst creating professional reports."),
            HumanMessage(content=report_prompt)
        ])
        
        state["final_report"] = response.content
        return state
    
    def analyze_product(self, product_data: Dict[str, Any], analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Analyze a product and generate recommendations."""
        initial_state = {
            "product_data": product_data,
            "analysis_type": analysis_type,
            "market_analysis": "",
            "pricing_analysis": "",
            "recommendation": "",
            "confidence_score": 0.0,
            "final_report": ""
        }
        
        final_state = self.graph.invoke(initial_state)
        
        return {
            "product_name": product_data.get("name", "Unknown"),
            "analysis_type": analysis_type,
            "market_analysis": final_state["market_analysis"],
            "pricing_analysis": final_state["pricing_analysis"],
            "recommendations": final_state["recommendation"],
            "confidence_score": final_state["confidence_score"],
            "final_report": final_state["final_report"]
        }
    
    def analyze_product_by_id(self, product_id: str) -> Dict[str, Any]:
        """Analyze a product by its ID (integrate with your product repository)."""
        # This would integrate with your existing product repository
        # For now, using mock data
        mock_product = {
            "id": product_id,
            "name": "Sample Product",
            "category": "Electronics",
            "description": "A sample product for analysis",
            "price": 99.99
        }
        
        return self.analyze_product(mock_product)

# Integration helper functions
def create_product_analysis_endpoint():
    """Helper function to create FastAPI endpoint for product analysis."""
    from fastapi import APIRouter
    
    router = APIRouter()
    analyzer = ProductAnalyzer()
    
    @router.post("/analyze-product")
    async def analyze_product_endpoint(product_data: Dict[str, Any]):
        """Endpoint to analyze a product using LangGraph."""
        try:
            result = analyzer.analyze_product(product_data)
            return {"success": True, "analysis": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @router.get("/analyze-product/{product_id}")
    async def analyze_product_by_id_endpoint(product_id: str):
        """Endpoint to analyze a product by ID."""
        try:
            result = analyzer.analyze_product_by_id(product_id)
            return {"success": True, "analysis": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    return router

# Example usage function
async def product_analyzer_example():
    """Example of how to use the ProductAnalyzer."""
    analyzer = ProductAnalyzer()
    
    # Example product data
    sample_product = {
        "name": "Wireless Bluetooth Headphones",
        "category": "Electronics",
        "description": "High-quality wireless headphones with noise cancellation",
        "price": 149.99,
        "brand": "TechSound"
    }
    
    result = analyzer.analyze_product(sample_product)
    
    print("Product Analysis Complete!")
    print("Product:", result["product_name"])
    print("Confidence Score:", result["confidence_score"])
    print("\nFinal Report:")
    print(result["final_report"])
    
    return result 