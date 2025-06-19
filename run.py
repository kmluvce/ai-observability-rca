#!/usr/bin/env python3
"""
AI Observability RCA System - Main Runner
==========================================

This script starts the AI Observability RCA System.

Usage:
    python run.py [OPTIONS]

Options:
    --host HOST     Host to bind to (default: 0.0.0.0)
    --port PORT     Port to bind to (default: 8000)
    --reload        Enable auto-reload for development
    --debug         Enable debug mode
    --workers NUM   Number of worker processes (default: 1)

Environment Variables:
    OLLAMA_HOST     Ollama server host (default: http://localhost:11434)
    CHROMA_DB_PATH  ChromaDB persistence path (default: ./data/chroma_db)
    LOG_LEVEL       Logging level (default: INFO)
"""

import os
import sys
import argparse
import asyncio
import signal
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

import uvicorn
from backend.main import app

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="AI Observability RCA System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (default: 1)"
    )
    
    parser.add_argument(
        "--log-level",
        default="info",
        choices=["critical", "error", "warning", "info", "debug"],
        help="Log level (default: info)"
    )
    
    return parser.parse_args()

def setup_environment():
    """Setup environment variables and directories"""
    
    # Set default environment variables if not present
    env_defaults = {
        "OLLAMA_HOST": "http://localhost:11434",
        "CHROMA_DB_PATH": "./data/chroma_db",
        "LOG_LEVEL": "INFO"
    }
    
    for key, default_value in env_defaults.items():
        if key not in os.environ:
            os.environ[key] = default_value
    
    # Create necessary directories
    directories = [
        "data",
        "data/chroma_db",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✓ Environment setup complete")

def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import ollama
        print("✓ Ollama client available")
    except ImportError:
        print("✗ Ollama client not found. Install with: pip install ollama")
        return False
    
    try:
        import chromadb
        print("✓ ChromaDB available")
    except ImportError:
        print("✗ ChromaDB not found. Install with: pip install chromadb")
        return False
    
    try:
        import fastapi
        print("✓ FastAPI available")
    except ImportError:
        print("✗ FastAPI not found. Install with: pip install fastapi")
        return False
    
    return True

def check_ollama_connection():
    """Check if Ollama server is running"""
    try:
        import ollama
        
        # Try to connect to Ollama
        client = ollama.Client(host=os.getenv("OLLAMA_HOST", "http://localhost:11434"))
        models = client.list()
        print(f"✓ Connected to Ollama server ({len(models.get('models', []))} models available)")
        
        # Check if llama3 model is available
        model_names = [model["name"] for model in models.get("models", [])]
        if "llama3" in model_names or "llama3:latest" in model_names:
            print("✓ Llama3 model is available")
        else:
            print("⚠ Llama3 model not found. You may need to pull it with: ollama pull llama3")
        
        return True
        
    except Exception as e:
        print(f"✗ Cannot connect to Ollama server: {e}")
        print("  Make sure Ollama is running. Start with: ollama serve")
        return False

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print(f"\n🛑 Received signal {signum}. Shutting down gracefully...")
    sys.exit(0)

def main():
    """Main entry point"""
    print("🚀 Starting AI Observability RCA System...")
    print("=" * 50)
    
    # Parse arguments
    args = parse_arguments()
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Setup environment
    setup_environment()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Missing required dependencies. Please install them and try again.")
        sys.exit(1)
    
    # Check Ollama connection
    if not check_ollama_connection():
        print("\n⚠ Ollama server is not available. Some features may not work.")
        print("  You can still use the system for data upload and storage.")
    
    print("\n" + "=" * 50)
    print("🎯 System checks complete. Starting web server...")
    print(f"📍 Server will be available at: http://{args.host}:{args.port}")
    print(f"📊 Database path: {os.getenv('CHROMA_DB_PATH')}")
    print(f"🤖 Ollama host: {os.getenv('OLLAMA_HOST')}")
    print("=" * 50)
    
    # Configure uvicorn
    config = uvicorn.Config(
        app=app,
        host=args.host,
        port=args.port,
        log_level=args.log_level,
        reload=args.reload,
        workers=args.workers if not args.reload else 1,
        access_log=True
    )
    
    # Start server
    server = uvicorn.Server(config)
    
    try:
        if args.debug:
            # Run in debug mode
            print("🔧 Debug mode enabled")
            uvicorn.run(
                "backend.main:app",
                host=args.host,
                port=args.port,
                log_level="debug",
                reload=True
            )
        else:
            # Run normally
            server.run()
            
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)
    finally:
        print("👋 AI Observability RCA System stopped")

if __name__ == "__main__":
    main()
