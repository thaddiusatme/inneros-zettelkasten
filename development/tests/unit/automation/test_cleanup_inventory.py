import pytest


@pytest.mark.parametrize(
    "source_path, expected_destination",
    [
        ("Projects/ACTIVE/draft-todo.md", "Projects/COMPLETED-2025-10/draft-todo.md"),
        (
            "Projects/ACTIVE/november-summary.md",
            "Projects/COMPLETED-2025-11/november-summary.md",
        ),
        (
            "development/docs/YOUTUBE-INTEGRATION-MAINTENANCE.md",
            "Projects/REFERENCE/youtube-integration-maintenance.md",
        ),
    ],
)
def test_cleanup_inventory_flags_mismatched_locations(tmp_path, source_path, expected_destination):
    cleanup_log = tmp_path / "cleanup-inventory.yaml"

    active_file = tmp_path / source_path
    active_file.parent.mkdir(parents=True, exist_ok=True)
    active_file.write_text("dummy content")

    from src.automation import cleanup_inventory

    cleanup_inventory.generate_inventory(
        vault_root=tmp_path,
        inventory_path=cleanup_log,
        sources=[source_path],
    )

    data = cleanup_log.read_text()

    assert expected_destination in data, (
        "Expected cleanup inventory to recommend moving documentation into the "
        "monthly completed archive."
    )


def test_cleanup_inventory_routes_automation_assets(tmp_path):
    cleanup_log = tmp_path / "cleanup-inventory.yaml"

    asset_relative_path = ".automation/scripts/audit_design_flaws.sh"
    asset_file = tmp_path / asset_relative_path
    asset_file.parent.mkdir(parents=True, exist_ok=True)
    asset_file.write_text("#!/usr/bin/env bash\necho 'audit'\n")

    from src.automation import cleanup_inventory

    cleanup_inventory.generate_inventory(
        vault_root=tmp_path,
        inventory_path=cleanup_log,
        sources=[asset_relative_path],
    )

    data = cleanup_log.read_text()

    assert "development/src/automation/tools/audit_design_flaws.sh" in data
    assert "trigger: schedule" in data
    assert "monitoring: cron-log" in data
