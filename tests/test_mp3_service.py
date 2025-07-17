import pytest
from pathlib import Path
from unittest.mock import Mock

from aiutils.schemas.mp3_input import Mp3Input
from aiutils.services.mp3_service import Mp3Service, Mp3DownloadError, TranscribeResult


# Get the path to test data
TEST_DATA_DIR = Path(__file__).parent / "data"
TEST_MP3_PATH = TEST_DATA_DIR / "test_sounds.mp3"


@pytest.fixture
def mock_whisper_model():
    """Create a mock Whisper model."""
    model = Mock()
    model.transcribe.return_value = {
        "text": "This is a test transcription",
        "language": "en"
    }
    return model


@pytest.fixture
def mp3_service(mock_whisper_model):
    """Create MP3 service with mock model."""
    return Mp3Service(mock_whisper_model)


class TestMp3ToText:
    """Test mp3ToText method."""
    
    @pytest.mark.asyncio
    async def test_valid_file_transcription(self, mp3_service):
        """Test that mp3ToText correctly processes test_sounds.mp3 file."""
        mp3_input = Mp3Input(
            url=f"file://{TEST_MP3_PATH}",
            language="auto"
        )
        
        result = await mp3_service.mp3ToText(mp3_input)
        
        # Check that method returns TranscribeResult
        assert isinstance(result, TranscribeResult)
        assert result.text == "This is a test transcription"
        assert result.language == "en"
        
        # Verify Whisper was called
        assert mp3_service.whisper_model.transcribe.called
    
    @pytest.mark.asyncio
    async def test_invalid_url_raises_error(self, mp3_service):
        """Test that invalid URL raises Mp3DownloadError."""
        # Test with complete nonsense URL
        mp3_input = Mp3Input(
            url="file:///this/is/complete/nonsense/path/that/does/not/exist.mp3",
            language="auto"
        )
        
        with pytest.raises(Mp3DownloadError) as exc_info:
            await mp3_service.mp3ToText(mp3_input)
        
        # Check error message contains relevant info
        error_message = str(exc_info.value)
        assert "File not found" in error_message or "Failed to download" in error_message