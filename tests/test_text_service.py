import pytest
import torch
from unittest.mock import Mock, MagicMock
from transformers import AutoTokenizer, AutoModel

from aiutils.schemas.text_input import TextInput
from aiutils.services.text_service import TextService, TextEmbeddingResult, TextTokenizationResult
from aiutils.core.exceptions import ModelNotLoadedError, ProcessingError


@pytest.fixture
def mock_tokenizer():
    """Create a mock tokenizer for fast tests."""
    tokenizer = Mock()
    tokenizer.return_value = {
        "input_ids": torch.tensor([[101, 7592, 2088, 102]]),
        "attention_mask": torch.tensor([[1, 1, 1, 1]])
    }
    tokenizer.convert_ids_to_tokens.return_value = ["[CLS]", "hello", "world", "[SEP]"]
    return tokenizer


@pytest.fixture
def mock_model():
    """Create a mock model for fast tests."""
    model = Mock()
    # Mock the model output
    mock_output = Mock()
    mock_output.last_hidden_state = torch.randn(1, 4, 384)  # batch_size=1, seq_len=4, hidden_size=384
    model.return_value = mock_output
    return model


@pytest.fixture(scope="session")
def real_tokenizer():
    """Load real tokenizer for integration tests."""
    return AutoTokenizer.from_pretrained("thenlper/gte-small")


@pytest.fixture(scope="session")
def real_model():
    """Load real model for integration tests."""
    return AutoModel.from_pretrained("thenlper/gte-small")


@pytest.fixture
def text_service(mock_tokenizer, mock_model):
    """Create TextService with mock dependencies."""
    return TextService(
        tokenizer=mock_tokenizer,
        model=mock_model,
        model_name="mock-model"
    )


@pytest.fixture
def text_service_real(real_tokenizer, real_model):
    """Create TextService with real model."""
    return TextService(
        tokenizer=real_tokenizer,
        model=real_model,
        model_name="thenlper/gte-small"
    )


class TestProcessToTensor:
    """Test process_to_tensor method."""
    
    def test_valid_text_to_tensor_mock(self, text_service):
        """Test tensor generation with mock model."""
        text_input = TextInput(
            text="Hello, world!",
            max_length=128
        )
        
        result = text_service.process_to_tensor(text_input)
        
        # Check that result is a TextEmbeddingResult dataclass
        assert isinstance(result, TextEmbeddingResult)
        assert result.model_name == "mock-model"
        assert result.max_length == 128
        assert isinstance(result.embedding, list)
        assert result.embedding_dimension == len(result.embedding)
        
        # Verify tokenizer was called correctly
        text_service.tokenizer.assert_called_once_with(
            "Hello, world!",
            return_tensors="pt",
            truncation=True,
            padding="max_length",
            max_length=128
        )
        
        # Verify model was called
        text_service.model.assert_called_once()
    
    def test_valid_text_to_tensor_real(self, text_service_real):
        """Test tensor generation with real gte-tiny model."""
        text_input = TextInput(
            text="This is a test sentence for embedding generation.",
            max_length=256
        )
        
        result = text_service_real.process_to_tensor(text_input)
        
        # Check that result is a TextEmbeddingResult dataclass
        assert isinstance(result, TextEmbeddingResult)
        assert result.model_name == "thenlper/gte-small"
        assert result.max_length == 256
        assert isinstance(result.embedding, list)
        assert result.embedding_dimension == 384  # gte-tiny has 384 dimensions
        assert len(result.embedding) == 384
        
        # Check that embedding values are reasonable floats
        for value in result.embedding[:10]:  # Check first 10 values
            assert isinstance(value, float)
            assert -10 < value < 10  # Embeddings should be in reasonable range
    
    def test_long_text_truncation_real(self, text_service_real):
        """Test that long text is properly truncated."""
        # Create a very long text
        long_text = " ".join(["This is a test sentence."] * 100)
        
        text_input = TextInput(
            text=long_text,
            max_length=128
        )
        
        result = text_service_real.process_to_tensor(text_input)
        
        # Should still produce valid embeddings
        assert isinstance(result, TextEmbeddingResult)
        assert isinstance(result.embedding, list)
        assert result.embedding_dimension == 384
        assert result.max_length == 128
    
    def test_model_not_loaded_error(self):
        """Test error when model is not loaded."""
        service = TextService()  # No model provided
        
        text_input = TextInput(text="Test text")
        
        with pytest.raises(ModelNotLoadedError) as exc_info:
            service.process_to_tensor(text_input)
        
        assert "multilingual-e5-small" in str(exc_info.value)


