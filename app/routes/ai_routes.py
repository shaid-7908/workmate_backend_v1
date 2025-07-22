from fastapi import APIRouter
from app.controller.ai_controller import AiController




router = APIRouter(
    prefix="/api/ai",
    tags=["ai"],
    responses={404: {"description": "Not found"}}
)

ai_controller = AiController()

@router.get("/units-sold/analysis/{limit}")
async def get_units_sold_analysis(limit: int = 10):
    products = ai_controller.top_selling_products_by_unit_sold(limit)
    return {"message": "Units sold analysis", "products": products}


