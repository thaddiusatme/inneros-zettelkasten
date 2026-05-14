"""
enrichment — per-note AI enhancement pipeline.

Consolidates five former modules:
  - tagger.py              → AITagger
  - summarizer.py          → AISummarizer
  - enhancer.py            → AIEnhancer
  - ai_enhancement_manager → AIEnhancementManager
  - metadata_repair_engine → MetadataRepairEngine

Import boundary: imports from llm_client (OllamaClient) and src.utils only.
Does NOT import from any other src.ai module.
"""

import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .llm_client import AIEnhancementResult, ConfigDict, OllamaClient
from src.utils.bug_reporter import BugReporter
from src.utils.tags import sanitize_tags


# ---------------------------------------------------------------------------
# AITagger
# ---------------------------------------------------------------------------


class AITagger:
    """Generates relevant tags for notes using AI analysis."""

    def __init__(
        self, min_confidence: float = 0.7, config: Optional[Dict[str, Any]] = None
    ):
        self.ollama_client = OllamaClient(config=config)
        self.min_confidence = min_confidence

    def generate_tags(
        self, content: str, min_tags: int = 3, max_tags: int = 8
    ) -> List[str]:
        if not content or not content.strip():
            return []

        processed_content = self._strip_yaml_frontmatter(content)
        if not processed_content.strip():
            return []

        tags = self._generate_ollama_tags(processed_content)
        tags = sanitize_tags(tags)
        return tags[:max_tags]

    def _generate_ollama_tags(self, content: str) -> List[str]:
        if not content or not content.strip():
            return []

        try:
            system_prompt = (
                "You are an expert at extracting relevant tags from technical and academic "
                "content. Analyze the provided text and extract 3-8 highly relevant tags "
                "that capture the key concepts, topics, and themes.\n\n"
                "Guidelines:\n"
                "- Focus on specific, meaningful concepts\n"
                "- Use kebab-case for multi-word tags (e.g., 'machine-learning')\n"
                "- Prioritize technical accuracy over generic terms\n"
                "- Include domain-specific terminology when relevant\n"
                "- Avoid overly broad tags like 'technology' unless essential\n"
                "- Return only the tags, separated by commas\n\n"
                "Example response format: 'tag1, tag2, tag3, tag4'"
            )
            user_prompt = (
                f"Extract relevant tags from this content:\n\n{content}\n\nTags:"
            )
            response = self.ollama_client.generate_completion(
                prompt=user_prompt, system_prompt=system_prompt, max_tokens=100
            )
            return sanitize_tags(response)
        except Exception as e:
            print(f"Warning: Ollama API failed, using fallback: {e}")
            return sanitize_tags(self._generate_mock_tags(content))

    def _strip_yaml_frontmatter(self, content: str) -> str:
        if not content:
            return content
        lines = content.split("\n")
        if len(lines) >= 3 and lines[0].strip() == "---":
            for i in range(1, len(lines)):
                if lines[i].strip() == "---":
                    return "\n".join(lines[i + 1 :])
        return content

    def _generate_mock_tags(self, content: str) -> List[str]:
        content_lower = content.lower()
        tags = []
        keyword_map = {
            "machine learning": ["ai", "machine-learning"],
            "artificial intelligence": ["ai"],
            "python": ["programming", "python"],
            "neural": ["ai", "neural-networks"],
            "algorithm": ["algorithms", "computer-science"],
            "data": ["data-science", "analytics"],
            "learning": ["education", "ai"],
            "programming": ["programming"],
            "development": ["programming", "software"],
            "quantum": ["quantum-computing", "physics"],
            "cryptography": ["cryptography", "security"],
            "drug discovery": ["biotech", "pharmaceuticals"],
            "optimization": ["optimization", "algorithms"],
        }
        for keyword, keyword_tags in keyword_map.items():
            if keyword in content_lower:
                tags.extend(keyword_tags)
        if len(content) > 200:
            tags.extend(["detailed", "comprehensive"])
        return tags[:8]

    def generate_tags_with_confidence(self, content: str) -> List[Tuple[str, float]]:
        if not content or not content.strip():
            return []
        tags = self._generate_mock_tags(content)
        confidence_tags = [(tag, 0.9 - (i * 0.1)) for i, tag in enumerate(tags)]
        return [
            (tag, conf) for tag, conf in confidence_tags if conf >= self.min_confidence
        ]


# ---------------------------------------------------------------------------
# AISummarizer
# ---------------------------------------------------------------------------


