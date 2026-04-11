from __future__ import annotations

import math
import re
from collections import Counter


STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "have",
    "i",
    "in",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "this",
    "to",
    "was",
    "were",
    "with",
}


TOPIC_DEFINITIONS = [
    (
        "nail_file_effectiveness",
        "Nail File Effectiveness",
        {"nail", "file", "smooth", "smoothly", "edge", "polish", "shape"},
    ),
    (
        "product_quality",
        "Product Quality",
        {"quality", "excellent", "great", "best", "outstanding", "amazing", "well"},
    ),
    (
        "cuticle_care",
        "Cuticle Care",
        {"cuticle", "stick", "clean", "cleanup", "remove", "push"},
    ),
    (
        "delivery_experience",
        "Delivery Experience",
        {"delivery", "shipping", "arrive", "arrived", "fast", "package"},
    ),
    (
        "value_for_money",
        "Value for Money",
        {"value", "worth", "price", "expensive", "cheap"},
    ),
]


def _normalize_text(text: str) -> str:
    return (text or "").strip().lower()


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z]+", _normalize_text(text))


def _keyword_summary(text: str, top_n: int = 3) -> list[str]:
    words = [w for w in _tokenize(text) if w not in STOP_WORDS and len(w) > 2]
    if not words:
        return []
    return [w for w, _ in Counter(words).most_common(top_n)]


def generate_review_title(content: str, rating: int) -> str:
    """
    Lightweight AI-style title extraction fallback based on comment text.
    """
    keywords = _keyword_summary(content, top_n=3)
    if keywords:
        phrase = " ".join(w.capitalize() for w in keywords[:2])
        if rating >= 4:
            return f"{phrase} Works Great"
        if rating <= 2:
            return f"{phrase} Needs Improvement"
        return f"{phrase} Mixed Experience"

    if rating >= 4:
        return "Great Product Experience"
    if rating <= 2:
        return "Could Be Better"
    return "Decent Overall Experience"


def build_review_topics(review_texts: list[str]) -> list[dict]:
    if not review_texts:
        return []

    review_count = len(review_texts)
    topic_results = []

    for topic_key, topic_title, topic_keywords in TOPIC_DEFINITIONS:
        matched_texts = []
        for text in review_texts:
            tokens = set(_tokenize(text))
            if tokens.intersection(topic_keywords):
                matched_texts.append(text)

        if not matched_texts:
            continue

        mentioned_count = len(matched_texts)
        percent = int(math.floor((mentioned_count / review_count) * 100))
        focus_keywords = _keyword_summary(" ".join(matched_texts), top_n=4)
        focus_text = ", ".join(focus_keywords[:3]) if focus_keywords else "overall performance"

        topic_results.append(
            {
                "key": topic_key,
                "title": topic_title,
                "description": (
                    f"Customers frequently mentioned {focus_text} when discussing this topic."
                ),
                "mentioned_count": mentioned_count,
                "mentioned_percent": percent,
            }
        )

    topic_results.sort(key=lambda item: item["mentioned_count"], reverse=True)
    return topic_results[:5]


def build_customers_say_summary(review_texts: list[str], avg_rating: float) -> str:
    if not review_texts:
        return "There are not enough customer reviews yet to generate a reliable summary."

    topics = build_review_topics(review_texts)
    leading_topics = [item["title"] for item in topics[:2]]

    if avg_rating >= 4.5:
        opening = "Customers are highly positive about this product"
    elif avg_rating >= 3.5:
        opening = "Customers are generally satisfied with this product"
    else:
        opening = "Customer sentiment is mixed for this product"

    if leading_topics:
        joined_topics = " and ".join(leading_topics)
        return f"{opening}, especially around {joined_topics.lower()}."

    return f"{opening} based on the recent review content."
