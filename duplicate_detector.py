
from difflib import SequenceMatcher


def find_possible_duplicates(new_issue, issues):
    """Find existing complaints with similar titles and locations."""

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

        if (
            title_similarity >= 0.85
            and location_similarity >= 0.85
            and same_category
        ):
            duplicates.append(existing.to_dict())

    return duplicates