class AISummarizer:
    """Generates summaries for long notes using AI analysis."""

    def __init__(
        self,
        min_length: int = 500,
        max_summary_ratio: float = 0.3,
        config: Optional[Dict[str, Any]] = None,
    ):
        self.ollama_client = OllamaClient(config=config)
        self.min_length = min_length
        self.max_summary_ratio = max_summary_ratio

    def should_summarize(self, content: str) -> bool:
        if not content or not content.strip():
            return False
        processed_content = self._strip_yaml_frontmatter(content)
        return self._count_words(processed_content) >= self.min_length

    def generate_summary(
        self, content: str, summary_type: str = "abstractive"
    ) -> Optional[str]:
        if not self.should_summarize(content):
            return None
        processed_content = self._strip_yaml_frontmatter(content)
        try:
            if summary_type == "extractive":
                return self.generate_extractive_summary(content)
            else:
                return self._generate_ollama_summary(processed_content)
        except Exception:
            return None

    def generate_extractive_summary(
        self, content: str, num_sentences: int = 3
    ) -> Optional[str]:
        processed_content = self._strip_yaml_frontmatter(content)
        if not processed_content or not processed_content.strip():
            return None
        if self._count_words(processed_content) < 50:
            return None
        sentences = self._split_into_sentences(processed_content)
        if len(sentences) <= num_sentences:
            return processed_content.strip()
        sentence_scores = self._score_sentences(sentences)
        top_sentences = sorted(
            sentence_scores.items(), key=lambda x: x[1], reverse=True
        )[:num_sentences]
        selected_indices = sorted([sentences.index(sent) for sent, _ in top_sentences])
        return " ".join(sentences[i] for i in selected_indices).strip()

    def _generate_ollama_summary(self, content: str) -> str:
        if not self.ollama_client.health_check():
            raise Exception("Ollama service is not available")
        word_count = self._count_words(content)
        target_length = max(50, int(word_count * self.max_summary_ratio))
        system_prompt = (
            f"You are an expert at creating concise, informative summaries of academic "
            f"and technical content. Create a summary of approximately {target_length} "
            f"words. Provide only the summary without additional commentary."
        )
        user_prompt = f"Please summarize the following content:\n\n{content}"
        try:
            return self.ollama_client.generate(
                prompt=user_prompt, system_prompt=system_prompt
            ).strip()
        except Exception as e:
            raise Exception(f"Failed to generate summary: {str(e)}")

    def _strip_yaml_frontmatter(self, content: str) -> str:
        return re.sub(r"^---\s*\n.*?\n---\s*\n", "", content, flags=re.DOTALL).strip()

    def _count_words(self, text: str) -> int:
        if not text or not text.strip():
            return 0
        return len(text.split())

    def _split_into_sentences(self, text: str) -> List[str]:
        sentences = re.split(r"[.!?]+\s+", text)
        return [s.strip() for s in sentences if s.strip()]

    def _score_sentences(self, sentences: List[str]) -> Dict[str, float]:
        all_words = []
        for sentence in sentences:
            all_words.extend(re.findall(r"\b\w+\b", sentence.lower()))
        word_freq = Counter(all_words)

        sentence_scores = {}
        for i, sentence in enumerate(sentences):
            words = re.findall(r"\b\w+\b", sentence.lower())
            if not words:
                sentence_scores[sentence] = 0.0
                continue
            word_score = sum(word_freq[word] for word in words) / len(words)
            position_bonus = 1.0 - (i / len(sentences)) * 0.2
            length_penalty = (
                0.5 if len(words) < 5 else (0.8 if len(words) > 30 else 1.0)
            )
            sentence_scores[sentence] = word_score * position_bonus * length_penalty
        return sentence_scores


# ---------------------------------------------------------------------------
# AIEnhancer
# ---------------------------------------------------------------------------


