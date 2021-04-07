from typing import Any, Dict

from fastapi import Body, FastAPI
from pydantic import BaseModel

app = FastAPI()


class Intent(BaseModel):
    displayName: str


class Request(BaseModel):
    intent: Intent
    parameters: Dict[str, Any]


@app.post("/")
async def home(queryResult: Request = Body(..., embed=True)):
    intent = queryResult.intent.displayName
    count = len(queryResult.parameters)
    text = f"I'm responding to the {intent} intent with {count} slots found: "
    text += ",".join(queryResult.parameters.values())
    return {"fulfillmentText": text}