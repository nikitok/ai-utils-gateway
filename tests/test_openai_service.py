
import pytest
import os
from dotenv import load_dotenv
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text

from aiutils.core.logger import get_logger, console
from aiutils.schemas.openai_input import OpenAiCompletion
from aiutils.services.openai_service import open_ai_completion

# Load environment variables
load_dotenv()

# Get logger for this module
logger = get_logger(__name__)


@pytest.fixture
def api_key():
    """Fixture to get API key and skip test if not available"""
    key = os.getenv("OPENAI_API_KEY")
    if not key or key == "sk-your-api-key-here":
        logger.warning("⚠️  OPENAI_API_KEY not set in .env file - skipping test")
        pytest.skip("OPENAI_API_KEY not set in .env file")
    return key


def test_openai_completion(api_key):
    """Test OpenAI completion with 'ping?' question using API key from .env"""
    console.print(Panel.fit(
        "[bold cyan]Testing OpenAI Completion[/bold cyan]",
        border_style="blue"
    ))
    
    logger.info("✅ API key loaded from .env")
    
    # Create input for OpenAI completion
    input_data = OpenAiCompletion(
        key=api_key,
        text="ping?"
    )
    
    logger.info(f"📤 Sending request: '{input_data.text}'")
    
    # Call the OpenAI completion function with progress indicator
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("Calling OpenAI API...", total=None)
        result = open_ai_completion(input_data)
        progress.update(task, completed=True)
    
    # Verify the response
    assert "text" in result
    assert isinstance(result["text"], str)
    assert len(result["text"]) > 0
    
    # Check that there's no error in the response
    if "status_code" in result:
        if result.get("status_code") != 200:
            logger.error(f"❌ API returned error: {result.get('status_code')}")
        assert result.get("status_code") == 200
    
    # Display the response in a nice panel
    response_text = Text(result['text'], style="green")
    console.print(Panel(
        response_text,
        title="[bold green]OpenAI Response[/bold green]",
        border_style="green",
        padding=(1, 2)
    ))
    
    logger.info("✅ Test completed successfully!")


def test_openai_completion_with_custom_prompt(api_key):
    """Test OpenAI completion with custom prompt"""
    console.print(Panel.fit(
        "[bold cyan]Testing OpenAI with Custom Prompt[/bold cyan]",
        border_style="blue"
    ))
    
    # Create input for OpenAI completion
    input_data = OpenAiCompletion(
        key=api_key,
        text="What is 2+2? Reply with just the number."
    )
    
    logger.info(f"📤 Sending request: '{input_data.text}'")
    
    # Call the OpenAI completion function
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("Calling OpenAI API...", total=None)
        result = open_ai_completion(input_data)
        progress.update(task, completed=True)
    
    # Verify the response
    assert "text" in result
    assert isinstance(result["text"], str)
    assert len(result["text"]) > 0
    
    # Display the response
    response_text = Text(result['text'], style="yellow")
    console.print(Panel(
        response_text,
        title="[bold yellow]Math Response[/bold yellow]",
        border_style="yellow",
        padding=(1, 2)
    ))
    
    logger.info("✅ Custom prompt test completed!")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])