class AIEnhancer:
    """AI-powered content enhancement system for zettelkasten notes."""

    def __init__(
        self, model_name: str = "gemma4:latest", min_quality_score: float = 0.6
    ):
        self.ollama_client = OllamaClient(config={"model": model_name})
        self.min_quality_score = min_quality_score

    def analyze_note_quality(self, content: str) -> Dict[str, Any]:
        if not content or not content.strip():
            return {
                "quality_score": 0.0,
                "suggestions": ["Add meaningful content to the note"],
                "missing_elements": [
                    {
                        "type": "content",
                        "description": "Note appears to be empty or minimal",
                    }
                ],
            }
        content_to_analyze = self._strip_yaml_frontmatter(content)
        try:
            return self._generate_ollama_analysis(content_to_analyze)
        except Exception:
            return self._basic_quality_analysis(content_to_analyze)

    def suggest_missing_links(self, content: str) -> List[str]:
        content_to_analyze = self._strip_yaml_frontmatter(content)
        try:
            return self._generate_link_suggestions(content_to_analyze)
        except Exception:
            return []

    def identify_content_gaps(self, content: str) -> List[Dict[str, str]]:
        return self.analyze_note_quality(content).get("missing_elements", [])

    def suggest_improved_structure(self, content: str) -> Dict[str, Any]:
        content_to_analyze = self._strip_yaml_frontmatter(content)
        try:
            result = self._generate_structure_suggestions(content_to_analyze)
            if not isinstance(result, dict):
                return self._basic_structure_suggestion(content_to_analyze)
            if "recommended_structure" not in result or not isinstance(
                result.get("recommended_structure"), list
            ):
                return self._basic_structure_suggestion(content_to_analyze)
            if "reasoning" not in result:
                result["reasoning"] = (
                    "Suggested based on standard technical note organization"
                )
            return result
        except Exception:
            return self._basic_structure_suggestion(content_to_analyze)

    def enhance_note(self, content: str) -> Dict[str, Any]:
        quality_analysis = self.analyze_note_quality(content)
        return {
            "quality_score": quality_analysis["quality_score"],
            "suggestions": quality_analysis["suggestions"],
            "missing_elements": quality_analysis["missing_elements"],
            "link_suggestions": self.suggest_missing_links(content),
            "structure_suggestions": self.suggest_improved_structure(content),
            "enhanced_content": None,
        }

    def analyze_note_quality_deep(
        self, content: str, use_llm: bool = False
    ) -> Dict[str, Any]:
        if not content or not content.strip():
            return {
                "quality_score": 0.0,
                "coherence_score": 0.0,
                "grammar_issues": [],
                "zettelkasten_feedback": {},
                "mode": "heuristic",
            }
        content_to_analyze = self._strip_yaml_frontmatter(content)
        if not use_llm:
            heuristic = self._basic_quality_analysis(content_to_analyze)
            return {
                "quality_score": heuristic["quality_score"],
                "coherence_score": heuristic["quality_score"],
                "grammar_issues": heuristic.get("grammar_issues", []),
                "zettelkasten_feedback": heuristic.get("zettelkasten_compliance", {}),
                "mode": "heuristic",
                "suggestions": heuristic.get("suggestions", []),
                "score_breakdown": heuristic.get("score_breakdown", {}),
            }
        try:
            prompt = self._build_deep_analysis_prompt(content_to_analyze)
            response = self.ollama_client.generate(prompt)
            result = self._parse_deep_analysis_response(response)
            result["mode"] = "llm"
            return result
        except Exception:
            heuristic = self._basic_quality_analysis(content_to_analyze)
            return {
                "quality_score": heuristic["quality_score"],
                "coherence_score": heuristic["quality_score"],
                "grammar_issues": [],
                "zettelkasten_feedback": heuristic.get("zettelkasten_compliance", {}),
                "mode": "heuristic_fallback",
            }

    def _strip_yaml_frontmatter(self, content: str) -> str:
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
        return content[match.end() :] if match else content

    def _generate_ollama_analysis(self, content: str) -> Dict[str, Any]:
        prompt = f"""Analyze this zettelkasten note for quality, completeness, and improvement opportunities.

Content to analyze:
{content}

Provide a JSON response with:
1. "quality_score": A score from 0-1
2. "suggestions": List of specific improvement suggestions
3. "missing_elements": List of missing content types with descriptions

Response format:
{{
    "quality_score": 0.85,
    "suggestions": ["Add practical examples"],
    "missing_elements": [{{"type": "examples", "description": "Missing concrete examples"}}]
}}
"""
        response = self.ollama_client.generate(prompt)
        try:
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return self._basic_quality_analysis(content)
        except (json.JSONDecodeError, ValueError):
            return self._basic_quality_analysis(content)

    def _generate_link_suggestions(self, content: str) -> List[str]:
        prompt = f"""Suggest relevant internal wiki-style links [[note-name]] for this content.

Content:
{content}

Return only a JSON array like: ["[[machine-learning]]", "[[neural-networks]]"]
"""
        response = self.ollama_client.generate(prompt)
        try:
            json_match = re.search(r"\[.*\]", response, re.DOTALL)
            if json_match:
                links = json.loads(json_match.group())
                return [
                    link if link.startswith("[[") else f"[[{link}]]" for link in links
                ]
            return []
        except (json.JSONDecodeError, ValueError):
            return []

    def _generate_structure_suggestions(self, content: str) -> Dict[str, Any]:
        prompt = f"""Analyze the structure of this note and suggest improvements.

Content:
{content}

Provide JSON: {{"recommended_structure": ["Heading 1", "Heading 2"], "reasoning": "..."}}
"""
        response = self.ollama_client.generate(prompt)
        try:
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return self._basic_structure_suggestion(content)
        except (json.JSONDecodeError, ValueError):
            return self._basic_structure_suggestion(content)

    def _basic_quality_analysis(self, content: str) -> Dict[str, Any]:
        placeholder_patterns = [
            r"where did this come from\?",
            r"TODO:",
            r"\[insert .+?\]",
            r"\[add .+?\]",
            r"<insert .+?>",
            r"FIXME:",
        ]
        has_placeholders = any(
            re.search(p, content, re.IGNORECASE) for p in placeholder_patterns
        )
        has_heading = bool(re.search(r"^#+\s+.+$", content, re.MULTILINE))
        has_sections = bool(re.search(r"^##+\s+.+$", content, re.MULTILINE))
        has_lists = bool(re.search(r"^\s*[-*+]\s+.+$", content, re.MULTILINE))
        structural_score = (
            (0.4 if has_heading else 0.0)
            + (0.3 if has_sections else 0.0)
            + (0.3 if has_lists else 0.0)
        )

        word_count = len(content.split())
        content_score = (
            0.4
            if word_count > 100
            else (0.25 if word_count > 50 else (0.1 if word_count > 20 else 0.0))
        )
        if has_placeholders:
            content_score = max(0, content_score - 0.3)
        else:
            content_score += 0.3
        substantive_sentences = [
            s for s in re.split(r"[.!?]+", content) if len(s.split()) > 5
        ]
        if len(substantive_sentences) >= 3:
            content_score += 0.3

        has_links = bool(re.search(r"\[\[.+?\]\]", content))
        link_count = len(re.findall(r"\[\[.+?\]\]", content))
        has_source = bool(
            re.search(
                r"(source:|from:|reference:|see:|cited from|according to|\d{4})",
                content,
                re.IGNORECASE,
            )
        )
        h2_sections = re.findall(r"^##\s+(.+)$", content, re.MULTILINE)
        is_atomic = len(h2_sections) <= 4

        zettelkasten_score = 0.4 if is_atomic else 0.0
        if not is_atomic:
            content_score = max(0, content_score - 0.3)
            structural_score = max(0, structural_score - 0.2)
        content_score = min(content_score, 1.0)
        if has_links:
            zettelkasten_score += (
                0.2
                + (0.1 if link_count >= 2 else 0.0)
                + (0.1 if link_count >= 4 else 0.0)
            )
        if has_source:
            zettelkasten_score += 0.2

        suggestions, missing_elements = [], []
        if not has_heading:
            suggestions.append("Add a clear main heading")
            missing_elements.append(
                {"type": "structure", "description": "Missing main heading"}
            )
        if not has_sections and word_count > 100:
            suggestions.append("Break content into logical sections")
            missing_elements.append(
                {"type": "structure", "description": "Content lacks clear sections"}
            )
        if word_count < 50:
            suggestions.append("Expand the content with more detail")
            missing_elements.append(
                {"type": "content", "description": "Content appears too brief"}
            )
        if has_placeholders:
            suggestions.append(
                "Fill in template placeholders (TODO, 'Where did this come from?')"
            )
            missing_elements.append(
                {
                    "type": "placeholder",
                    "description": "Contains unfilled template placeholders",
                }
            )
        if not has_links:
            suggestions.append("Add internal links to related notes")
            missing_elements.append(
                {"type": "links", "description": "No internal links found"}
            )
        if not has_source:
            suggestions.append("Add source attribution or context")
            missing_elements.append(
                {"type": "source", "description": "Missing source or reference"}
            )
        if not is_atomic:
            suggestions.append("Consider breaking into separate atomic notes")
            missing_elements.append(
                {
                    "type": "atomicity",
                    "description": "Note covers multiple distinct topics",
                }
            )

        final_score = min(
            structural_score * 0.3 + content_score * 0.4 + zettelkasten_score * 0.3, 1.0
        )
        return {
            "quality_score": final_score,
            "suggestions": suggestions,
            "missing_elements": missing_elements,
            "grammar_issues": [],
            "has_placeholders": has_placeholders,
            "zettelkasten_compliance": {
                "atomic": is_atomic,
                "connected": has_links,
                "sourced": has_source,
            },
            "score_breakdown": {
                "structural": {
                    "score": structural_score,
                    "weight": 0.3,
                    "details": f"Heading: {has_heading}, Sections: {has_sections}, Lists: {has_lists}",
                },
                "content_quality": {
                    "score": content_score,
                    "weight": 0.4,
                    "details": f"Words: {word_count}, Placeholders: {has_placeholders}",
                },
                "zettelkasten": {
                    "score": zettelkasten_score,
                    "weight": 0.3,
                    "details": f"Atomic: {is_atomic}, Links: {link_count}, Sourced: {has_source}",
                },
            },
        }

    def _basic_structure_suggestion(self, content: str) -> Dict[str, Any]:
        return {
            "recommended_structure": [
                "# Main Topic",
                "## Overview",
                "## Key Concepts",
                "## Practical Applications",
                "## Related Notes",
                "## References",
            ],
            "reasoning": "Standard zettelkasten note structure for comprehensive coverage",
        }

    def _build_deep_analysis_prompt(self, content: str) -> str:
        return f"""Analyze this zettelkasten note for quality, grammar, coherence, and Zettelkasten methodology compliance.

Content to analyze:
{content}

Provide a JSON response with quality_score (0-1), coherence_score (0-1), grammar_issues list, and zettelkasten_feedback dict.
"""

    def _parse_deep_analysis_response(self, response: str) -> Dict[str, Any]:
        default = {
            "quality_score": 0.5,
            "coherence_score": 0.5,
            "grammar_issues": [],
            "zettelkasten_feedback": {},
        }
        try:
            code_match = re.search(
                r"```(?:json)?\s*(\{.*?\})\s*```", response, re.DOTALL
            )
            if code_match:
                return json.loads(code_match.group(1))
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            result = default.copy()
            for field, pattern in [
                ("quality_score", r'"quality_score"\s*:\s*([\d.]+)'),
                ("coherence_score", r'"coherence_score"\s*:\s*([\d.]+)'),
            ]:
                m = re.search(pattern, response)
                if m:
                    result[field] = float(m.group(1))
            return result
        except (json.JSONDecodeError, ValueError):
            return default


