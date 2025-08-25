#!/usr/bin/env python3
"""
Configuration settings for the RAG Multi-Agent System
====================================================

This module contains configuration settings that can be customized
for different deployment environments and use cases.
"""

import os
from typing import Dict, Any

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

DATABASE_CONFIG = {
    "db_path": os.getenv("RAG_DB_PATH", "rag_documents.db"),
    "backup_enabled": True,
    "backup_interval_hours": 24,
    "max_db_size_mb": 1000,  # Maximum database size in MB
}

# =============================================================================
# DOCUMENT PROCESSING CONFIGURATION
# =============================================================================

DOCUMENT_CONFIG = {
    "supported_file_types": [".txt", ".md", ".pdf", ".docx", ".html"],
    "max_file_size_mb": 50,  # Maximum file size in MB
    "default_chunk_size": 500,  # Default chunk size in tokens
    "default_overlap": 50,   # Default overlap between chunks
    "min_chunk_size": 100,   # Minimum chunk size
    "max_chunk_size": 1000,  # Maximum chunk size
}

# =============================================================================
# EMBEDDING CONFIGURATION
# =============================================================================

EMBEDDING_CONFIG = {
    "model_type": "mock",  # Options: "mock", "openai", "sentence_transformers", "cohere"
    "embedding_dimension": 384,  # Dimension of embedding vectors
    "batch_size": 32,     # Batch size for embedding generation
    "max_retries": 3,     # Maximum retries for embedding generation
    
    # OpenAI configuration (if using OpenAI embeddings)
    "openai_model": "text-embedding-ada-002",
    "openai_api_key": os.getenv("OPENAI_API_KEY"),
    
    # Sentence Transformers configuration
    "sentence_transformer_model": "all-MiniLM-L6-v2",
    
    # Cohere configuration
    "cohere_api_key": os.getenv("COHERE_API_KEY"),
    "cohere_model": "embed-english-v2.0",
}

# =============================================================================
# RETRIEVAL CONFIGURATION
# =============================================================================

RETRIEVAL_CONFIG = {
    "default_top_k": 5,      # Default number of documents to retrieve
    "max_top_k": 20,         # Maximum number of documents to retrieve
    "similarity_threshold": 0.1,  # Minimum similarity score
    "rerank_enabled": True,   # Enable re-ranking of results
    "diversity_factor": 0.3,  # Factor for promoting diversity in results
}

# =============================================================================
# SYNTHESIS CONFIGURATION
# =============================================================================

SYNTHESIS_CONFIG = {
    "max_context_length": 4000,  # Maximum context length for synthesis
    "include_citations": True,    # Include source citations in responses
    "confidence_threshold": 0.7,  # Minimum confidence for information inclusion
    "max_sources": 10,           # Maximum number of sources to cite
}

# =============================================================================
# AGENT CONFIGURATION
# =============================================================================

AGENT_CONFIG = {
    "model_provider": "github_copilot",  # Options: "github_copilot", "openai", "anthropic"
    "model_name": "gpt-4o",
    "temperature": 0.1,          # Lower temperature for more consistent responses
    "max_tokens": 2000,          # Maximum tokens per response
    "timeout_seconds": 60,       # Timeout for agent responses
}

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

LOGGING_CONFIG = {
    "log_level": "INFO",         # Options: "DEBUG", "INFO", "WARNING", "ERROR"
    "log_file": "rag_system.log",
    "max_log_size_mb": 100,      # Maximum log file size in MB
    "backup_count": 5,           # Number of backup log files to keep
    "log_queries": True,         # Log user queries for analysis
    "log_responses": True,       # Log system responses
}

# =============================================================================
# PERFORMANCE CONFIGURATION
# =============================================================================

PERFORMANCE_CONFIG = {
    "enable_caching": True,      # Enable response caching
    "cache_ttl_seconds": 3600,   # Cache time-to-live in seconds
    "max_cache_size": 1000,      # Maximum number of cached responses
    "parallel_processing": True,  # Enable parallel document processing
    "max_workers": 4,            # Maximum number of worker threads
}

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================

