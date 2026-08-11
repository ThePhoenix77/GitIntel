
from gitintel.models import (
    Commit,
    Hotspot,
)


def calculate_hotspots(
    commits: list[Commit],
    file_changes: dict[str, dict],
    ownership: dict[str, str],
) -> list[Hotspot]:
    """
    Calculate repository hotspots.

    Args:
        commits:
            Repository commits

        file_changes:
            File statistics

        ownership:
            File owners

    Returns:
        Sorted hotspots
    """

    hotspots = []


    for file_path, stats in file_changes.items():

        modifications = (
            stats.get(
                "modifications",
                0,
            )
        )


        lines_changed = (
            stats.get(
                "lines_changed",
                0,
            )
        )


        contributors = (
            stats.get(
                "contributors",
                0,
            )
        )


        score = 0

        reasons = []


        # -------------------------
        # Modification frequency
        # -------------------------

        if modifications > 50:

            score += 30

            reasons.append(
                "Frequently modified"
            )

        elif modifications > 20:

            score += 15



        # -------------------------
        # Code churn
        # -------------------------

        if lines_changed > 3000:

            score += 30

            reasons.append(
                "High code churn"
            )

        elif lines_changed > 1000:

            score += 15



        # -------------------------
        # Contributors
        # -------------------------

        if contributors > 5:

            score += 25

            reasons.append(
                "Many contributors"
            )

        elif contributors > 2:

            score += 10



        # -------------------------
        # Ownership
        # -------------------------

        owner = ownership.get(
            file_path
        )


        if owner is None:

            score += 15

            reasons.append(
                "No clear owner"
            )


        if score == 0:
            continue


        hotspots.append(
            Hotspot(
                file_path=file_path,
                risk_score=min(
                    score,
                    100,
                ),
                modifications=modifications,
                lines_changed=lines_changed,
                contributors=contributors,
                owner=owner,
                reasons=reasons,
            )
        )


    return sorted(
        hotspots,
        key=lambda h: h.risk_score,
        reverse=True,
    )