from dataclasses import dataclass


@dataclass
class TextChunk:
    text: str
    chunk_index: int
    char_start: int
    char_end: int


class TextChunker:
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = ["\n\n", "\n", ". ", " ", ""]

    def chunk_text(self, text: str) -> list[TextChunk]:
        if not text.strip():
            return []

        chunks = self._recursive_split(text, self.separators)
        result = []
        char_pos = 0

        for i, chunk_text in enumerate(chunks):
            start = text.find(chunk_text, max(0, char_pos - self.chunk_overlap))
            if start == -1:
                start = char_pos
            end = start + len(chunk_text)

            result.append(TextChunk(
                text=chunk_text.strip(),
                chunk_index=i,
                char_start=start,
                char_end=end,
            ))
            char_pos = end - self.chunk_overlap

        return [c for c in result if c.text]

    def _recursive_split(self, text: str, separators: list[str]) -> list[str]:
        if len(text) <= self.chunk_size:
            return [text] if text.strip() else []

        sep = separators[0] if separators else ""
        remaining_seps = separators[1:] if len(separators) > 1 else [""]

        if not sep:
            # Hard split at chunk_size
            chunks = []
            for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
                chunk = text[i:i + self.chunk_size]
                if chunk.strip():
                    chunks.append(chunk)
            return chunks

        parts = text.split(sep)
        chunks = []
        current = ""

        for part in parts:
            candidate = current + sep + part if current else part
            if len(candidate) <= self.chunk_size:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                if len(part) > self.chunk_size:
                    chunks.extend(self._recursive_split(part, remaining_seps))
                    current = ""
                else:
                    current = part

        if current.strip():
            chunks.append(current)

        return chunks
