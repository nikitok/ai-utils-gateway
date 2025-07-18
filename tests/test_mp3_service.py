import pytest
from pathlib import Path
from unittest.mock import Mock
import whisper

from aiutils.schemas.mp3_input import Mp3Input
from aiutils.services.mp3_service import Mp3Service, Mp3DownloadError, Mp3TranscribeResult


# Get the path to test data
TEST_DATA_DIR = Path(__file__).parent / "data"
TEST_MP3_PATH = TEST_DATA_DIR / "test_sounds.mp3"


@pytest.fixture
def mock_whisper_model():
    """Create a mock Whisper model for fast tests."""
    model = Mock()
    model.transcribe.return_value = {
        "text": "This is a test transcription",
        "language": "en"
    }
    return model


@pytest.fixture(scope="session")
def real_whisper_model():
    """Load real Whisper model for integration tests."""
    return whisper.load_model("tiny")  # Use tiny model for faster tests


@pytest.fixture
def mp3_service(mock_whisper_model):
    """Create MP3 service with mock model."""
    return Mp3Service(mock_whisper_model)


@pytest.fixture
def mp3_service_real(real_whisper_model):
    """Create MP3 service with real Whisper model."""
    return Mp3Service(real_whisper_model)


class TestTranscribe:
    """Test transcribe method."""
    
    @pytest.mark.asyncio
    async def test_valid_file_transcription_mock(self, mp3_service):
        """Test that transcribe correctly processes test_sounds.mp3 file with mock."""
        mp3_input = Mp3Input(
            url=f"file://{TEST_MP3_PATH}",
            language="auto"
        )
        
        result = await mp3_service.transcribe(mp3_input)
        
        # Check that method returns Mp3TranscribeResult
        assert isinstance(result, Mp3TranscribeResult)
        assert result.text == "This is a test transcription"
        assert result.language == "en"
        
        # Verify Whisper was called
        mp3_service.whisper_model.transcribe.assert_called_once()
    
    @pytest.mark.asyncio
    # @pytest.mark.slow  # Mark as slow test
    async def test_valid_file_transcription_real(self, mp3_service_real):
        """Test that transcribe correctly processes test_sounds.mp3 file with real Whisper model."""
        mp3_input = Mp3Input(
            url=f"file://{TEST_MP3_PATH}",
            language="auto"
        )
        
        result = await mp3_service_real.transcribe(mp3_input)
        
        # Check that method returns Mp3TranscribeResult
        assert isinstance(result, Mp3TranscribeResult)
        # With real model, we don't know exact text, but it should not be empty
        assert result.text.strip() != ""
        assert len(result.text) > 0
        # Language should be detected
        assert result.language in ["en", "es", "fr", "de", "ru", "zh", "ja", "ko", "ar", "hi", "pt"]
    
    @pytest.mark.asyncio
    async def test_invalid_url_raises_error(self, mp3_service):
        """Test that invalid URL raises Mp3DownloadError."""
        # Test with complete nonsense URL
        mp3_input = Mp3Input(
            url="file:///this/is/complete/nonsense/path/that/does/not/exist.mp3",
            language="auto"
        )
        
        with pytest.raises(Mp3DownloadError) as exc_info:
            await mp3_service.transcribe(mp3_input)
        
        # Check error message contains relevant info
        error_message = str(exc_info.value)
        assert "File not found" in error_message or "Failed to download" in error_message