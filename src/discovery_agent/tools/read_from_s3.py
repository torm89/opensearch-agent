from pathlib import Path
from typing import Optional

from langchain_core.callbacks import (
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from langchain_core.tools.base import ArgsSchema
from pydantic import BaseModel, Field

from discovery_agent.utils.knowledge import get_knowledge_file_path_str

class ReadFromS3Input(BaseModel):
    file_location: str = Field(description="Location of other documentation file mentioned in current document")
    relative_to: str = Field(description="Location of the current document")


class ReadDocumentFromS3Tool(BaseTool):
    name: str = "DocumentationFileReader"
    description: str = "Reads whole documentation, schema or example file and returns its content"
    args_schema: Optional[ArgsSchema] = ReadFromS3Input
    return_direct: bool = True

    def _run(
            self, file_location: str, relative_to: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        print(f"ReadDocumentFromS3Tool._run({file_location}, {relative_to})")
        filepath = Path(file_location).relative_to(relative_to)
        print(f"filepath: {str(filepath)}")
        filepath_str = get_knowledge_file_path_str(filepath)
        print(f"filepath_str: {filepath_str}")

        with open(filepath_str, "r") as file:
            content = file.read()

        return f"""
        <documentation_context>
        <filepath>{filepath}</filepath>
        <content>{content}</content>
        </documentation_context>
        """
