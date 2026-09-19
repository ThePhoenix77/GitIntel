from gitintel.analysis.hotspots import calculate_hotspots


def test_no_hotspots_for_empty_data():
    """Test that empty inputs return empty hotspots list."""
    commits = []
    file_changes = {}
    ownership = {}

    hotspots = calculate_hotspots(commits, file_changes, ownership)

    assert hotspots == []


def test_no_hotspots_for_low_activity_files():
    """Test that files with low activity are skipped (score == 0)."""
    commits = []
    file_changes = {
        "stable.py": {
            "modifications": 5,
            "lines_changed": 50,
            "contributors": 1,
        }
    }
    ownership = {"stable.py": "Alice"}

    hotspots = calculate_hotspots(commits, file_changes, ownership)

    assert hotspots == []


def test_frequently_modified_adds_risk():
    """Test that files with >50 modifications get +30 risk score."""
    commits = []
    file_changes = {
        "active.py": {
            "modifications": 51,
            "lines_changed": 100,
            "contributors": 1,
        }
    }
    ownership = {"active.py": "Alice"}

    hotspots = calculate_hotspots(commits, file_changes, ownership)

    assert len(hotspots) == 1
    assert hotspots[0].file_path == "active.py"
    assert hotspots[0].risk_score == 30
    assert "Frequently modified" in hotspots[0].reasons


def test_moderately_modified_adds_risk():
    """Test that files with >20 modifications get +15 risk score."""
    commits = []
    file_changes = {
        "moderate.py": {
            "modifications": 21,
            "lines_changed": 100,
            "contributors": 1,
        }
    }
    ownership = {"moderate.py": "Alice"}

    hotspots = calculate_hotspots(commits, file_changes, ownership)

    assert len(hotspots) == 1
    assert hotspots[0].risk_score == 15
    assert hotspots[0].reasons == []  # No reason text for moderate threshold


def test_exactly_20_modifications_no_risk():
    """Test that files with exactly 20 modifications get no risk from this rule."""
    commits = []
    file_changes = {
        "boundary.py": {
            "modifications": 20,
            "lines_changed": 100,
            "contributors": 1,
        }
    }
    ownership = {"boundary.py": "Alice"}

    hotspots = calculate_hotspots(commits, file_changes, ownership)

    assert hotspots == []


def test_high_code_churn_adds_risk():
    """Test that files with >3000 lines changed get +30 risk score."""
    commits = []
    file_changes = {
        "churn.py": {
            "modifications": 10,
            "lines_changed": 3001,
            "contributors": 1,
        }
    }
    ownership = {"churn.py": "Alice"}

    hotspots = calculate_hotspots(commits, file_changes, ownership)

    assert len(hotspots) == 1
    assert hotspots[0].risk_score == 30
    assert "High code churn" in hotspots[0].reasons


def test_moderate_code_churn_adds_risk():
    """Test that files with >1000 lines changed get +15 risk score."""
    commits = []
    file_changes = {
        "moderate_churn.py": {
            "modifications": 10,
            "lines_changed": 1001,
            "contributors": 1,
        }
    }
    ownership = {"moderate_churn.py": "Alice"}

    hotspots = calculate_hotspots(commits, file_changes, ownership)

    assert len(hotspots) == 1
    assert hotspots[0].risk_score == 15


def test_many_contributors_adds_risk():
    """Test that files with >5 contributors get +25 risk score."""
    commits = []
    file_changes = {
        "popular.py": {
            "modifications": 10,
            "lines_changed": 100,
            "contributors": 6,
        }
    }
    ownership = {"popular.py": "Alice"}

    hotspots = calculate_hotspots(commits, file_changes, ownership)

    assert len(hotspots) == 1
    assert hotspots[0].risk_score == 25
    assert "Many contributors" in hotspots[0].reasons


