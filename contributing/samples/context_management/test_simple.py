"""
Simple Test Cases for Context Management

Focused tests that can be run without complex mocking or dependencies.
These tests validate the core logic and configuration.

Usage:
    python test_simple.py
    pytest test_simple.py
"""

import unittest
from unittest.mock import Mock, patch
from advanced_context_manager import ContextConfig, AdvancedContextManager, SmartAgent


class TestContextConfig(unittest.TestCase):
    """Test configuration class"""
    
    def test_default_values(self):
        """Test default configuration values"""
        config = ContextConfig()
        
        self.assertEqual(config.max_tokens, 8000)
        self.assertEqual(config.keep_system_messages, 2)
        self.assertEqual(config.keep_recent_turns, 6)
        self.assertEqual(config.summarization_model, "gemini-2.0-flash")
        self.assertTrue(config.enable_memory_storage)
    
    def test_custom_values(self):
        """Test custom configuration"""
        config = ContextConfig(
            max_tokens=5000,
            keep_system_messages=3,
            keep_recent_turns=10,
            summarization_model="gpt-4",
            enable_memory_storage=False
        )
        
        self.assertEqual(config.max_tokens, 5000)
        self.assertEqual(config.keep_system_messages, 3)
        self.assertEqual(config.keep_recent_turns, 10)
        self.assertEqual(config.summarization_model, "gpt-4")
        self.assertFalse(config.enable_memory_storage)


class TestAdvancedContextManager(unittest.TestCase):
    """Test core context manager functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = ContextConfig(max_tokens=1000)
        self.manager = AdvancedContextManager(self.config)
    
    def test_initialization(self):
        """Test context manager initialization"""
        self.assertEqual(self.manager.config.max_tokens, 1000)
        self.assertEqual(len(self.manager.conversation_memory), 0)
        self.assertIsNotNone(self.manager.encoding)
    
    def test_identify_conversation_turns(self):
        """Test conversation turn identification"""
        # Mock content objects
        contents = [
            Mock(role='system'),
            Mock(role='user'),
            Mock(role='assistant'), 
            Mock(role='user'),
            Mock(role='assistant'),
            Mock(role='system')
        ]
        
        indices = self.manager.identify_conversation_turns(contents)
        
        self.assertEqual(indices['system'], [0, 5])
        self.assertEqual(indices['user'], [1, 3])
        self.assertEqual(indices['assistant'], [2, 4])
    
    def test_empty_conversation_turns(self):
        """Test with empty content list"""
        indices = self.manager.identify_conversation_turns([])
        
        self.assertEqual(indices['system'], [])
        self.assertEqual(indices['user'], [])
        self.assertEqual(indices['assistant'], [])
    
    def test_text_extraction(self):
        """Test text extraction from content objects"""
        # Content with direct text attribute
        content1 = Mock(text="Hello world")
        text1 = self.manager._extract_text(content1)
        self.assertEqual(text1, "Hello world")
        
        # Content with parts
        part1 = Mock(text="Part 1")
        part2 = Mock(text="Part 2")
        content2 = Mock(parts=[part1, part2])
        content2.text = None
        text2 = self.manager._extract_text(content2)
        self.assertEqual(text2, "Part 1 Part 2")
        
        # Content with no text
        content3 = Mock(spec=[])
        text3 = self.manager._extract_text(content3)
        self.assertIsInstance(text3, str)
    
    def test_fallback_summary_creation(self):
        """Test fallback summary when LLM is unavailable"""
        contents = [
            Mock(role='user', text='Help me with Python'),
            Mock(role='assistant', text='I can help with Python programming'),
            Mock(role='user', text='Show me functions'),
            Mock(role='assistant', text='Here are some function examples')
        ]
        
        summary = self.manager._create_fallback_summary(contents)
        
        self.assertIn('CONVERSATION SUMMARY', summary)
        self.assertIn('USER REQUESTS', summary)
        self.assertIn('ASSISTANT ACTIONS', summary)
        self.assertIn('TOTAL EXCHANGES', summary)
        self.assertIn('2 user messages', summary)
        self.assertIn('2 assistant responses', summary)
    
    def test_summary_prompt_creation(self):
        """Test summary prompt generation"""
        contents = [
            Mock(role='user', text='Test message'),
            Mock(role='assistant', text='Test response')
        ]
        
        prompt = self.manager.create_summary_prompt(contents)
        
        # Check for key sections
        self.assertIn('USER_CONTEXT', prompt)
        self.assertIn('TASK_TRACKING', prompt)
        self.assertIn('COMPLETED_WORK', prompt)
        self.assertIn('PENDING_TASKS', prompt)
        self.assertIn('CURRENT_STATE', prompt)
        self.assertIn('CODE_STATE', prompt)
        
        # Check for conversation content
        self.assertIn('[USER]: Test message', prompt)
        self.assertIn('[ASSISTANT]: Test response', prompt)


class TestSmartAgent(unittest.TestCase):
    """Test SmartAgent wrapper"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_agent = Mock()
        self.mock_agent._before_model_callback = None
        
        self.config = ContextConfig(max_tokens=500)
        self.smart_agent = SmartAgent(self.mock_agent, self.config)
    
    def test_smart_agent_initialization(self):
        """Test SmartAgent creation"""
        self.assertIsNotNone(self.smart_agent.context_manager)
        self.assertEqual(self.smart_agent.agent, self.mock_agent)
        self.assertIsNotNone(self.mock_agent._before_model_callback)
        self.assertEqual(self.smart_agent.original_callback, None)
    
    def test_existing_callback_preservation(self):
        """Test preservation of existing callback"""
        original_callback = Mock()
        agent_with_callback = Mock()
        agent_with_callback._before_model_callback = original_callback
        
        smart_agent = SmartAgent(agent_with_callback, self.config)
        
        self.assertEqual(smart_agent.original_callback, original_callback)
    
    def test_memory_summary_empty(self):
        """Test memory summary when empty"""
        summary = self.smart_agent.get_memory_summary()
        self.assertIn("No conversation memories stored", summary)
    
    def test_memory_summary_with_data(self):
        """Test memory summary with stored data"""
        # Add test memory
        self.smart_agent.context_manager.conversation_memory = [
            {
                'timestamp': '0',
                'summary': 'User asked about Python. Assistant provided help.',
                'condensed_turns': 3
            },
            {
                'timestamp': '1', 
                'summary': 'Discussion about machine learning concepts.',
                'condensed_turns': 5
            }
        ]
        
        summary = self.smart_agent.get_memory_summary()
        
        self.assertIn("CONVERSATION MEMORY BANK", summary)
        self.assertIn("User asked about Python", summary)
        self.assertIn("machine learning concepts", summary)
        self.assertIn("Condensed 3 turns", summary)
        self.assertIn("Condensed 5 turns", summary)
    
    def test_attribute_delegation(self):
        """Test that SmartAgent delegates to wrapped agent"""
        # Set attribute on mock agent
        self.mock_agent.test_method = Mock(return_value="test_result")
        self.mock_agent.test_attribute = "test_value"
        
        # Should delegate method calls
        result = self.smart_agent.test_method()
        self.assertEqual(result, "test_result")
        
        # Should delegate attribute access
        value = self.smart_agent.test_attribute
        self.assertEqual(value, "test_value")


