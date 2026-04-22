import os

from .parser import Parser, DATA_DIR


def detect_parser() -> Parser:
    from .parser_jsonl import ParserJsonl

    _parsers: dict[str, type[Parser]] = {
        ParserJsonl().file_extension: ParserJsonl,
    }

    for entry in os.listdir(DATA_DIR):
        ext = os.path.splitext(entry)[1].lower()
        if ext in _parsers:
            return _parsers[ext]()
    supported = ", ".join(sorted(_parsers))
    raise RuntimeError(
        f"No supported data files found in {DATA_DIR}. "
        f"Supported extensions: {supported}"
    )
