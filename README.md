# 🔍 AI Observability RCA System

**Generative AI-Driven Observability for Automated Root Cause Analysis in Modern IT Systems**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Ollama](https://img.shields.io/badge/Ollama-LLama3-orange.svg)](https://ollama.ai/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-0.4+-purple.svg)](https://www.trychroma.com/)

## 🚀 Overview

This system leverages **Generative AI** and **Retrieval-Augmented Generation (RAG)** to automatically analyze observability data (logs, metrics, traces) and generate comprehensive root cause analysis reports. Built with modern technologies including **Ollama/Llama3** for LLM capabilities and **ChromaDB** for vector storage.

### ✨ Key Features

- **🤖 AI-Powered RCA**: Automated root cause analysis using Llama3
- **📊 Multi-Modal Analysis**: Processes logs, metrics, and traces together
- **🧠 RAG Integration**: Learns from historical cases for better analysis
- **📁 Bulk Upload**: Support for bulk data ingestion (JSON, CSV, XLSX, TXT)
- **🔍 Similarity Search**: Find similar historical incidents
- **📱 Modern UI**: Clean, responsive web interface
- **🚫 No Docker Required**: Simple local installation and setup

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend UI   │────│  FastAPI Backend │────│  Ollama/Llama3  │
│   (HTML/CSS/JS) │    │                 │    │      (LLM)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                │
                       ┌─────────────────┐
                       │    ChromaDB     │
                       │ (Vector Store)  │
                       └─────────────────┘
```

### 🧩 Components

1. **Frontend**: Clean web interface for data input and results visualization
2. **FastAPI Backend**: RESTful API handling requests and orchestrating services
3. **LLM Service**: Integration with Ollama/Llama3 for text generation
4. **RAG Service**: Retrieval-augmented generation using ChromaDB
5. **RCA Service**: Core root cause analysis orchestration
6. **Database Layer**: ChromaDB for vector storage and similarity search

## 📋 Prerequisites

- **Python 3.8+**
- **Ollama** (for LLM capabilities)
- **Git** (for cloning the repository)

## 🛠️ Quick Start

### 1. Install Ollama

```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Download from https://ollama.ai/download
```

### 2. Pull Llama3 Model

```bash
ollama pull llama3
```

### 3. Start Ollama Server

```bash
ollama serve
```

### 4. Clone and Setup Project

```bash
# Clone repository
git clone <repository-url>
cd ai-observability-rca

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 5. Run the System

```bash
python run.py
```

### 6. Access the Application

Open your browser to: **http://localhost:8000**

## 🎯 Usage Guide

### 📊 Single Analysis

1. Navigate to the main page
2. Fill in the three text boxes:
   - **Logs**: Paste your application/system logs
   - **Metrics**: Paste performance metrics data
   - **Traces**: Paste distributed tracing data
3. Click **"Generate RCA Analysis"**
4. Review the generated root cause analysis
5. Optionally copy or download the results

### 📁 Bulk Upload

1. Click on **"Bulk Upload"** in the navigation
2. Select files for each data type (JSON, CSV, XLSX, or TXT)
3. Click **"Upload Files"** to process in bulk
4. View upload results and database statistics

### 🔍 Search Historical Cases

Use the search functionality to find similar past incidents and learn from historical patterns.

## 📁 Project Structure

```
ai-observability-rca/
├── backend/                    # Backend Python code
│   ├── __init__.py
│   ├── main.py                # FastAPI application
│   ├── models/                # Data models and schemas
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── services/              # Core business logic
│   │   ├── __init__.py
│   │   ├── llm_service.py     # Ollama/LLM integration
│   │   ├── rag_service.py     # RAG functionality
│   │   └── rca_service.py     # RCA orchestration
│   ├── database/              # Database layer
│   │   ├── __init__.py
│   │   └── chroma_db.py       # ChromaDB management
│   └── utils/                 # Utility functions
│       ├── __init__.py
│       └── helpers.py
├── frontend/                  # Frontend web interface
│   ├── index.html            # Main RCA page
│   ├── bulk_upload.html      # Bulk upload page
│   └── static/
│       ├── css/
│       │   └── style.css     # Styling
│       └── js/
│           ├── main.js       # Main page functionality
│           └── bulk_upload.js # Bulk upload functionality
├── data/                     # Data storage
│   └── chroma_db/           # ChromaDB persistence
├── requirements.txt         # Python dependencies
├── setup.py                # Installation script
├── run.py                  # Main application runner
└── README.md              # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3

# ChromaDB Configuration
CHROMA_DB_PATH=./data/chroma_db

# Server Configuration
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
```

### Command Line Options

```bash
python run.py --help

Options:
  --host HOST       Host to bind to (default: 0.0.0.0)
  --port PORT       Port to bind to (default: 8000)
  --reload          Enable auto-reload for development
  --debug           Enable debug mode
  --workers NUM     Number of worker processes
  --log-level LEVEL Logging level (debug, info, warning, error)
```

## 📚 API Documentation

Once running, visit **http://localhost:8000/docs** for interactive API documentation.

### Key Endpoints

- `POST /api/analyze` - Analyze observability data and generate RCA
- `POST /api/bulk-upload` - Bulk upload historical data
- `GET /api/search-similar` - Search for similar historical cases
- `GET /api/health` - Health check endpoint

## 🧪 Example Data Formats

### Logs Example
```
2025-06-19 10:30:15 ERROR [ApplicationService] Database connection failed: timeout after 30s
2025-06-19 10:30:16 WARN [ConnectionPool] Retrying connection attempt 1/3
2025-06-19 10:30:18 ERROR [ConnectionPool] Connection attempt failed: Connection refused
```

### Metrics Example
```
timestamp,cpu_usage,memory_usage,disk_io,network_io
2025-06-19T10:30:00Z,85.2,78.5,120.3,45.7
2025-06-19T10:30:30Z,92.1,82.1,134.7,52.3
```

### Traces Example
```json
{
  "trace_id": "abc123def456",
  "spans": [
    {
      "span_id": "span001",
      "operation": "http_request",
      "duration_ms": 1250,
      "status": "error"
    }
  ]
}
```

## 🐛 Troubleshooting

### Common Issues

1. **Ollama Connection Failed**
   ```bash
   # Check if Ollama is running
   curl http://localhost:11434/api/version
   
   # Start Ollama if not running
   ollama serve
   ```

2. **Llama3 Model Not Found**
   ```bash
   # Pull the model
   ollama pull llama3
   
   # List available models
   ollama list
   ```

3. **Port Already in Use**
   ```bash
   # Run on different port
   python run.py --port 8001
   ```

4. **ChromaDB Permission Issues**
   ```bash
   # Ensure data directory is writable
   chmod -R 755 data/
   ```

## 🔒 Security Considerations

- **Development Only**: This setup is intended for development/testing
- **Production Deployment**: 
  - Use proper authentication
  - Set strong secret keys
  - Configure HTTPS
  - Implement rate limiting
  - Secure database access

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Ollama Team** for the excellent LLM runtime
- **Meta** for the Llama3 model
- **ChromaDB** for vector database capabilities
- **FastAPI** for the robust web framework

## 📞 Support

For support, questions, or feedback:

- 📧 Email: support@aiobservability.com
- 🐛 Issues: [GitHub Issues](https://github.com/ai-observability/rca-system/issues)
- 📖 Documentation: [Wiki](https://github.com/ai-observability/rca-system/wiki)

---

**⭐ Star this repository if you find it helpful!**
