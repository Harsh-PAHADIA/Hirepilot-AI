from fastapi import APIRouter
from pydantic import BaseModel
import os
import traceback
import sys

from lemma_wrapper import LemmaClient

router = APIRouter()

@router.get("/test-lemma")
def test_lemma_endpoint():
    try:
        has_token = bool(os.environ.get("LEMMA_TOKEN"))
        has_api_key = bool(os.environ.get("LEMMA_API_KEY"))
        
        client = LemmaClient()
        
        res = client._run_agent_sync("jd-analyst", "Test ping")
        
        return {
            "success": True,
            "has_lemma_token_env": has_token,
            "has_lemma_api_key_env": has_api_key,
            "result": res
        }
    except Exception as e:
        return {
            "success": False,
            "has_lemma_token_env": has_token,
            "has_lemma_api_key_env": has_api_key,
            "error_type": type(e).__name__,
            "error_msg": str(e),
            "traceback": traceback.format_exc()
        }