SECURITY_CONFIG = {
    "sanitize_inputs": True,     # Sanitize user inputs
    "rate_limiting": True,       # Enable rate limiting
    "max_requests_per_minute": 60,  # Maximum requests per minute per user
    "allowed_file_types": [".txt", ".md", ".pdf", ".docx"],
    "max_query_length": 1000,    # Maximum query length in characters
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_config(config_name: str) -> Dict[str, Any]:
    """Get configuration by name."""
    configs = {
        "database": DATABASE_CONFIG,
        "document": DOCUMENT_CONFIG,
        "embedding": EMBEDDING_CONFIG,
        "retrieval": RETRIEVAL_CONFIG,
        "synthesis": SYNTHESIS_CONFIG,
        "agent": AGENT_CONFIG,
        "logging": LOGGING_CONFIG,
        "performance": PERFORMANCE_CONFIG,
        "security": SECURITY_CONFIG,
    }
    return configs.get(config_name, {})


def update_config(config_name: str, updates: Dict[str, Any]) -> bool:
    """Update configuration with new values."""
    try:
        config = get_config(config_name)
        if config:
            config.update(updates)
            return True
        return False
    except Exception:
        return False


def validate_config() -> Dict[str, bool]:
    """Validate all configuration settings."""
    validation_results = {}
    
    # Validate database config
    db_config = get_config("database")
    validation_results["database"] = (
        isinstance(db_config.get("max_db_size_mb"), int) and
        db_config.get("max_db_size_mb", 0) > 0
    )
    
    # Validate document config
    doc_config = get_config("document")
    validation_results["document"] = (
        isinstance(doc_config.get("default_chunk_size"), int) and
        doc_config.get("default_chunk_size", 0) > 0 and
        doc_config.get("default_overlap", 0) >= 0
    )
    
    # Validate embedding config
    embed_config = get_config("embedding")
    validation_results["embedding"] = (
        embed_config.get("model_type") in ["mock", "openai", "sentence_transformers", "cohere"] and
        isinstance(embed_config.get("embedding_dimension"), int) and
        embed_config.get("embedding_dimension", 0) > 0
    )
    
    # Validate retrieval config
    retrieval_config = get_config("retrieval")
    validation_results["retrieval"] = (
        isinstance(retrieval_config.get("default_top_k"), int) and
        retrieval_config.get("default_top_k", 0) > 0 and
        0 <= retrieval_config.get("similarity_threshold", 0) <= 1
    )
    
    return validation_results


def get_environment_config() -> Dict[str, str]:
    """Get environment-specific configuration."""
    return {
        "environment": os.getenv("RAG_ENVIRONMENT", "development"),
        "debug_mode": os.getenv("RAG_DEBUG", "false").lower() == "true",
        "api_base_url": os.getenv("RAG_API_BASE_URL", "http://localhost:8000"),
        "external_db_url": os.getenv("RAG_EXTERNAL_DB_URL"),
        "redis_url": os.getenv("REDIS_URL"),
        "elasticsearch_url": os.getenv("ELASTICSEARCH_URL"),
    }


# =============================================================================
# CONFIGURATION PRESETS
# =============================================================================

DEVELOPMENT_PRESET = {
    "database": {"db_path": "dev_rag_documents.db"},
    "logging": {"log_level": "DEBUG"},
    "performance": {"enable_caching": False},
    "security": {"rate_limiting": False},
}

PRODUCTION_PRESET = {
    "database": {"db_path": "/data/rag_documents.db", "backup_enabled": True},
    "logging": {"log_level": "INFO"},
    "performance": {"enable_caching": True, "max_workers": 8},
    "security": {"rate_limiting": True, "max_requests_per_minute": 30},
}

TESTING_PRESET = {
    "database": {"db_path": ":memory:"},  # In-memory database for testing
    "logging": {"log_level": "WARNING"},
    "performance": {"enable_caching": False},
    "security": {"rate_limiting": False},
}


def apply_preset(preset_name: str) -> bool:
    """Apply a configuration preset."""
    presets = {
        "development": DEVELOPMENT_PRESET,
        "production": PRODUCTION_PRESET,
        "testing": TESTING_PRESET,
    }
    
    preset = presets.get(preset_name)
    if not preset:
        return False
    
    try:
        for config_name, updates in preset.items():
            update_config(config_name, updates)
        return True
    except Exception:
        return False


if __name__ == "__main__":
    # Configuration validation and testing
    print("RAG System Configuration")
    print("=" * 30)
    
    # Validate configuration
    validation_results = validate_config()
    print("Configuration Validation:")
    for config_name, is_valid in validation_results.items():
        status = "✅ Valid" if is_valid else "❌ Invalid"
        print(f"  {config_name}: {status}")
    
    # Show environment configuration
    env_config = get_environment_config()
    print(f"\nEnvironment Configuration:")
    for key, value in env_config.items():
        print(f"  {key}: {value}")
    
    # Show available presets
    print(f"\nAvailable Presets:")
    print("  - development: Optimized for local development")
    print("  - production: Optimized for production deployment")
    print("  - testing: Optimized for automated testing")