class TestProcessToTokens:
    """Test process_to_tokens method."""
    
    def test_valid_text_to_tokens_mock(self, text_service):
        """Test tokenization with mock tokenizer."""
        text_input = TextInput(
            text="Hello, world!",
            max_length=128
        )
        
        # Configure mock for this specific test
        text_service.tokenizer.return_value = {
            "input_ids": [101, 7592, 2088, 102]
        }
        
        result = text_service.process_to_tokens(text_input)
        
        # Check that result is a TextTokenizationResult dataclass
        assert isinstance(result, TextTokenizationResult)
        assert result.model_name == "mock-model"
        assert result.text == "Hello, world!"
        assert result.max_length == 128
        assert result.tokens == ["[CLS]", "hello", "world", "[SEP]"]
        assert result.input_ids == [101, 7592, 2088, 102]
    
    def test_valid_text_to_tokens_real(self, text_service_real):
        """Test tokenization with real gte-tiny tokenizer."""
        text_input = TextInput(
            text="Machine learning is fascinating!",
            max_length=128
        )
        
        result = text_service_real.process_to_tokens(text_input)
        
        # Check that result is a TextTokenizationResult dataclass
        assert isinstance(result, TextTokenizationResult)
        assert result.model_name == "thenlper/gte-small"
        assert result.text == "Machine learning is fascinating!"
        assert result.max_length == 128
        assert isinstance(result.tokens, list)
        assert isinstance(result.input_ids, list)
        
        # Check tokens contain expected special tokens
        assert result.tokens[0] == "[CLS]"
        assert result.tokens[-1] == "[SEP]"
        
        # Check token count matches input_ids count
        assert len(result.tokens) == len(result.input_ids)
        
        # Verify some expected tokens are present
        tokens_lower = [t.lower() for t in result.tokens]
        assert any("machine" in t for t in tokens_lower)
        assert any("learning" in t for t in tokens_lower)
    
    def test_empty_text_validation(self, text_service_real):
        """Test that empty text is rejected by Pydantic validation."""
        with pytest.raises(ValueError):
            TextInput(text="", max_length=128)
    
    def test_whitespace_only_validation(self, text_service_real):
        """Test that whitespace-only text is rejected."""
        with pytest.raises(ValueError):
            TextInput(text="   \n\t  ", max_length=128)
    
    def test_tokenizer_not_loaded_error(self):
        """Test error when tokenizer is not loaded."""
        service = TextService(model=Mock())  # Model but no tokenizer
        
        text_input = TextInput(text="Test text")
        
        with pytest.raises(ModelNotLoadedError) as exc_info:
            service.process_to_tokens(text_input)
        
        assert "tokenizer" in str(exc_info.value)


