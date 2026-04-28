import os

from .parser import Parser, resolve_data_dir


def detect_parser(data_dir: str) -> Parser:
    from .parser_jsonl import ParserJsonl

    resolved_data_dir = resolve_data_dir(data_dir)

    _parsers: dict[str, type[Parser]] = {
        ParserJsonl(resolved_data_dir).file_extension: ParserJsonl,
    }

    if not os.path.isdir(resolved_data_dir):
        raise FileNotFoundError(f"Data directory not found: {resolved_data_dir}")

    for entry in os.listdir(resolved_data_dir):
        ext = os.path.splitext(entry)[1].lower()
        if ext in _parsers:
            return _parsers[ext](resolved_data_dir)
    supported = ", ".join(sorted(_parsers))
    raise RuntimeError(
        f"No supported data files found in {resolved_data_dir}. "
        f"Supported extensions: {supported}"
    )
