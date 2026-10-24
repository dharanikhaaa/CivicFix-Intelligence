
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
    
from difflib import SequenceMatcher


def find_possible_duplicates(new_issue, issues):
    """
    Find genuinely similar existing complaints.
    Returns matching complaints only when title and location
    are sufficiently similar.
    """
    if issues is None or issues.empty:
        return []

    new_title = str(new_issue.get("issue", "")).strip().lower()
    new_location = str(new_issue.get("location", "")).strip().lower()
    new_category = str(new_issue.get("category", "")).strip().lower()

    if not new_title or not new_location:
        return []

    duplicates = []

    for _, existing in issues.iterrows():
        existing_id = str(existing.get("id", ""))

        # Do not compare a complaint with itself.
        if existing_id == str(new_issue.get("id", "")):
            continue

        old_title = str(existing.get("issue", "")).strip().lower()
        old_location = str(existing.get("location", "")).strip().lower()
        old_category = str(existing.get("category", "")).strip().lower()

        if not old_title or not old_location:
            continue

        title_similarity = SequenceMatcher(
            None, new_title, old_title
        ).ratio()

        location_similarity = SequenceMatcher(
            None, new_location, old_location
        ).ratio()

        same_category = (
            not new_category
            or not old_category
            or new_category == old_category
        )

        # Require a very similar title AND location.
        if (
            title_similarity >= 0.85
            and location_similarity >= 0.85
            and same_category
        ):
            duplicates.append(existing.to_dict())

    return duplicates