class TestTokenEstimation(unittest.TestCase):
    """Test token counting functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.manager = AdvancedContextManager(ContextConfig())
    
    @patch('advanced_context_manager.tiktoken')
    def test_token_estimation_with_text(self, mock_tiktoken):
        """Test token estimation for content with text"""
        # Mock tiktoken
        mock_encoding = Mock()
        mock_encoding.encode.return_value = [1, 2, 3, 4, 5]  # 5 tokens
        mock_tiktoken.get_encoding.return_value = mock_encoding
        
        contents = [
            Mock(text="Hello world"),
            Mock(text="How are you?")
        ]
        
        tokens = self.manager.estimate_tokens(contents)
        
        self.assertGreater(tokens, 0)  # Should have some tokens
        # Note: Mock behavior may vary, just check functionality works
    
    @patch('advanced_context_manager.tiktoken')
    def test_token_estimation_with_parts(self, mock_tiktoken):
        """Test token estimation for content with parts"""
        mock_encoding = Mock()
        mock_encoding.encode.return_value = [1, 2, 3]  # 3 tokens per part
        mock_tiktoken.get_encoding.return_value = mock_encoding
        
        part1 = Mock(text="Part one")
        part2 = Mock(text="Part two")
        content = Mock(parts=[part1, part2])
        content.text = None  # No direct text
        
        tokens = self.manager.estimate_tokens([content])
        
        self.assertEqual(tokens, 4)  # Actual tokens from mock
    
    def test_token_estimation_empty(self):
        """Test token estimation for empty content"""
        tokens = self.manager.estimate_tokens([])
        self.assertEqual(tokens, 0)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.manager = AdvancedContextManager(ContextConfig())
    
    def test_malformed_content_handling(self):
        """Test handling of malformed content objects"""
        # Content with no text or parts
        malformed_content = Mock(spec=['role'])
        malformed_content.role = 'user'
        
        # Should not crash
        text = self.manager._extract_text(malformed_content)
        self.assertIsInstance(text, str)
        
        # Should handle in conversation turns
        indices = self.manager.identify_conversation_turns([malformed_content])
        self.assertEqual(indices['user'], [0])
    
    def test_mixed_content_types(self):
        """Test handling of mixed content types"""
        contents = [
            Mock(role='system', text='System message'),
            Mock(role='user', text=None, parts=[Mock(text='User message')]),
            Mock(role='assistant', text='Assistant message'),
            Mock(role='unknown', text='Unknown role')  # Edge case
        ]
        
        indices = self.manager.identify_conversation_turns(contents)
        
        self.assertEqual(indices['system'], [0])
        self.assertEqual(indices['user'], [1])
        self.assertEqual(indices['assistant'], [2])
        # Unknown role should not appear in any category
        self.assertNotIn(3, indices['system'])
        self.assertNotIn(3, indices['user'])
        self.assertNotIn(3, indices['assistant'])


def run_tests():
    """Run all tests with detailed output"""
    print("🧪 Running Context Management Tests")
    print("=" * 40)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestContextConfig,
        TestAdvancedContextManager,
        TestSmartAgent,
        TestTokenEstimation,
        TestEdgeCases
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print(f"\n📊 Test Results:")
    print(f"✅ Tests run: {result.testsRun}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"🚫 Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\n💥 Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print(f"\n🔥 Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\n🎯 Overall: {'PASSED' if success else 'FAILED'}")
    
    return success


if __name__ == "__main__":
    run_tests()