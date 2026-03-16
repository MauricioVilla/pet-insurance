from dataclasses import dataclass
from typing import Any


@dataclass
class PaginatedResult:
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int


@dataclass
class ServiceResult:
    success: bool
    data: Any = None
    error: str = ''
    errors: dict = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = {}