def test_multiple_contributors_adds_risk():
    """Test that files with >2 contributors get +10 risk score."""
    commits = []
    file_changes = {
        "team.py": {
            "modifications": 10,
            "lines_changed": 100,
            "contributors": 3,
        }
    }
    ownership = {"team.py": "Alice"}

    hotspots = calculate_hotspots(commits, file_changes, ownership)

    assert len(hotspots) == 1
    assert hotspots[0].risk_score == 10


def test_no_owner_adds_risk():
    """Test that files without an owner get +15 risk score."""
    commits = []
    file_changes = {
        "orphan.py": {
            "modifications": 10,
            "lines_changed": 100,
            "contributors": 1,
        }
    }
    ownership = {}  # No owner for orphan.py

    hotspots = calculate_hotspots(commits, file_changes, ownership)

    assert len(hotspots) == 1
    assert hotspots[0].risk_score == 15
    assert "No clear owner" in hotspots[0].reasons
    assert hotspots[0].owner is None


def test_combined_risk_factors():
    """Test that multiple risk factors are summed correctly."""
    commits = []
    file_changes = {
        "risky.py": {
            "modifications": 60,  # +30
            "lines_changed": 4000,  # +30
            "contributors": 8,  # +25
        }
    }
    ownership = {}  # +15 for no owner

    hotspots = calculate_hotspots(commits, file_changes, ownership)

    assert len(hotspots) == 1
    assert hotspots[0].risk_score == 100  # 30+30+25+15 = 100 (capped)
    assert "Frequently modified" in hotspots[0].reasons
    assert "High code churn" in hotspots[0].reasons
    assert "Many contributors" in hotspots[0].reasons
    assert "No clear owner" in hotspots[0].reasons


def test_score_capped_at_100():
    """Test that risk scores are capped at 100."""
    commits = []
    file_changes = {
        "extreme.py": {
            "modifications": 1000,  # Would be +30
            "lines_changed": 100000,  # Would be +30
            "contributors": 100,  # Would be +25
        }
    }
    ownership = {}  # Would be +15

    hotspots = calculate_hotspots(commits, file_changes, ownership)

    assert len(hotspots) == 1
    assert hotspots[0].risk_score == 100  # Capped


def test_hotspots_sorted_by_risk_score():
    """Test that hotspots are returned sorted by risk score descending."""
    commits = []
    file_changes = {
        "low_risk.py": {
            "modifications": 25,  # +15
            "lines_changed": 100,
            "contributors": 1,
        },
        "high_risk.py": {
            "modifications": 60,  # +30
            "lines_changed": 4000,  # +30
            "contributors": 8,  # +25
        },
        "medium_risk.py": {
            "modifications": 30,  # +15
            "lines_changed": 2000,  # +15
            "contributors": 4,  # +10
        },
    }
    ownership = {}

    hotspots = calculate_hotspots(commits, file_changes, ownership)

    assert len(hotspots) == 3
    assert hotspots[0].file_path == "high_risk.py"
    assert hotspots[1].file_path == "medium_risk.py"
    assert hotspots[2].file_path == "low_risk.py"
    assert hotspots[0].risk_score > hotspots[1].risk_score > hotspots[2].risk_score


def test_hotspot_with_owner():
    """Test that hotspots preserve owner information when available."""
    commits = []
    file_changes = {
        "owned.py": {
            "modifications": 60,
            "lines_changed": 100,
            "contributors": 1,
        }
    }
    ownership = {"owned.py": "Alice"}

    hotspots = calculate_hotspots(commits, file_changes, ownership)

    assert len(hotspots) == 1
    assert hotspots[0].owner == "Alice"


def test_hotspot_preserves_file_stats():
    """Test that hotspots preserve original file statistics."""
    commits = []
    file_changes = {
        "stats.py": {
            "modifications": 60,
            "lines_changed": 1234,
            "contributors": 3,
        }
    }
    ownership = {"stats.py": "Bob"}

    hotspots = calculate_hotspots(commits, file_changes, ownership)

    assert len(hotspots) == 1
    assert hotspots[0].modifications == 60
    assert hotspots[0].lines_changed == 1234
    assert hotspots[0].contributors == 3


