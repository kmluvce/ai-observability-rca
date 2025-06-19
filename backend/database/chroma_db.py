import chromadb
from chromadb.config import Settings
import uuid
from typing import List, Dict, Any, Optional
import os
from datetime import datetime
import json

class ChromaDBManager:
    """Manages ChromaDB for RAG functionality"""
    
    def __init__(self, persist_directory: str = "./data/chroma_db"):
        self.persist_directory = persist_directory
        self.client = None
        self.collections = {}
        
        # Ensure directory exists
        os.makedirs(persist_directory, exist_ok=True)
    
    async def initialize(self):
        """Initialize ChromaDB client and collections"""
        try:
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Create collections for different data types
            collection_names = [
                "observability_logs",
                "observability_metrics", 
                "observability_traces",
                "rca_results",
                "historical_cases"
            ]
            
            for name in collection_names:
                try:
                    self.collections[name] = self.client.get_collection(name)
                except:
                    self.collections[name] = self.client.create_collection(
                        name=name,
                        metadata={"hnsw:space": "cosine"}
                    )
            
            print(f"ChromaDB initialized with {len(self.collections)} collections")
            
        except Exception as e:
            print(f"Error initializing ChromaDB: {e}")
            raise
    
    async def store_observability_data(self, logs: str, metrics: str, traces: str, metadata: Dict[str, Any] = None):
        """Store observability data in respective collections"""
        try:
            base_metadata = {
                "timestamp": datetime.now().isoformat(),
                "analysis_id": metadata.get("analysis_id", str(uuid.uuid4()))
            }
            
            if metadata:
                base_metadata.update(metadata)
            
            # Store logs
            if logs.strip():
                self.collections["observability_logs"].add(
                    documents=[logs],
                    metadatas=[{**base_metadata, "data_type": "logs"}],
                    ids=[f"logs_{base_metadata['analysis_id']}"]
                )
            
            # Store metrics
            if metrics.strip():
                self.collections["observability_metrics"].add(
                    documents=[metrics],
                    metadatas=[{**base_metadata, "data_type": "metrics"}],
                    ids=[f"metrics_{base_metadata['analysis_id']}"]
                )
            
            # Store traces
            if traces.strip():
                self.collections["observability_traces"].add(
                    documents=[traces],
                    metadatas=[{**base_metadata, "data_type": "traces"}],
                    ids=[f"traces_{base_metadata['analysis_id']}"]
                )
            
            return base_metadata["analysis_id"]
            
        except Exception as e:
            print(f"Error storing observability data: {e}")
            raise
    
    async def store_rca_result(self, analysis_id: str, rca_result: str, original_data: Any = None):
        """Store RCA result with reference to original data"""
        try:
            metadata = {
                "analysis_id": analysis_id,
                "timestamp": datetime.now().isoformat(),
                "data_type": "rca_result"
            }
            
            if original_data:
                metadata["has_original_data"] = True
            
            self.collections["rca_results"].add(
                documents=[rca_result],
                metadatas=[metadata],
                ids=[f"rca_{analysis_id}"]
            )
            
            # Also store as historical case for future RAG queries
            combined_text = f"RCA: {rca_result}"
            if original_data:
                combined_text += f"\nLogs: {original_data.logs[:500]}..."
                combined_text += f"\nMetrics: {original_data.metrics[:500]}..."
                combined_text += f"\nTraces: {original_data.traces[:500]}..."
            
            self.collections["historical_cases"].add(
                documents=[combined_text],
                metadatas=[{**metadata, "data_type": "historical_case"}],
                ids=[f"case_{analysis_id}"]
            )
            
        except Exception as e:
            print(f"Error storing RCA result: {e}")
            raise
    
    async def search_similar_cases(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for similar historical cases"""
        try:
            results = self.collections["historical_cases"].query(
                query_texts=[query],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            similar_cases = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    similar_cases.append({
                        "document": doc,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "similarity_score": 1 - results["distances"][0][i] if results["distances"] else 0.0
                    })
            
            return similar_cases
            
        except Exception as e:
            print(f"Error searching similar cases: {e}")
            return []
    
    async def bulk_store_data(self, data_type: str, data: Any):
        """Bulk store data of specific type"""
        try:
            collection_name = f"observability_{data_type}"
            if collection_name not in self.collections:
                self.collections[collection_name] = self.client.create_collection(
                    name=collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
            
            if isinstance(data, list):
                documents = []
                metadatas = []
                ids = []
                
                for i, item in enumerate(data):
                    doc_id = f"{data_type}_bulk_{uuid.uuid4()}"
                    
                    if isinstance(item, dict):
                        doc_text = json.dumps(item, indent=2)
                        metadata = {**item, "data_type": data_type, "bulk_upload": True}
                    else:
                        doc_text = str(item)
                        metadata = {"data_type": data_type, "bulk_upload": True}
                    
                    metadata["timestamp"] = datetime.now().isoformat()
                    
                    documents.append(doc_text)
                    metadatas.append(metadata)
                    ids.append(doc_id)
                
                # Add in batches to avoid memory issues
                batch_size = 100
                for i in range(0, len(documents), batch_size):
                    batch_docs = documents[i:i+batch_size]
                    batch_metas = metadatas[i:i+batch_size]
                    batch_ids = ids[i:i+batch_size]
                    
                    self.collections[collection_name].add(
                        documents=batch_docs,
                        metadatas=batch_metas,
                        ids=batch_ids
                    )
            else:
                # Single document
                doc_id = f"{data_type}_bulk_{uuid.uuid4()}"
                metadata = {
                    "data_type": data_type,
                    "bulk_upload": True,
                    "timestamp": datetime.now().isoformat()
                }
                
                self.collections[collection_name].add(
                    documents=[str(data)],
                    metadatas=[metadata],
                    ids=[doc_id]
                )
                
        except Exception as e:
            print(f"Error in bulk store: {e}")
            raise
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about all collections"""
        stats = {}
        for name, collection in self.collections.items():
            try:
                count = collection.count()
                stats[name] = {"document_count": count}
            except Exception as e:
                stats[name] = {"error": str(e)}
        
        return stats
