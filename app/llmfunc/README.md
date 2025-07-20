# LangGraph AI Workflows for Workmate Backend

This module contains LangGraph-powered AI workflows that can be integrated into your FastAPI backend to provide intelligent features.

## 🚀 Features

### 1. Simple Agent (`simple_agent.py`)
A basic LangGraph agent that can handle general AI tasks with a simple workflow:
- Task Analysis → Processing → Result Finalization
- Perfect for straightforward AI queries and assistance

### 2. Multi-Agent System (`multi_agent_system.py`)
A collaborative multi-agent workflow with specialized roles:
- **Coordinator**: Routes tasks to appropriate agents
- **Researcher**: Gathers comprehensive information
- **Analyst**: Analyzes data and provides insights
- **Writer**: Creates polished final outputs

### 3. Product Analyzer (`product_analyzer.py`)
Specialized workflow for product analysis and business intelligence:
- Market Analysis
- Pricing Strategy Analysis
- Business Recommendations
- Comprehensive Reporting

## 📋 Prerequisites

### Environment Variables
Create a `.env` file in your project root:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_PROJECT=workmate-backend
```

### Dependencies
All required dependencies are in `requirements.txt`. Install them:

```bash
pip install -r requirements.txt
```

## 🛠️ Installation & Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

3. **Test the Installation**:
   ```python
   from app.llmfunc.simple_agent import SimpleAgent
   
   agent = SimpleAgent()
   result = agent.run("Hello, test the system!")
   print(result)
   ```

## 💻 Usage Examples

### Simple Agent

```python
from app.llmfunc.simple_agent import SimpleAgent

# Initialize agent
agent = SimpleAgent()

# Run a task
result = agent.run("Explain the benefits of microservices")

print("Task:", result['task'])
print("Result:", result['result'])
print("Iterations:", result['iteration_count'])
```

### Multi-Agent Workflow

```python
from app.llmfunc.multi_agent_system import MultiAgentWorkflow

# Initialize workflow
workflow = MultiAgentWorkflow()

# Run a complex query
result = workflow.run("Research AI trends and analyze their business impact")

print("Query:", result['query'])
print("Final Result:", result['final_result'])
print("Research Output:", result['researcher_output'])
print("Analysis:", result['analyst_output'])
```

### Product Analyzer

```python
from app.llmfunc.product_analyzer import ProductAnalyzer

# Initialize analyzer
analyzer = ProductAnalyzer()

# Analyze a product
product_data = {
    "name": "Smart Watch Pro",
    "category": "Wearables",
    "description": "Advanced smartwatch with health monitoring",
    "price": 299.99,
    "brand": "TechCorp"
}

result = analyzer.analyze_product(product_data)

print("Product:", result['product_name'])
print("Confidence:", result['confidence_score'])
print("Market Analysis:", result['market_analysis'])
print("Recommendations:", result['recommendations'])
```

## 🌐 FastAPI Integration

### Add Routes to Your Server

In your `server.py` or main FastAPI app:

```python
from fastapi import FastAPI
from app.llmfunc.examples import create_langgraph_routes

app = FastAPI()

# Add LangGraph routes
langgraph_router = create_langgraph_routes()
app.include_router(langgraph_router)

# Your existing routes...
```

### Available Endpoints

After integration, you'll have these AI endpoints:

- `POST /ai/simple-agent` - Run simple AI tasks
- `POST /ai/multi-agent` - Run complex multi-agent workflows
- `POST /ai/analyze-product` - Analyze products with AI
- `GET /ai/analyze-product/{product_id}` - Analyze product by ID

### Example API Calls

```bash
# Simple Agent
curl -X POST "http://localhost:8000/ai/simple-agent" \
  -H "Content-Type: application/json" \
  -d '{"task": "Explain REST API best practices"}'

# Multi-Agent
curl -X POST "http://localhost:8000/ai/multi-agent" \
  -H "Content-Type: application/json" \
  -d '{"query": "Research market trends in e-commerce"}'

# Product Analysis
curl -X POST "http://localhost:8000/ai/analyze-product" \
  -H "Content-Type: application/json" \
  -d '{
    "product_data": {
      "name": "Wireless Headphones",
      "category": "Electronics",
      "price": 149.99,
      "description": "Premium wireless headphones"
    }
  }'
```

## 🧪 Running Examples

### Run All Demos
```python
from app.llmfunc.examples import run_all_demos
import asyncio

asyncio.run(run_all_demos())
```

### Run Individual Examples
```python
# Simple Agent Demo
from app.llmfunc.simple_agent import simple_agent_example
import asyncio
asyncio.run(simple_agent_example())

# Multi-Agent Demo
from app.llmfunc.multi_agent_system import multi_agent_example
import asyncio
asyncio.run(multi_agent_example())

# Product Analyzer Demo
from app.llmfunc.product_analyzer import product_analyzer_example
import asyncio
asyncio.run(product_analyzer_example())
```

## 🔧 Configuration

### Model Configuration
You can customize the AI models used in `config.py`:

```python
from app.llmfunc.config import config

# Use different models
config.default_model = "gpt-4o"  # More powerful
config.temperature = 0.3        # More creative
```

### Custom Agent Configuration
```python
# Use specific model for an agent
agent = SimpleAgent(model_name="gpt-4o")

# Use different model for workflow
workflow = MultiAgentWorkflow(model_name="gpt-4o-mini")
```

## 🔌 Integration with Existing Backend

### With Product System
The Product Analyzer can integrate with your existing product repository:

```python
# In product_analyzer.py, modify analyze_product_by_id
def analyze_product_by_id(self, product_id: str):
    # Replace with your actual product repository
    from app.repository.product_repository import ProductRepository
    
    repo = ProductRepository()
    product = repo.get_by_id(product_id)
    
    if not product:
        raise ValueError(f"Product {product_id} not found")
    
    return self.analyze_product(product.dict())
```

### With Order System
You can create custom workflows for order analysis:

```python
# Example: Order Analysis Workflow
from app.llmfunc.config import config
from langgraph.graph import StateGraph

class OrderAnalyzer:
    def __init__(self):
        self.llm = ChatOpenAI(**config.get_llm_config())
    
    def analyze_order_patterns(self, orders_data):
        # Implement order analysis logic
        pass
```

## 🚨 Error Handling

All LangGraph components include error handling:

```python
try:
    agent = SimpleAgent()
    result = agent.run("Your task here")
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## 📊 Monitoring with LangSmith

If you set `LANGSMITH_API_KEY`, all workflows will be automatically tracked:

- View workflow execution traces
- Monitor performance metrics
- Debug agent behavior
- Track token usage

## 🎯 Next Steps

1. **Test the basic setup** with simple examples
2. **Integrate with your existing endpoints** gradually
3. **Customize workflows** for your specific business needs
4. **Add monitoring** with LangSmith for production use
5. **Extend with more agents** as needed

## 📝 Notes

- All components are designed to work with your existing FastAPI architecture
- The Product Analyzer can be easily integrated with your product repository
- Multi-agent workflows are perfect for complex business analysis tasks
- Simple agents work great for customer support and general AI assistance

## 🤝 Contributing

To add new LangGraph workflows:

1. Create a new file in `app/llmfunc/`
2. Follow the existing patterns for state management
3. Add to `__init__.py` exports
4. Create example usage in `examples.py`
5. Document in this README

---

**Ready to add AI superpowers to your workmate backend! 🚀** 