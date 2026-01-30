"""Tests for GitHub Copilot authentication."""

import pytest


@pytest.mark.requires_api
@pytest.mark.asyncio
async def test_github_copilot_llm():
    """Test GitHub Copilot LLM authentication and basic functionality."""
    from llama_index.llms.litellm import LiteLLM
    
    llm = LiteLLM(
        model="github_copilot/gpt-4o-mini",
        api_key="oauth2",
        temperature=0.7,
    )
    
    response = await llm.acomplete("Say 'Hello from GitHub Copilot!'")
    
    assert response is not None
    assert len(response.text) > 0
    assert "hello" in response.text.lower() or "hi" in response.text.lower()


@pytest.mark.requires_api
@pytest.mark.asyncio
async def test_github_copilot_embeddings():
    """Test GitHub Copilot embeddings."""
    from llama_index.embeddings.litellm import LiteLLMEmbedding
    
    embed_model = LiteLLMEmbedding(
        model_name="github_copilot/text-embedding-3-small",
        api_key="oauth2",
    )
    
    result = await embed_model.aget_text_embedding("test")
    
    assert result is not None
    assert len(result) == 1536  # text-embedding-3-small dimension
    assert all(isinstance(x, float) for x in result)


@pytest.mark.requires_api
def test_auth_integration():
    """Integration test for authentication (placeholder)."""
    # This test can be expanded to check:
    # - API key validation
    # - Rate limiting
    # - Error handling
    pass
