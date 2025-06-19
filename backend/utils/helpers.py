"""
Helper Utilities
================

Common utility functions used throughout the application.
"""

import re
import uuid
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

def format_timestamp(timestamp: Any) -> str:
    """Format timestamp to ISO string format"""
    if isinstance(timestamp, datetime):
        return timestamp.isoformat()
    elif isinstance(timestamp, str):
        try:
            return datetime.fromisoformat(timestamp.replace('Z', '+00:00')).isoformat()
        except:
            return timestamp
    else:
        return datetime.now().isoformat()

def sanitize_text(text: str, max_length: int = 10000) -> str:
    """Sanitize and truncate text for safe processing"""
    if not isinstance(text, str):
        text = str(text)
    
    # Remove potentially harmful characters
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Remove non-ASCII
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    text = text.strip()
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    return text

def extract_error_patterns(log_text: str) -> List[Dict[str, Any]]:
    """Extract common error patterns from log text"""
    patterns = [
        {
            'name': 'HTTP_ERROR',
            'pattern': r'HTTP (\d{3})',
            'description': 'HTTP status codes'
        },
        {
            'name': 'EXCEPTION',
            'pattern': r'(Exception|Error|Failed|Timeout)',
            'description': 'General exceptions and errors'
        },
        {
            'name': 'DATABASE_ERROR',
            'pattern': r'(database|sql|connection|query).*?(error|failed|timeout)',
            'description': 'Database related errors'
        },
        {
            'name': 'NETWORK_ERROR',
            'pattern': r'(network|connection|socket).*?(error|failed|refused|timeout)',
            'description': 'Network connectivity issues'
        },
        {
            'name': 'MEMORY_ERROR',
            'pattern': r'(memory|heap|oom|out of memory)',
            'description': 'Memory related issues'
        },
        {
            'name': 'DISK_ERROR',
            'pattern': r'(disk|storage|filesystem).*?(full|error|failed)',
            'description': 'Disk and storage issues'
        }
    ]
    
    found_patterns = []
    
    for pattern_info in patterns:
        matches = re.findall(pattern_info['pattern'], log_text, re.IGNORECASE)
        if matches:
            found_patterns.append({
                'pattern_name': pattern_info['name'],
                'description': pattern_info['description'],
                'matches': matches,
                'count': len(matches)
            })
    
    return found_patterns

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate simple similarity score between two texts"""
    if not text1 or not text2:
        return 0.0
    
    # Convert to lowercase and split into words
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    # Calculate Jaccard similarity
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    if union == 0:
        return 0.0
    
    return intersection / union

def generate_analysis_id() -> str:
    """Generate unique analysis ID"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_part = str(uuid.uuid4())[:8]
    return f"RCA_{timestamp}_{random_part}"

def extract_metrics_summary(metrics_text: str) -> Dict[str, Any]:
    """Extract summary statistics from metrics text"""
    summary = {
        'cpu_usage': [],
        'memory_usage': [],
        'disk_io': [],
        'network_io': [],
        'error_rate': [],
        'response_time': []
    }
    
    # Look for common metric patterns
    patterns = {
        'cpu': r'cpu[_\s]*usage?[:\s]*(\d+\.?\d*)%?',
        'memory': r'memory[_\s]*usage?[:\s]*(\d+\.?\d*)%?',
        'disk': r'disk[_\s]*io[:\s]*(\d+\.?\d*)',
        'network': r'network[_\s]*io[:\s]*(\d+\.?\d*)',
        'error': r'error[_\s]*rate[:\s]*(\d+\.?\d*)%?',
        'response': r'response[_\s]*time[:\s]*(\d+\.?\d*)'
    }
    
    for metric_type, pattern in patterns.items():
        matches = re.findall(pattern, metrics_text, re.IGNORECASE)
        if matches:
            values = [float(m) for m in matches if m.replace('.', '').isdigit()]
            if values:
                summary[f'{metric_type}_values'] = values
                summary[f'{metric_type}_avg'] = sum(values) / len(values)
                summary[f'{metric_type}_max'] = max(values)
                summary[f'{metric_type}_min'] = min(values)
    
    return summary

