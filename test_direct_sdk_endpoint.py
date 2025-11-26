"""Test endpoint that calls SDK directly without the service layer."""

from fastapi import FastAPI
from aliexpress_api import AliexpressApi, models
import uvicorn

app = FastAPI()

@app.get("/test-direct")
def test_direct():
    """Call SDK directly."""
    try:
        # Create SDK instance directly
        api = AliexpressApi(
            key="520934",
            secret="inC2NFrIr1SvtTGlUWxyQec6EvHyjIno",
            language=models.Language.EN,
            currency=models.Currency.USD,
            tracking_id="gpt_chat"
        )
        
        # Call API
        categories = api.get_parent_categories()
        
        return {
            "success": True,
            "count": len(categories) if categories else 0,
            "categories": [
                {"id": str(cat.category_id), "name": cat.category_name}
                for cat in (categories[:5] if categories else [])
            ]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
