from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import base64
from fastapi.middleware.cors import CORSMiddleware

from service import ClassifierServ, Predict
from config import config

class PredictionRequest(BaseModel):
    text: str
    image: Optional[str] = None

class PredictionResponse(BaseModel):
    success: bool
    predicted_class: str
    conf: float

class HealthResponse(BaseModel):
    status: str
    device: str
    model_loaded: bool

classifier_service = ClassifierServ()


app = FastAPI(title = config.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get(config.API_PREFIX+"/health", response_model=HealthResponse)
async def health_check():
    return {
        "status": "healthy",
        "device": str(classifier_service.device),
        "model_loaded": classifier_service.model is not None
    }

@app.post(config.API_PREFIX+"/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    try:
        text = request.text
        if not text or text.strip() == "":
            raise HTTPException(
                status_code=400,
                detail="text is empty"
            )

        image_bytes = None
        if request.image:
            try:
                image_bytes = base64.b64decode(request.image)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid image base64: {str(e)}"
                )



        result = classifier_service.bytes_predict(text, image_bytes)

        return {
            "success": True,
            "predicted_class": result.class_name,
            "conf": result.conf
        }
    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


