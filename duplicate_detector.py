
import re
from difflib import SequenceMatcher


def normalize_text(text):
    """Normalize text for comparison."""
    text = str(text).lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return " ".join(text.split())


def similarity(text1, text2):
    """Return a similarity score between 0 and 1."""
    return SequenceMatcher(
        None,
        normalize_text(text1),
        normalize_text(text2),
    ).ratio()


def find_possible_duplicates(new_issue, existing_issues,
                             threshold=0.65):
    """
    Find reports with similar titles at the same location.
    Returns possible matches for human review.
    """
    matches = []

    for _, existing in existing_issues.iterrows():
        same_location = (
            normalize_text(new_issue["location"])
            == normalize_text(existing["location"])
        )

        if not same_location:
            continue

        title_similarity = similarity(
            new_issue["issue"],
            existing["issue"],
        )

        if title_similarity >= threshold:
            matches.append({
                "id": existing["id"],
                "issue": existing["issue"],
                "location": existing["location"],
                "similarity": round(title_similarity * 100, 1),
            })

    return matches
