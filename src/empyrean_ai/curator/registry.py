from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass(frozen=True)
class ModelInfo:
    key: str
    ollama_name: str
    context_max: int
    family: str

class ModelRegistry:
    def __init__(self, cfg: dict):
        self._models: Dict[str, ModelInfo] = {}
        for k, v in cfg["models"]["models"].items():
            self._models[k] = ModelInfo(
                key=k, ollama_name=v["ollama_name"], context_max=v["context_max"], family=v["family"]
            )
        self._aliases: Dict[str, str] = cfg["models"].get("aliases", {})

    def resolve(self, name: str) -> ModelInfo:
        if name in self._aliases:
            name = self._aliases[name]
        if name not in self._models:
            raise KeyError(f"Unknown model: {name}")
        return self._models[name]

    def smallest_for_family(self, task_family: str) -> ModelInfo:
        # simple heuristic: pick initial from routing task_map
        return self.resolve(self.routing_initial(task_family))

    def routing_initial(self, task_family: str) -> str:
        return self._routing["task_map"][task_family]["initial"]  # type: ignore

    def set_routing(self, routing_cfg: dict) -> None:
        self._routing = routing_cfg
