import os
import asyncio
import httpx
import json
from typing import Optional, List, Union, Dict, Any
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field, field_validator, HttpUrl, AnyHttpUrl
from pydantic_ai import Agent, RunContext
import openai
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.status import Status
from rich.prompt import Prompt, Confirm

# API keys
openai.api_key = os.getenv("OPENAI_API_KEY")
SPIDER_API_KEY = os.getenv("SPIDER_API_KEY")

# Spider API configuration
SPIDER_API_URL = "https://api.spider.cloud/v1/extract"


class SourceInfo(BaseModel):
    """Source article information"""
    title: str = Field(description="The title of the source article")
    publication: str = Field(description="The publication name")
    url: str = Field(description="The URL of the source article")
    date: str = Field(description="The publication date")
    author: Optional[str] = Field(None, description="The author name if available")

    def to_markdown(self) -> str:
        """Convert source info to markdown format"""
        return "\n".join([
            "## Source Information",
            f"- **Article**: {self.title}",
            f"- **Publication**: {self.publication}",
            f"- **URL**: {self.url}",
            f"- **Date**: {self.date}",
            f"- **Author**: {self.author if self.author else 'Not specified'}"
        ])


class EssayContent(BaseModel):
    """Essay content structure"""
    title: str = Field(description="The title of the essay")
    content: str = Field(description="The main content of the essay")
    summary: str = Field(description="A brief summary of the essay")

    def to_markdown(self) -> str:
        """Convert essay content to markdown format"""
        return "\n\n".join([
            f"# {self.title}",
            self.content,
            "## Summary",
            self.summary
        ])


class EssayResult(BaseModel):
    """Complete essay result including source and content"""
    title: str = Field(description="The title of the essay")
    content: str = Field(description="The main content of the essay")
    summary: str = Field(description="A brief summary of the essay")
    source: SourceInfo = Field(description="Source article information")

    def to_markdown(self) -> str:
        """Convert complete essay to markdown format"""
        return "\n\n".join([
            f"# {self.title}",
            self.source.to_markdown(),
            "\n## Content",
            self.content,
            "## Summary",
            self.summary
        ])


class EssayDependencies(BaseModel):
    """Dependencies for essay generation"""
    source_content: str = Field(description="The source content to generate essay from")
    source_url: str = Field(description="The URL of the source content")
    desired_length: str = Field(default="medium", description="Desired essay length (short/medium/long)")
    todays_date: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d"),
        description="Current date in YYYY-MM-DD format"
    )


class EssayAgent:
    """Agent for generating essays from source content"""
    def __init__(self):
        self.agent = Agent[str, EssayResult](
            model="openai:gpt-4o-mini",
            system_prompt=self._load_system_prompt()
        )

    def _load_system_prompt(self) -> str:
        """Load the system prompt from guidelines.md"""
        try:
            with open("prompt/guidelines.md", "r", encoding="utf-8") as f:
                guidelines = f.read().strip()
                schema = EssayResult.model_json_schema()
                return f"""{guidelines}

You will receive source content to analyze and write about. Your response must be a valid JSON object matching this schema:

{json.dumps(schema, indent=2)}

Follow these rules:
1. Extract the original article title and publication name from the content
2. Use the provided URL and date
3. Look for author information in the content
4. Write a well-structured essay with title, content, and summary
5. Format dates as YYYY-MM-DD
6. Keep URLs exactly as provided
7. Use "Not specified" for missing author names"""
        except FileNotFoundError:
            print("Warning: guidelines.md not found, using default prompt")
            return """You are an expert essay writer. You craft well-structured essays with clear titles, 
                     detailed content, and concise summaries. Your writing is engaging and professional."""

    def _format_input(self, deps: EssayDependencies) -> str:
        """Format the input for the OpenAI API"""
        return f"""Source URL: {deps.source_url}
Today's Date: {deps.todays_date}
Desired Length: {deps.desired_length}

Content:
{deps.source_content}"""

    async def generate(self, source_content: str, source_url: str, desired_length: str = "medium") -> EssayResult:
        """Generate an essay from source content"""
        deps = EssayDependencies(
            source_content=source_content,
            source_url=source_url,
            desired_length=desired_length
        )
        
        formatted_input = self._format_input(deps)
        result = await self.agent.run(formatted_input)
        return result


class SpiderResponse(BaseModel):
    """Response from Spider API"""
    title: str = Field(description="The title of the webpage")
    text: str = Field(description="The main content of the webpage")
    description: Optional[str] = Field(None, description="Meta description of the webpage")


