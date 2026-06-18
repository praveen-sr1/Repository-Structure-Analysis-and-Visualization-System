"""Parser base class and the shared result structure."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass(slots=True)
class ParseResult:
    """Structured output of parsing one source file.

    Attributes:
        imports: Raw import tokens as written in the source (e.g. ``"os.path"``,
            ``"./utils"``, ``"java.util.List"``). Resolution to concrete files
            happens later in the graph resolver.
        classes: Names of classes/structs/interfaces declared in the file.
        functions: Names of functions/methods declared in the file.
    """

    imports: list[str] = field(default_factory=list)
    classes: list[str] = field(default_factory=list)
    functions: list[str] = field(default_factory=list)

    @property
    def num_imports(self) -> int:
        return len(self.imports)

    @property
    def num_classes(self) -> int:
        return len(self.classes)

    @property
    def num_functions(self) -> int:
        return len(self.functions)


class BaseParser(ABC):
    """Interface implemented by every language parser.

    Subclasses declare the ``language`` they handle and implement :meth:`parse`.
    They must never import, exec, or otherwise run the analysed source.
    """

    #: Canonical language name this parser handles (matches ``detect_language``).
    language: str = "unknown"

    @abstractmethod
    def parse(self, source: str) -> ParseResult:
        """Parse ``source`` text and return the extracted structure."""
        raise NotImplementedError

    def safe_parse(self, source: str) -> ParseResult:
        """Parse, converting any unexpected parser error into an empty result.

        Robustness matters more than completeness here: a single malformed file
        should never abort a whole-repository scan.
        """
        try:
            return self.parse(source)
        except Exception:  # noqa: BLE001 - intentional catch-all for resilience
            return ParseResult()
