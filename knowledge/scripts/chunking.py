import json
from pathlib import Path

import tqdm
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain_text_splitters import RecursiveJsonSplitter, TokenTextSplitter


def chunking():
    headers_to_split_on = [("#" * i, f"Markdown Header {i}") for i in range(1, 6)]
    # splitter = MarkdownHeaderTextSplitter(headers_to_split_on)

    splitter = MarkdownHeaderTextSplitter(headers_to_split_on)

    path = r""
    with open(path, "r") as file:
        markdown_text = file.read()

    chunks = splitter.split_text(markdown_text)  # Zachowuje hierarchię nagłówków w metadanych

    for i, chunk in enumerate(chunks):
        print(i, chunk.metadata)

    print(chunks[1])


def chunking_md():
    headers_to_split_on = [("#" * i, f"Markdown Header {i}") for i in range(1, 6)]
    splitter_md = MarkdownHeaderTextSplitter(headers_to_split_on)
    splitter_token = TokenTextSplitter(chunk_size=2000, chunk_overlap=200)

    root_path = Path(__file__).parent.parent.parent
    data_path = root_path / "data" / "opensearch"
    markdown_files = list(data_path.glob("**/*.md"))

    chunks = []
    for markdown_file in tqdm.tqdm(markdown_files):
        text = markdown_file.read_text(encoding="utf-8")
        prechunks = splitter_md.split_text(text)
        for chunk in splitter_token.transform_documents(prechunks):
            chunk.metadata.update({
                "filepath": str(markdown_file.relative_to(root_path)),
                "filepath_parts": markdown_file.relative_to(root_path).parts
            })
            chunks.append(chunk)

    opensearch_docs_chunks_path = root_path / "knowledge" / "data" / "opensearch_docs_chunks.ndjson"
    with open(opensearch_docs_chunks_path, "w", encoding="utf-8") as file:
        for chunk in chunks:
            file.writelines(chunk.json() + "\n")


# def chunking_json():
#     splitter = RecursiveJsonSplitter(max_chunk_size=2000)
#
#     root_path_str = r""
#     root_path = Path(root_path_str)
#     json_files = root_path.glob("**/*.json")
#
#     chunks = []
#     for json_file in json_files:
#         if json_file.name in ["chunks_json.json", "chunks_md.json"]:
#             continue
#         json_data = json.load(json_file.open(encoding="utf-8"))
#
#         for chunk in splitter.create_documents([json_data], convert_lists=True):
#             chunk.metadata.update({
#                 "filepath": str(json_file.relative_to(root_path)),
#                 "filepath_parts": json_file.relative_to(root_path).parts
#             })
#             chunks.append(chunk)
#
#     open_path_str = r""
#     with open(open_path_str, "w", encoding="utf-8") as file:
#         for chunk in chunks:
#             file.writelines(chunk.json() + "\n")
#
#     # markdown_file = r""
#     # with open(markdown_file, "r") as file:
#     #     markdown_text = file.read()
#     #
#     # chunks = splitter.split_text(markdown_text)  # Zachowuje hierarchię nagłówków w metadanych
#     #
#     # for i, chunk in enumerate(chunks):
#     #     print(i, chunk.metadata)


if __name__ == "__main__":
    chunking_md()
    # chunking_json()