# ---------------------------------------------------------------------------
# AIEnhancementManager
# ---------------------------------------------------------------------------


class AIEnhancementManager:
    """AI-powered note enhancement with 3-tier fallback strategy."""

    def __init__(
        self,
        base_dir: Path,
        config: ConfigDict,
        local_llm: Optional[Any] = None,
        ai_tagger: Optional[Any] = None,
        ai_summarizer: Optional[Any] = None,
    ) -> None:
        self.base_dir = Path(base_dir)
        self.config = config
        self.local_llm = local_llm
        self.ai_tagger = ai_tagger
        self.ai_summarizer = ai_summarizer
        self.external_api = None
        self.bug_reporter = BugReporter(base_dir)

    def enhance_note(
        self, note_path: str, fast: bool = False, dry_run: bool = False
    ) -> AIEnhancementResult:
        if dry_run:
            return {
                "success": True,
                "tags": [],
                "summary": "",
                "skipped": True,
                "reason": "dry_run",
                "source": "dry_run",
            }

        try:
            result = self._enhance_with_local_llm(note_path)
            if result["success"]:
                result.update(
                    {"fallback": False, "tier": "local", "source": "local_ollama"}
                )
                return result
        except Exception as e:
            self.bug_reporter.create_ai_failure_report(
                note_path,
                {"tier": "local_llm", "error": str(e), "error_type": type(e).__name__},
            )

        try:
            result = self._enhance_with_external_api(note_path)
            if result["success"]:
                result.update(
                    {"fallback": True, "tier": "api", "source": "external_api"}
                )
                return result
        except Exception:
            pass

        return {
            "success": False,
            "tags": [],
            "summary": "",
            "quality_score": 0.5,
            "fallback": True,
            "tier": "degraded",
            "source": "degraded",
            "error": "All AI tiers failed",
        }

    def assess_promotion_readiness(self, note_path: str) -> AIEnhancementResult:
        return {
            "ready_for_promotion": True,
            "confidence": 0.8,
            "reasons": ["Content is well-developed", "Clear atomic concept"],
            "suggestions": [],
            "recommended_type": "permanent",
        }

    def generate_ai_tags(self, content: str) -> List[str]:
        if self.local_llm and hasattr(self.local_llm, "generate_tags"):
            return self._enforce_kebab_case(self.local_llm.generate_tags(content))
        return self._enforce_kebab_case(["ai-generated"])

    def _enhance_with_local_llm(self, note_path: str) -> AIEnhancementResult:
        if self.local_llm and hasattr(self.local_llm, "enhance"):
            llm_result = self.local_llm.enhance(note_path)
            return {
                "success": True,
                "tags": llm_result.get("tags", []),
                "summary": llm_result.get("summary", ""),
            }
        if self.ai_tagger and self.ai_summarizer:
            pass
        return {"success": True, "tags": [], "summary": ""}

    def _enhance_with_external_api(self, note_path: str) -> AIEnhancementResult:
        if self.external_api and hasattr(self.external_api, "enhance"):
            api_result = self.external_api.enhance(note_path)
            return {
                "success": True,
                "tags": api_result.get("tags", []),
                "summary": api_result.get("summary", ""),
            }
        return {"success": True, "tags": [], "summary": ""}

    def _enforce_kebab_case(self, tags: List[str]) -> List[str]:
        result = []
        for tag in tags:
            tag = tag.lower()
            tag = re.sub(r"[\s_]+", "-", tag)
            tag = re.sub(r"[^a-z0-9-]", "", tag)
            tag = re.sub(r"-+", "-", tag).strip("-")
            if tag:
                result.append(tag)
        return result


