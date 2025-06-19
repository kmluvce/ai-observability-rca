#!/usr/bin/env python3
"""
Setup script for AI Observability RCA System
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
def read_requirements(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line.strip() and not line.startswith('#')]

requirements = read_requirements('requirements.txt')

setup(
    name="ai-observability-rca",
    version="1.0.0",
    author="AI Observability Team",
    author_email="team@aiobservability.com",
    description="Generative AI-Driven Observability for Automated Root Cause Analysis in Modern IT Systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ai-observability/rca-system",
    project_urls={
        "Bug Tracker": "https://github.com/ai-observability/rca-system/issues",
        "Documentation": "https://github.com/ai-observability/rca-system/wiki",
        "Source Code": "https://github.com/ai-observability/rca-system",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Systems Administration",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.20.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.18.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "ai-rca=run:main",
            "ai-observability-rca=run:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.html", "*.css", "*.js", "*.json", "*.md", "*.txt"],
        "frontend": ["**/*"],
        "frontend/static": ["**/*"],
    },
    keywords=[
        "ai", "artificial intelligence", "observability", "monitoring", 
        "root cause analysis", "rca", "llm", "rag", "ollama", "llama3",
        "chromadb", "fastapi", "devops", "sre", "system administration"
    ],
    zip_safe=False,
)

# Post-installation setup
def post_install():
    """Run post-installation setup"""
    import os
    from pathlib import Path
    
    print("🔧 Running post-installation setup...")
    
    # Create data directories
    directories = [
        "data",
        "data/chroma_db", 
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")
    
    # Create default configuration
    config_content = """# AI Observability RCA System Configuration
# Copy this file to .env to customize settings

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3

# ChromaDB Configuration  
CHROMA_DB_PATH=./data/chroma_db

# Server Configuration
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# Security (set strong values in production)
SECRET_KEY=your-secret-key-here
API_KEY=your-api-key-here
"""
    
    config_file = Path("config.env.example")
    if not config_file.exists():
        config_file.write_text(config_content)
        print(f"✓ Created example config: {config_file}")
    
    print("\n🎉 Installation complete!")
    print("\nNext steps:")
    print("1. Install and start Ollama: https://ollama.ai")
    print("2. Pull Llama3 model: ollama pull llama3")
    print("3. Start the system: python run.py")
    print("4. Open browser to: http://localhost:8000")

if __name__ == "__main__":
    # This runs during 'python setup.py install'
    post_install()