def validate_url(url: str) -> bool:
    """Validate if the URL is properly formatted."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


async def extract_content_with_httpx(url: str) -> SpiderResponse:
    """Fallback method to extract content using httpx and BeautifulSoup."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Get title
        title = soup.title.string if soup.title else ""
        
        # Get meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        description = meta_desc["content"] if meta_desc else None
        
        # Get main content
        # First try article tag
        content = soup.find("article")
        if not content:
            # Then try main tag
            content = soup.find("main")
        if not content:
            # Fallback to body
            content = soup.body
            
        # Get text and clean it
        text = content.get_text(separator="\n", strip=True) if content else ""
        # Remove excessive newlines
        text = "\n".join(line.strip() for line in text.split("\n") if line.strip())
        
        return SpiderResponse(
            title=title,
            text=text,
            description=description
        )


async def extract_url_content(url: str) -> SpiderResponse:
    """Extract content from a URL using Spider API with fallback to direct extraction."""
    if not validate_url(url):
        raise ValueError("Invalid URL format. Please provide a valid URL (e.g., https://example.com)")

    # Try Spider API first
    if SPIDER_API_KEY:
        try:
            headers = {
                "Authorization": f"Bearer {SPIDER_API_KEY}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    SPIDER_API_URL,
                    headers=headers,
                    json={"url": url}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return SpiderResponse(
                        title=data.get("title", ""),
                        text=data.get("text", ""),
                        description=data.get("description")
                    )
        except Exception as e:
            print(f"Spider API failed, falling back to direct extraction: {str(e)}")
    
    # Fallback to direct extraction
    return await extract_content_with_httpx(url)


async def main():
    # Create rich console for better output
    console = Console()
    console.print(Panel.fit("[bold green]Essay Generator[/bold green]", border_style="green"))
    
    try:
        # Get input type from user
        input_type = Prompt.ask(
            "\n[bold yellow]Choose input type[/bold yellow]",
            choices=["url", "files"],
            default="files"
        )

        # Initialize progress bar
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console,
            transient=False
        )

        # Create essay agent
        essay_agent = EssayAgent()

        # Handle URL input
        if input_type == "url":
            if not SPIDER_API_KEY:
                console.print("\n[bold red]❌ SPIDER_API_KEY environment variable not set. Please set it and try again.[/bold red]")
                return
            
            # Get URL from user
            url = Prompt.ask("\n[bold yellow]Enter URL[/bold yellow] (e.g., https://example.com)")
            if not validate_url(url):
                console.print("\n[bold red]❌ Invalid URL format. Please enter a valid URL (e.g., https://example.com)[/bold red]")
                return

            with progress:
                task_id = progress.add_task("[cyan]Extracting content from URL...", total=None)
                try:
                    spider_content = await extract_url_content(url)
                    if not spider_content.text.strip():
                        console.print("\n[bold red]❌ No content could be extracted from the URL. Please try a different URL.[/bold red]")
                        return
                    
                    # Generate essay
                    progress.update(task_id, description="[bold cyan]Generating essay...")
                    run_result = await essay_agent.generate(
                        source_content=spider_content.text,
                        source_url=url,
                        desired_length="medium"
                    )
                    
                    # Parse the result into our model
                    result_data = json.loads(run_result.data)
                    result = EssayResult(**result_data)
                    
                    # Print results
                    progress.stop()
                    console.print("\n[bold green]✨ Essay Generated Successfully! ✨[/bold green]")
                    
                    with Status("[bold blue]Formatting output...", console=console):
                        console.print("\n[bold blue]Title:[/bold blue]")
                        console.print(Panel.fit(result.title, border_style="blue"))
                        
                        console.print("\n[bold green]Content:[/bold green]")
                        console.print(result.content)
                        
                        console.print("\n[bold cyan]Summary:[/bold cyan]")
                        console.print(Panel.fit(result.summary, border_style="cyan"))
                    
                    # Save the essay
                    with Status("[bold yellow]Saving essay...", console=console):
                        output_dir = Path("output")
                        output_dir.mkdir(exist_ok=True)
                        
                        # Create filename from date and domain
                        domain = urlparse(url).netloc
                        filename = f"essay_{datetime.now().strftime('%Y-%m-%d')}_{domain}"
                        output_path = output_dir / f"{filename}.md"
                        
                        # Save markdown output
                        markdown = result.to_markdown()
                        output_path.write_text(markdown)
                        console.print(f"\n[bold green]✅ Essay saved to: {output_path}[/bold green]")
                
                except Exception as e:
                    console.print(f"\n[bold red]❌ Error: {str(e)}[/bold red]")
                    return
        
        # Handle file input
        else:
            with progress:
                task_id = progress.add_task("Checking directories...", total=None)
                # ... rest of the file input handling code ...

    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {str(e)}[/bold red]")


if __name__ == "__main__":
    asyncio.run(main())