def extract_trace_summary(trace_text: str) -> Dict[str, Any]:
    """Extract summary from trace data"""
    summary = {
        'total_spans': 0,
        'error_spans': 0,
        'slow_spans': [],
        'services': set(),
        'operations': set()
    }
    
    try:
        # Try to parse as JSON first
        if trace_text.strip().startswith('{'):
            trace_data = json.loads(trace_text)
            
            if 'spans' in trace_data:
                spans = trace_data['spans']
                summary['total_spans'] = len(spans)
                
                for span in spans:
                    # Count errors
                    if span.get('status') == 'error' or span.get('error'):
                        summary['error_spans'] += 1
                    
                    # Check for slow spans (>1000ms)
                    duration = span.get('duration_ms', 0)
                    if duration > 1000:
                        summary['slow_spans'].append({
                            'operation': span.get('operation', 'unknown'),
                            'duration_ms': duration
                        })
                    
                    # Collect services and operations
                    if 'service' in span:
                        summary['services'].add(span['service'])
                    if 'operation' in span:
                        summary['operations'].add(span['operation'])
        
        # Convert sets to lists for JSON serialization
        summary['services'] = list(summary['services'])
        summary['operations'] = list(summary['operations'])
        
    except (json.JSONDecodeError, KeyError):
        # Fallback to text analysis
        lines = trace_text.split('\n')
        summary['total_spans'] = len([l for l in lines if 'span' in l.lower()])
        summary['error_spans'] = len([l for l in lines if 'error' in l.lower()])
    
    return summary

def create_hash(text: str) -> str:
    """Create SHA-256 hash of text"""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]

def validate_json_data(data: str) -> Dict[str, Any]:
    """Validate and parse JSON data"""
    try:
        parsed = json.loads(data)
        return {
            'valid': True,
            'data': parsed,
            'type': type(parsed).__name__,
            'size': len(str(parsed))
        }
    except json.JSONDecodeError as e:
        return {
            'valid': False,
            'error': str(e),
            'data': None
        }

def truncate_text(text: str, max_words: int = 100) -> str:
    """Truncate text to maximum number of words"""
    if not text:
        return ""
    
    words = text.split()
    if len(words) <= max_words:
        return text
    
    return ' '.join(words[:max_words]) + "..."

def extract_timestamps(text: str) -> List[str]:
    """Extract timestamps from text using common patterns"""
    timestamp_patterns = [
        r'\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}',  # ISO format
        r'\d{2}/\d{2}/\d{4}\s\d{2}:\d{2}:\d{2}',      # US format
        r'\d{2}-\d{2}-\d{4}\s\d{2}:\d{2}:\d{2}',      # EU format
        r'\w{3}\s\d{1,2}\s\d{2}:\d{2}:\d{2}',         # Syslog format
    ]
    
    timestamps = []
    for pattern in timestamp_patterns:
        matches = re.findall(pattern, text)
        timestamps.extend(matches)
    
    return list(set(timestamps))  # Remove duplicates

def format_duration(milliseconds: float) -> str:
    """Format duration in milliseconds to human readable format"""
    if milliseconds < 1000:
        return f"{milliseconds:.1f}ms"
    elif milliseconds < 60000:
        return f"{milliseconds/1000:.1f}s"
    elif milliseconds < 3600000:
        return f"{milliseconds/60000:.1f}m"
    else:
        return f"{milliseconds/3600000:.1f}h"

def clean_log_entry(log_entry: str) -> str:
    """Clean and normalize a single log entry"""
    # Remove ANSI color codes
    log_entry = re.sub(r'\x1b\[[0-9;]*m', '', log_entry)
    
    # Normalize whitespace
    log_entry = re.sub(r'\s+', ' ', log_entry)
    
    # Remove leading/trailing whitespace
    log_entry = log_entry.strip()
    
    return log_entry

def parse_key_value_pairs(text: str) -> Dict[str, str]:
    """Extract key=value pairs from text"""
    pattern = r'(\w+)=([^\s,]+)'
    matches = re.findall(pattern, text)
    return dict(matches)
