from dataclasses import dataclass


@dataclass(frozen=True)
class Evidence:
    source: str
    text: str


def build_evidence_context(evidence: list[Evidence]) -> str:
    blocks = []
    for item in evidence:
        blocks.append(f"<evidence source={item.source!r}>\n{item.text}\n</evidence>")
    return "\n".join(blocks)
