from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, HttpUrl


class Paper(BaseModel):
	title: str
	link: HttpUrl
	abstract: str
	published: datetime


class ClassificationResult(BaseModel):
	is_interpretability: bool
	reason: str | None = None
