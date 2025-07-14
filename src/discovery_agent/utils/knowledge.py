import os
import tempfile
from pathlib import Path

import boto3


def get_knowledge_root_local_path() -> Path:
    return Path(__file__).parent.parent.parent.parent.parent / "knowledge"


def get_knowledge_file_path_str(file_location: Path) -> str:
    if bucket_name := os.environ.get("KNOWLEDGE_S3_BUCKET_NAME"):
        s3_client = boto3.client("s3")

        temp_dir = tempfile.mkdtemp()
        temp_file_path = Path(temp_dir) / file_location.name
        s3_client.download_file(bucket_name, file_location.as_posix(), str(temp_file_path))

        return str(temp_file_path)

    return str(get_knowledge_root_local_path() / file_location)
