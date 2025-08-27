#!/usr/bin/env python3
"""
Environment Setup Script for Core RAG Examples

This script helps set up the environment and configuration needed
to run the RAG examples with proper Google Cloud credentials.
"""

import os
import sys
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    try:
        import google.adk
        print("✅ google-adk is installed")
    except ImportError:
        print("❌ google-adk not found. Please install with:")
        print("   pip install 'google-adk[extensions]'")
        return False
    
    try:
        from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
        print("✅ VertexAiRagRetrieval is available")
    except ImportError:
        print("❌ VertexAiRagRetrieval not available. Please install extensions:")
        print("   pip install 'google-adk[extensions]'")
        return False
    
    try:
        from google.adk.tools.retrieval.files_retrieval import FilesRetrieval
        print("✅ FilesRetrieval is available")
    except ImportError:
        print("❌ FilesRetrieval not available. Please install extensions:")
        print("   pip install 'google-adk[extensions]'")
        return False
    
    return True


def setup_environment_file():
    """Create a .env file template for configuration."""
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return
    
    env_template = """# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-project-id

# Vertex AI RAG Configuration
RAG_CORPUS=projects/your-project/locations/us-central1/ragCorpora/your-corpus-id

# Vertex AI Search Configuration
VERTEX_AI_SEARCH_DATASTORE=projects/your-project/locations/global/collections/default_collection/dataStores/your-datastore

# Optional: Google Search API (for GoogleSearchTool)
GOOGLE_SEARCH_API_KEY=your-google-search-api-key
GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id

# Optional: Authentication
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json
"""
    
    env_file.write_text(env_template.strip())
    print("📝 Created .env template file")
    print("   Please edit .env with your actual configuration values")


def check_authentication():
    """Check Google Cloud authentication."""
    print("\n🔐 Checking Google Cloud authentication...")
    
    # Check for service account key
    if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        key_path = Path(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
        if key_path.exists():
            print("✅ Service account key found")
            return True
        else:
            print("❌ Service account key path not found")
    
    # Check for gcloud CLI authentication
    try:
        import subprocess
        result = subprocess.run(
            ["gcloud", "auth", "list", "--filter=status:ACTIVE", "--format=value(account)"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            print("✅ gcloud CLI authentication found")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("⚠️  No Google Cloud authentication found")
    print("   Please set up authentication using one of these methods:")
    print("   1. Set GOOGLE_APPLICATION_CREDENTIALS environment variable")
    print("   2. Run 'gcloud auth application-default login'")
    print("   3. Use service account key in your .env file")
    
    return False


def create_sample_rag_corpus_guide():
    """Create a guide for setting up a RAG corpus."""
    guide_file = Path("RAG_CORPUS_SETUP.md")
    
    if guide_file.exists():
        return
    
    guide_content = """# Setting Up Vertex AI RAG Corpus

To use the Vertex AI RAG examples, you need to create a RAG corpus in Google Cloud.

## Steps:

1. **Enable APIs**:
   ```bash
   gcloud services enable aiplatform.googleapis.com
   gcloud services enable discoveryengine.googleapis.com
   ```

2. **Create a RAG Corpus**:
   ```bash
   # Using gcloud CLI
   gcloud ai rag-corpora create --display-name="my-rag-corpus" --location=us-central1
   ```

3. **Upload Documents**:
   ```bash
   # Upload files to your corpus
   gcloud ai rag-corpora files upload --corpus=CORPUS_ID --location=us-central1 --source-uri=gs://your-bucket/documents/
   ```

4. **Get Corpus ID**:
   ```bash
   # List your corpora to get the ID
   gcloud ai rag-corpora list --location=us-central1
   ```

5. **Update .env file**:
   ```
   RAG_CORPUS=projects/YOUR_PROJECT/locations/us-central1/ragCorpora/CORPUS_ID
   ```

## Alternative: Use Console

1. Go to [Vertex AI Console](https://console.cloud.google.com/vertex-ai)
2. Navigate to "Agent Builder" > "Data Stores"
3. Create a new data store
4. Upload your documents
5. Copy the resource name to your .env file

## Testing

Once set up, you can test with:
```bash
python basic_rag_agent.py
```
"""
    
    guide_file.write_text(guide_content.strip())
    print("📖 Created RAG_CORPUS_SETUP.md guide")


def main():
    """Main setup function."""
    print("🚀 Setting up Core RAG Examples Environment")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install required dependencies first:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    print()
    
    # Setup environment file
    setup_environment_file()
    
    # Check authentication
    auth_ok = check_authentication()
    
    # Create guides
    create_sample_rag_corpus_guide()
    
    print("\n" + "=" * 50)
    print("🎉 Setup Complete!")
    print()
    
    if auth_ok:
        print("✅ You're ready to run the examples!")
        print("   Try starting with: python files_rag_agent.py")
    else:
        print("⚠️  Please set up Google Cloud authentication first")
        print("   Then you can run: python files_rag_agent.py")
    
    print("\n📚 Available examples:")
    print("   - files_rag_agent.py (works without cloud setup)")
    print("   - basic_rag_agent.py (requires RAG corpus)")
    print("   - memory_rag_agent.py (requires RAG corpus)")
    print("   - multi_tool_rag_agent.py (requires full setup)")
    
    print("\n📖 See README.md and RAG_CORPUS_SETUP.md for detailed instructions")


if __name__ == "__main__":
    main()