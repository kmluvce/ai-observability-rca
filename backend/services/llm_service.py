import ollama
import asyncio
from typing import List, Dict, Any, Optional
import json
import re

class LLMService:
    """Service for interacting with Ollama and Llama3"""
    
    def __init__(self, model_name: str = "llama3", host: str = "http://localhost:11434"):
        self.model_name = model_name
        self.host = host
        self.client = ollama.Client(host=host)
        
    async def ensure_model_available(self):
        """Ensure the specified model is available"""
        try:
            # Check if model exists
            models = self.client.list()
            model_names = [model["name"] for model in models["models"]]
            
            if self.model_name not in model_names and f"{self.model_name}:latest" not in model_names:
                print(f"Model {self.model_name} not found. Pulling...")
                self.client.pull(self.model_name)
                print(f"Model {self.model_name} pulled successfully")
            else:
                print(f"Model {self.model_name} is available")
                
        except Exception as e:
            print(f"Error checking/pulling model: {e}")
            raise
    
    async def generate_response(self, prompt: str, system_prompt: str = None) -> str:
        """Generate response from Llama3"""
        try:
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user", 
                "content": prompt
            })
            
            response = self.client.chat(
                model=self.model_name,
                messages=messages,
                options={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 2048
                }
            )
            
            return response["message"]["content"]
            
        except Exception as e:
            print(f"Error generating LLM response: {e}")
            raise
    
    async def analyze_observability_data(self, logs: str, metrics: str, traces: str, similar_cases: List[Dict] = None) -> str:
        """Analyze observability data and generate RCA"""
        
        system_prompt = """You are an expert Site Reliability Engineer (SRE) and DevOps specialist with deep expertise in:
- System observability and monitoring
- Root cause analysis methodologies
- Log analysis and pattern recognition
- Performance metrics interpretation
- Distributed tracing analysis
- Incident management and troubleshooting

Your task is to analyze observability data (logs, metrics, traces) and provide comprehensive root cause analysis.

Guidelines for analysis:
1. Examine logs for error patterns, anomalies, and sequence of events
2. Analyze metrics for performance degradation, resource constraints, or unusual patterns
3. Review traces for request flow issues, latency spikes, or service dependencies
4. Consider correlations between different data sources
5. Identify the most likely root cause based on evidence
6. Provide actionable recommendations for resolution
7. Rate your confidence level in the analysis

Format your response as a structured RCA report."""

        # Prepare the analysis prompt
        prompt = f"""
Please analyze the following observability data and provide a comprehensive root cause analysis:

**LOGS:**
{logs[:2000]}...

**METRICS:**
{metrics[:2000]}...

**TRACES:**
{traces[:2000]}...
"""

        # Add similar cases if available
        if similar_cases:
            prompt += "\n**SIMILAR HISTORICAL CASES:**\n"
            for i, case in enumerate(similar_cases[:3]):
                prompt += f"Case {i+1} (Similarity: {case.get('similarity_score', 0):.2f}):\n"
                prompt += f"{case.get('document', '')[:500]}...\n\n"

        prompt += """
**ANALYSIS REQUIREMENTS:**
1. **Root Cause Identification**: What is the primary root cause?
2. **Evidence Summary**: What evidence supports this conclusion?
3. **Impact Assessment**: What systems/services are affected?
4. **Resolution Steps**: What immediate actions should be taken?
5. **Prevention Measures**: How can this be prevented in the future?
6. **Confidence Level**: Rate your confidence (1-10) in this analysis

Please provide a detailed, structured response following the above format.
"""

        return await self.generate_response(prompt, system_prompt)
    
    async def summarize_case(self, rca_result: str) -> str:
        """Generate a summary of an RCA case"""
        system_prompt = "You are an expert at summarizing technical root cause analysis reports. Provide concise, clear summaries that capture the key points."
        
        prompt = f"""
Please provide a concise summary (2-3 sentences) of the following RCA report:

{rca_result}

Focus on:
- The root cause
- The impact
- The resolution approach
"""

        return await self.generate_response(prompt, system_prompt)
    
    async def extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from observability data"""
        system_prompt = "You are an expert at extracting relevant technical keywords from system logs, metrics, and traces."
        
        prompt = f"""
Extract the most relevant technical keywords from the following observability data. 
Focus on:
- Error types and codes
- Service names
- System components
- Performance indicators
- Technology stack components

Return only the keywords as a comma-separated list.

Text: {text[:1000]}...
"""

        response = await self.generate_response(prompt, system_prompt)
        
        # Clean and parse keywords
        keywords = [kw.strip().lower() for kw in response.split(",")]
        keywords = [kw for kw in keywords if kw and len(kw) > 2]
        
        return keywords[:20]  # Limit to top 20 keywords
    
    async def generate_recommendations(self, rca_result: str) -> List[str]:
        """Generate actionable recommendations based on RCA"""
        system_prompt = "You are an expert SRE providing actionable recommendations for system improvements."
        
        prompt = f"""
Based on the following RCA analysis, provide 5-7 specific, actionable recommendations for:
1. Immediate remediation
2. Short-term improvements
3. Long-term prevention

RCA Analysis:
{rca_result}

Format each recommendation as a single sentence starting with an action verb.
"""

        response = await self.generate_response(prompt, system_prompt)
        
        # Parse recommendations into list
        recommendations = []
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            # Remove numbering and bullet points
            line = re.sub(r'^\d+\.?\s*', '', line)
            line = re.sub(r'^[-*]\s*', '', line)
            
            if line and len(line) > 10:
                recommendations.append(line)
        
        return recommendations[:7]  # Limit to 7 recommendations