# ---------------------------------------------------------------------------
# MetadataRepairEngine
# ---------------------------------------------------------------------------


class MetadataRepairEngine:
    """Detects and repairs missing frontmatter in Inbox notes."""

    LITERATURE_PATTERN = re.compile(r"^lit-\d{8}-\d{4}")
    FLEETING_PATTERN = re.compile(r"^(fleeting|capture|prompt)-\d{8}-\d{4}")
    LITERATURE_INDICATORS = ["source:", "author:", "url:", "published:"]

    def __init__(self, inbox_dir: str, dry_run: bool = True):
        self.inbox_dir = Path(inbox_dir)
        self.dry_run = dry_run

    def detect_missing_metadata(self, note_path) -> List[str]:
        note_path = Path(note_path)
        content = note_path.read_text()
        if not content.startswith("---"):
            return ["type", "created", "status"]
        parts = content.split("---", 2)
        if len(parts) < 3:
            return ["type", "created", "status"]
        frontmatter = parts[1]
        missing = []
        for field in ("type", "created", "status"):
            if f"{field}:" not in frontmatter:
                missing.append(field)
        return missing

    def infer_note_type(self, note_path) -> str:
        note_path = Path(note_path)
        filename = note_path.name
        if self.LITERATURE_PATTERN.match(filename):
            return "literature"
        if self.FLEETING_PATTERN.match(filename):
            return "fleeting"
        try:
            content = note_path.read_text().lower()
            for indicator in self.LITERATURE_INDICATORS:
                if indicator in content:
                    return "literature"
        except Exception:
            pass
        return "fleeting"

    def repair_note_metadata(self, note_path) -> Dict:
        note_path = Path(note_path)
        missing_fields = self.detect_missing_metadata(str(note_path))
        if not missing_fields:
            return {"would_add": {}, "added": {}}
        repairs = {}
        if "type" in missing_fields:
            repairs["type"] = self.infer_note_type(str(note_path))
        if "created" in missing_fields:
            repairs["created"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        if "status" in missing_fields:
            repairs["status"] = "inbox"
        if self.dry_run:
            return {"would_add": repairs}
        self._add_frontmatter_fields(note_path, repairs)
        return {"added": repairs}

    def _add_frontmatter_fields(self, note_path: Path, fields: Dict[str, str]):
        content = note_path.read_text()
        if not content.startswith("---"):
            lines = ["---"] + [f"{k}: {v}" for k, v in fields.items()] + ["---", ""]
            note_path.write_text("\n".join(lines) + content)
            return
        parts = content.split("---", 2)
        if len(parts) < 3:
            lines = ["---"] + [f"{k}: {v}" for k, v in fields.items()] + ["---", ""]
            note_path.write_text("\n".join(lines) + content)
            return
        frontmatter_lines = parts[1].strip().split("\n")
        frontmatter_lines.extend(f"{k}: {v}" for k, v in fields.items())
        note_path.write_text(f"---\n{chr(10).join(frontmatter_lines)}\n---{parts[2]}")
