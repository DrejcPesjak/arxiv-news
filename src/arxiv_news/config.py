"""
Configuration loader for arxiv-news.
Loads config.yaml and processes prompt templates with static parameters.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import yaml


def _load_config() -> Dict[str, Any]:
	"""Load configuration from config.yaml in project root."""
	# Go up from src/arxiv_news/ to project root
	config_path = Path(__file__).parent.parent.parent / "config.yaml"
	
	if not config_path.exists():
		raise FileNotFoundError(f"Configuration file not found: {config_path}")
	
	with open(config_path, "r", encoding="utf-8") as f:
		return yaml.safe_load(f)


# Load configuration once at module import
_CONFIG = _load_config()


# ============================================================================
# ArXiv Configuration
# ============================================================================
ARXIV_CATEGORY = _CONFIG["arxiv"]["category"]
ARXIV_DEFAULT_DAYS = _CONFIG["arxiv"]["default_days"]
ARXIV_DEFAULT_LIMIT = _CONFIG["arxiv"]["default_limit"]
ARXIV_DEFAULT_NO_LIMIT = _CONFIG["arxiv"]["default_no_limit"]


# ============================================================================
# Ollama Configuration
# ============================================================================
OLLAMA_URL = _CONFIG["ollama"]["url"]


# ============================================================================
# Keyword Filter Configuration
# ============================================================================
KEYWORD_LIST = _CONFIG["keyword_filter"]["keywords"]


# ============================================================================
# Classification Configuration
# ============================================================================
CLASSIFICATION_MODEL = _CONFIG["classification"]["model"]
CLASSIFICATION_PROMPT = _CONFIG["classification"]["prompt"]


# ============================================================================
# Ranking Configuration
# ============================================================================
RANKING_MODEL = _CONFIG["ranking"]["model"]
RANKING_TOURNAMENT_TOPK = _CONFIG["ranking"]["tournament_topk"]

# Process ranking prompt: fill static params but keep {num} as placeholder
_ranking_template = _CONFIG["ranking"]["prompt_template"]
_research_focus = _CONFIG["ranking"]["research_focus"]
_think_time = _CONFIG["ranking"]["think_time"]

# Fill static params while keeping {num} as a placeholder for runtime
RANKING_PROMPT_TEMPLATE = _ranking_template.format(
	num="{num}",  # Keep as placeholder for runtime
	research_focus=_research_focus,
	think_time=_think_time
)


# ============================================================================
# Output Configuration
# ============================================================================
OUTPUT_BASE_DIR = Path(_CONFIG["output"]["base_dir"])
OUTPUT_ALL_DIR = Path(_CONFIG["output"]["all_dir"])
OUTPUT_FILTERED_DIR = Path(_CONFIG["output"]["filtered_dir"])
OUTPUT_RANKED_DIR = Path(_CONFIG["output"]["ranked_dir"])


# ============================================================================
# Helper Functions
# ============================================================================

def get_ranking_prompt(num: int) -> str:
	"""Get ranking prompt with the given number of papers to select."""
	return RANKING_PROMPT_TEMPLATE.format(num=num)


def reload_config() -> None:
	"""Reload configuration from disk (useful for testing/development)."""
	global _CONFIG, ARXIV_CATEGORY, ARXIV_DEFAULT_DAYS, ARXIV_DEFAULT_LIMIT, ARXIV_DEFAULT_NO_LIMIT
	global OLLAMA_URL, KEYWORD_LIST, CLASSIFICATION_MODEL, CLASSIFICATION_PROMPT
	global RANKING_MODEL, RANKING_TOURNAMENT_TOPK, RANKING_PROMPT_TEMPLATE
	global OUTPUT_BASE_DIR, OUTPUT_ALL_DIR, OUTPUT_FILTERED_DIR, OUTPUT_RANKED_DIR
	
	_CONFIG = _load_config()
	
	ARXIV_CATEGORY = _CONFIG["arxiv"]["category"]
	ARXIV_DEFAULT_DAYS = _CONFIG["arxiv"]["default_days"]
	ARXIV_DEFAULT_LIMIT = _CONFIG["arxiv"]["default_limit"]
	ARXIV_DEFAULT_NO_LIMIT = _CONFIG["arxiv"]["default_no_limit"]
	
	OLLAMA_URL = _CONFIG["ollama"]["url"]
	
	KEYWORD_LIST = _CONFIG["keyword_filter"]["keywords"]
	
	CLASSIFICATION_MODEL = _CONFIG["classification"]["model"]
	CLASSIFICATION_PROMPT = _CONFIG["classification"]["prompt"]
	
	RANKING_MODEL = _CONFIG["ranking"]["model"]
	RANKING_TOURNAMENT_TOPK = _CONFIG["ranking"]["tournament_topk"]
	
	_ranking_template = _CONFIG["ranking"]["prompt_template"]
	_research_focus = _CONFIG["ranking"]["research_focus"]
	_think_time = _CONFIG["ranking"]["think_time"]
	
	RANKING_PROMPT_TEMPLATE = _ranking_template.format(
		num="{num}",
		research_focus=_research_focus,
		think_time=_think_time
	)
	
	OUTPUT_BASE_DIR = Path(_CONFIG["output"]["base_dir"])
	OUTPUT_ALL_DIR = Path(_CONFIG["output"]["all_dir"])
	OUTPUT_FILTERED_DIR = Path(_CONFIG["output"]["filtered_dir"])
	OUTPUT_RANKED_DIR = Path(_CONFIG["output"]["ranked_dir"])

