import pytest


def test_sanitize_tags_removes_prompt_artifact_prefixes_and_salvages_suffixes():
    from src.utils.tags import sanitize_tags

    raw = [
        "ai-processing",
        "herearetheextractedrelevanttags",
        "herearetheextractedtags",
        "herearetheextractedtagseducation",
        "herearetheextractedtagsinkebab-caseformat",
        "herearetheextractedtagsprohibition",
        "herearetheextractedtagsvideo-content",
        "herearetherelevanttagsextractedfromthecontentprohibition",
    ]

    assert sanitize_tags(raw) == [
        "ai-processing",
        "education",
        "prohibition",
        "video-content",
    ]


def test_sanitize_tags_handles_inline_yaml_list_format_and_dedupes():
    from src.utils.tags import sanitize_tags

    raw = [
        "ai-effects-on-lives",
        "ai-environmental-impact",
        "ai-water-use",
        "artificial-intelligence",
        "artificial-intelligence-environmental-impact",
        "environmental-impact",
        "environmental-sustainability",
        "herearetheextractedrelevanttagsai",
        "environmental-impact",  # duplicate
    ]

    assert sanitize_tags(raw) == [
        "ai-effects-on-lives",
        "ai-environmental-impact",
        "ai-water-use",
        "artificial-intelligence",
        "artificial-intelligence-environmental-impact",
        "environmental-impact",
        "environmental-sustainability",
        "ai",
    ]


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("tag1, tag2, tag3", ["tag1", "tag2", "tag3"]),
        ("tag1 tag2\ntag3", ["tag1", "tag2", "tag3"]),
        ("Tags: education, video-content", ["education", "video-content"]),
        (
            "here are the extracted tags: education, video-content",
            ["education", "video-content"],
        ),
    ],
)
def test_sanitize_tags_splits_strings_and_strips_tag_preambles(raw, expected):
    from src.utils.tags import sanitize_tags

    assert sanitize_tags(raw) == expected
