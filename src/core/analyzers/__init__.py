"""
Analysis pipeline framework for shader analyzers
"""
from typing import List, Dict, Any, Callable

class AnalysisPipeline:
    """Pipeline to run multiple analyzers on shader data."""
    def __init__(self):
        self.analyzers: List[Callable[[Any], Dict[str, Any]]] = []

    def add_analyzer(self, analyzer: Callable[[Any], Dict[str, Any]]):
        self.analyzers.append(analyzer)

    def run(self, shader_data: Any) -> List[Dict[str, Any]]:
        results = []
        for analyzer in self.analyzers:
            result = analyzer(shader_data)
            results.append(result)
        return results
