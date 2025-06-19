from typing import List, Dict, Any, Optional
from database.chroma_db import ChromaDBManager
from services.llm_service import LLMService
import json

class RAGService:
    """Service for Retrieval-Augmented Generation functionality"""
    
    def __init__(self, chroma_manager: ChromaDBManager):
        self.chroma_manager = chroma_manager
        self.llm_service = LLMService()
        
    async def initialize(self):
        """Initialize the RAG service"""
        await self.llm_service.ensure_model_available()
        print("RAG Service initialized successfully")
    
    async def store_observability_data(self, logs: str, metrics: str, traces: str, metadata: Dict[str, Any] = None):
        """Store observability data in ChromaDB"""
        return await self.chroma_manager.store_observability_data(logs, metrics, traces, metadata)
    
    async def store_rca_result(self, analysis_id: str, rca_result: str, original_data: Any = None):
        """Store RCA result in ChromaDB"""
        await self.chroma_manager.store_rca_result(analysis_id, rca_result, original_data)
    
    async def search_similar_cases(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar historical cases using vector similarity"""
        try:
            # Extract keywords from query for better search
            keywords = await self.llm_service.extract_keywords(query)
            enhanced_query = f"{query} {' '.join(keywords)}"
            
            # Search in historical cases
            similar_cases = await self.chroma_manager.search_similar_cases(enhanced_query, limit)
            
            # Enhance results with summaries if needed
            enhanced_cases = []
            for case in similar_cases:
                if case.get("document"):
                    # Extract RCA summary if document is long
                    doc = case["document"]
                    if len(doc) > 500:
                        summary = await self.llm_service.summarize_case(doc)
                        case["summary"] = summary
                    
                    enhanced_cases.append(case)
            
            return enhanced_cases
            
        except Exception as e:
            print(f"Error searching similar cases: {e}")
            return []
    
    async def get_relevant_context(self, logs: str, metrics: str, traces: str) -> Dict[str, Any]:
        """Get relevant historical context for current observability data"""
        try:
            # Combine all data for context search
            combined_data = f"Logs: {logs[:500]} Metrics: {metrics[:500]} Traces: {traces[:500]}"
            
            # Search for similar cases
            similar_cases = await self.search_similar_cases(combined_data, limit=3)
            
            # Extract relevant patterns from logs
            log_keywords = await self.llm_service.extract_keywords(logs)
            metric_keywords = await self.llm_service.extract_keywords(metrics)
            trace_keywords = await self.llm_service.extract_keywords(traces)
            
            return {
                "similar_cases": similar_cases,
                "keywords": {
                    "logs": log_keywords,
                    "metrics": metric_keywords, 
                    "traces": trace_keywords
                },
                "context_available": len(similar_cases) > 0
            }
            
        except Exception as e:
            print(f"Error getting relevant context: {e}")
            return {"similar_cases": [], "keywords": {}, "context_available": False}
    
    async def bulk_store_data(self, data_type: str, data: Any):
        """Bulk store data in ChromaDB"""
        await self.chroma_manager.bulk_store_data(data_type, data)
    
    async def enhance_query_with_context(self, query: str, context_limit: int = 3) -> str:
        """Enhance a search query with relevant historical context"""
        try:
            # Get similar cases for context
            similar_cases = await self.search_similar_cases(query, context_limit)
            
            if not similar_cases:
                return query
            
            # Build enhanced query with context
            enhanced_query = query
            
            context_snippets = []
            for case in similar_cases:
                if case.get("summary"):
                    context_snippets.append(case["summary"])
                elif case.get("document"):
                    # Use first 200 chars as context
                    context_snippets.append(case["document"][:200] + "...")
            
            if context_snippets:
                enhanced_query += f"\n\nRelated historical context:\n{chr(10).join(context_snippets)}"
            
            return enhanced_query
            
        except Exception as e:
            print(f"Error enhancing query: {e}")
            return query
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        return await self.chroma_manager.get_collection_stats()
    
    async def search_by_metadata(self, metadata_filters: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
        """Search cases by metadata filters"""
        try:
            results = []
            
            # Search across different collections
            for collection_name, collection in self.chroma_manager.collections.items():
                try:
                    # ChromaDB doesn't support complex metadata filtering in query
                    # So we'll get all results and filter in memory
                    all_results = collection.get(
                        include=["documents", "metadatas"]
                    )
                    
                    if all_results["documents"] and all_results["metadatas"]:
                        for i, doc in enumerate(all_results["documents"]):
                            metadata = all_results["metadatas"][i]
                            
                            # Check if metadata matches filters
                            match = True
                            for key, value in metadata_filters.items():
                                if key in metadata:
                                    if isinstance(value, str):
                                        if value.lower() not in str(metadata[key]).lower():
                                            match = False
                                            break
                                    elif metadata[key] != value:
                                        match = False
                                        break
                                else:
                                    match = False
                                    break
                            
                            if match:
                                results.append({
                                    "document": doc,
                                    "metadata": metadata,
                                    "collection": collection_name
                                })
                                
                                if len(results) >= limit:
                                    break
                    
                    if len(results) >= limit:
                        break
                        
                except Exception as e:
                    print(f"Error searching collection {collection_name}: {e}")
                    continue
            
            return results[:limit]
            
        except Exception as e:
            print(f"Error in metadata search: {e}")
            return []
