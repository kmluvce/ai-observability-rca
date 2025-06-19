from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import uuid
from typing import List, Optional
import pandas as pd
import io

from models.schemas import ObservabilityData, BulkUploadResponse, RCAResponse
from services.rca_service import RCAService
from services.rag_service import RAGService
from database.chroma_db import ChromaDBManager

app = FastAPI(title="AI Observability RCA System", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Initialize services
chroma_manager = ChromaDBManager()
rag_service = RAGService(chroma_manager)
rca_service = RCAService(rag_service)

@app.on_startup
async def startup_event():
    """Initialize database and services on startup"""
    await chroma_manager.initialize()
    print("ChromaDB initialized successfully")

@app.get("/", response_class=HTMLResponse)
async def get_main_page():
    """Serve the main HTML page"""
    with open("frontend/index.html", "r") as file:
        return HTMLResponse(content=file.read())

@app.get("/bulk-upload", response_class=HTMLResponse)
async def get_bulk_upload_page():
    """Serve the bulk upload HTML page"""
    with open("frontend/bulk_upload.html", "r") as file:
        return HTMLResponse(content=file.read())

@app.post("/api/analyze", response_model=RCAResponse)
async def analyze_observability_data(data: ObservabilityData):
    """
    Analyze logs, metrics, and traces to generate RCA
    """
    try:
        # Generate unique ID for this analysis
        analysis_id = str(uuid.uuid4())
        
        # Store the data in ChromaDB
        await rag_service.store_observability_data(
            logs=data.logs,
            metrics=data.metrics,
            traces=data.traces,
            metadata={"analysis_id": analysis_id}
        )
        
        # Generate RCA using LLM and RAG
        rca_result = await rca_service.generate_rca(
            logs=data.logs,
            metrics=data.metrics,
            traces=data.traces
        )
        
        # Store the RCA result
        await rag_service.store_rca_result(
            analysis_id=analysis_id,
            rca_result=rca_result,
            original_data=data
        )
        
        return RCAResponse(
            analysis_id=analysis_id,
            rca_result=rca_result,
            status="success"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/bulk-upload", response_model=BulkUploadResponse)
async def bulk_upload_data(
    logs_file: Optional[UploadFile] = File(None),
    metrics_file: Optional[UploadFile] = File(None),
    traces_file: Optional[UploadFile] = File(None),
    rca_file: Optional[UploadFile] = File(None)
):
    """
    Bulk upload logs, metrics, traces, and RCA data
    """
    try:
        uploaded_files = []
        processed_count = 0
        
        # Process each uploaded file
        files_map = {
            "logs": logs_file,
            "metrics": metrics_file,
            "traces": traces_file,
            "rca": rca_file
        }
        
        for file_type, file in files_map.items():
            if file and file.filename:
                content = await file.read()
                
                # Determine file format and process
                if file.filename.endswith('.json'):
                    data = json.loads(content.decode('utf-8'))
                elif file.filename.endswith(('.csv', '.xlsx')):
                    if file.filename.endswith('.csv'):
                        df = pd.read_csv(io.StringIO(content.decode('utf-8')))
                    else:
                        df = pd.read_excel(io.BytesIO(content))
                    data = df.to_dict('records')
                else:
                    # Treat as text
                    data = content.decode('utf-8')
                
                # Store in ChromaDB
                await rag_service.bulk_store_data(file_type, data)
                
                uploaded_files.append({
                    "type": file_type,
                    "filename": file.filename,
                    "size": len(content)
                })
                processed_count += len(data) if isinstance(data, list) else 1
        
        return BulkUploadResponse(
            uploaded_files=uploaded_files,
            total_processed=processed_count,
            status="success"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk upload failed: {str(e)}")

@app.get("/api/search-similar")
async def search_similar_cases(query: str, limit: int = 5):
    """
    Search for similar historical cases using RAG
    """
    try:
        similar_cases = await rag_service.search_similar_cases(query, limit)
        return {"similar_cases": similar_cases}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "AI Observability RCA System is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