class TestTextServiceMethods:
    """Test TextService helper methods."""
    
    def test_set_models(self, mock_tokenizer, mock_model):
        """Test setting models after initialization."""
        service = TextService()
        
        # Initially no models
        assert service.tokenizer is None
        assert service.model is None
        
        # Set models
        service.set_models(mock_tokenizer, mock_model, "new-model")
        
        # Check models are set
        assert service.tokenizer == mock_tokenizer
        assert service.model == mock_model
        assert service.model_name == "new-model"
    
    def test_different_text_lengths_real(self, text_service_real):
        """Test processing texts of different lengths."""
        test_cases = [
            ("Short", 64),
            ("This is a medium length sentence that should test the tokenizer.", 128),
            ("This is a much longer text. " * 20, 512),
        ]
        
        for text, max_length in test_cases:
            text_input = TextInput(text=text, max_length=max_length)
            
            # Test tensor generation
            tensor_result = text_service_real.process_to_tensor(text_input)
            assert isinstance(tensor_result, TextEmbeddingResult)
            assert tensor_result.embedding_dimension == 384
            assert tensor_result.max_length == max_length
            
            # Test tokenization
            tokens_result = text_service_real.process_to_tokens(text_input)
            assert isinstance(tokens_result, TextTokenizationResult)
            assert len(tokens_result.tokens) <= max_length
            assert tokens_result.max_length == max_length


class TestErrorHandling:
    """Test error handling in TextService."""
    
    def test_processing_error_in_tensor_generation(self, mock_tokenizer, mock_model):
        """Test ProcessingError when tensor generation fails."""
        # Make model raise an exception
        mock_model.side_effect = RuntimeError("Model error")
        
        service = TextService(tokenizer=mock_tokenizer, model=mock_model)
        text_input = TextInput(text="Test text")
        
        with pytest.raises(ProcessingError) as exc_info:
            service.process_to_tensor(text_input)
        
        assert "Failed to generate embeddings" in str(exc_info.value)
        assert "Model error" in str(exc_info.value)
    
    def test_processing_error_in_tokenization(self, mock_tokenizer, mock_model):
        """Test ProcessingError when tokenization fails."""
        # Make tokenizer raise an exception
        mock_tokenizer.side_effect = RuntimeError("Tokenizer error")
        
        service = TextService(tokenizer=mock_tokenizer, model=mock_model)
        text_input = TextInput(text="Test text")
        
        with pytest.raises(ProcessingError) as exc_info:
            service.process_to_tokens(text_input)
        
        assert "Failed to tokenize text" in str(exc_info.value)
        assert "Tokenizer error" in str(exc_info.value)


@pytest.mark.parametrize("text,expected_min_tokens", [
    ("Hello", 3),  # [CLS] hello [SEP]
    ("The quick brown fox jumps over the lazy dog.", 10),
    ("人工智能", 3),  # Test with Chinese characters
    ("🚀 Rocket emoji!", 5),  # Test with emoji
])
def test_various_text_inputs_real(text_service_real, text, expected_min_tokens):
    """Test service with various text inputs."""
    text_input = TextInput(text=text, max_length=128)
    
    # Test tokenization
    tokens_result = text_service_real.process_to_tokens(text_input)
    assert isinstance(tokens_result, TextTokenizationResult)
    assert len(tokens_result.tokens) >= expected_min_tokens
    
    # Test tensor generation
    tensor_result = text_service_real.process_to_tensor(text_input)
    assert isinstance(tensor_result, TextEmbeddingResult)
    assert tensor_result.embedding_dimension == 384
    assert all(isinstance(v, float) for v in tensor_result.embedding)


def test_dataclass_attributes():
    """Test that dataclasses have correct attributes."""
    # Test TextEmbeddingResult
    embedding_result = TextEmbeddingResult(
        model_name="test",
        max_length=128,
        embedding=[0.1, 0.2, 0.3],
        embedding_dimension=3
    )
    assert embedding_result.model_name == "test"
    assert embedding_result.max_length == 128
    assert embedding_result.embedding == [0.1, 0.2, 0.3]
    assert embedding_result.embedding_dimension == 3
    
    # Test TextTokenizationResult
    token_result = TextTokenizationResult(
        model_name="test",
        text="Hello",
        max_length=128,
        tokens=["hello"],
        input_ids=[1]
    )
    assert token_result.model_name == "test"
    assert token_result.text == "Hello"
    assert token_result.max_length == 128
    assert token_result.tokens == ["hello"]
    assert token_result.input_ids == [1]