def test_missing_file_change_fields():
    """Test that missing fields in file_changes are handled gracefully."""
    commits = []
    file_changes = {
        "minimal.py": {
            "modifications": 60,
            # Missing lines_changed and contributors
        }
    }
    ownership = {"minimal.py": "Alice"}

    hotspots = calculate_hotspots(commits, file_changes, ownership)

    assert len(hotspots) == 1
    assert hotspots[0].lines_changed == 0  # Default from .get()
    assert hotspots[0].contributors == 0  # Default from .get()


def test_multiple_files_mixed_risk():
    """Test processing multiple files with varying risk levels."""
    commits = []
    file_changes = {
        "safe.py": {
            "modifications": 5,
            "lines_changed": 50,
            "contributors": 1,
        },
        "risky.py": {
            "modifications": 60,
            "lines_changed": 4000,
            "contributors": 8,
        },
        "moderate.py": {
            "modifications": 25,
            "lines_changed": 1500,
            "contributors": 3,
        },
    }
    ownership = {"safe.py": "Alice", "risky.py": "Bob", "moderate.py": "Carol"}

    hotspots = calculate_hotspots(commits, file_changes, ownership)

    # safe.py should be skipped (score == 0)
    assert len(hotspots) == 2
    file_paths = {h.file_path for h in hotspots}
    assert file_paths == {"risky.py", "moderate.py"}


def test_boundary_conditions():
    """Test exact boundary conditions for thresholds."""
    commits = []
    file_changes = {
        "mod_50.py": {"modifications": 50, "lines_changed": 100, "contributors": 1},
        "mod_51.py": {"modifications": 51, "lines_changed": 100, "contributors": 1},
        "mod_20.py": {"modifications": 20, "lines_changed": 100, "contributors": 1},
        "mod_21.py": {"modifications": 21, "lines_changed": 100, "contributors": 1},
        "lines_1000.py": {"modifications": 10, "lines_changed": 1000, "contributors": 1},
        "lines_1001.py": {"modifications": 10, "lines_changed": 1001, "contributors": 1},
        "lines_3000.py": {"modifications": 10, "lines_changed": 3000, "contributors": 1},
        "lines_3001.py": {"modifications": 10, "lines_changed": 3001, "contributors": 1},
        "contrib_2.py": {"modifications": 10, "lines_changed": 100, "contributors": 2},
        "contrib_3.py": {"modifications": 10, "lines_changed": 100, "contributors": 3},
        "contrib_5.py": {"modifications": 10, "lines_changed": 100, "contributors": 5},
        "contrib_6.py": {"modifications": 10, "lines_changed": 100, "contributors": 6},
    }
    ownership = {path: "Owner" for path in file_changes.keys()}

    hotspots = calculate_hotspots(commits, file_changes, ownership)

    # Files at exact boundaries should not trigger the higher threshold
    # but may trigger lower thresholds (e.g., 50 > 20 triggers moderate threshold)
    risky_files = {h.file_path for h in hotspots}
    assert "mod_50.py" in risky_files  # Exactly 50, gets +15 (50 > 20)
    assert "mod_51.py" in risky_files  # >50, gets +30
    assert "mod_20.py" not in risky_files  # Exactly 20, no risk (not >20)
    assert "mod_21.py" in risky_files  # >20, gets +15
    assert "lines_1000.py" not in risky_files  # Exactly 1000, no risk (not >1000)
    assert "lines_1001.py" in risky_files  # >1000, gets +15
    assert "lines_3000.py" in risky_files  # Exactly 3000, gets +15 (from >1000 threshold)
    assert "lines_3001.py" in risky_files  # >3000, gets +30
    assert "contrib_2.py" not in risky_files  # Exactly 2, no risk (not >2)
    assert "contrib_3.py" in risky_files  # >2, gets +10
    assert "contrib_5.py" in risky_files  # Exactly 5, gets +10 (from >2 threshold)
    assert "contrib_6.py" in risky_files  # >5, gets +25