from src.normalization.engine import normalize_config, tier1_exact_match


def test_tier1_cisco_ssh():
    assert tier1_exact_match("ip ssh version 2", "cisco") == (
        "baseline.remote_access.ssh_version", 2, 1.0
    )


def test_unknown_line_is_flagged_for_training():
    config = normalize_config("interface GigabitEthernet0/1\nunknown setting", "cisco")
    assert config.unmapped_lines == [
        {"line_no": 1, "raw": "interface GigabitEthernet0/1", "status": "needs_training"},
        {"line_no": 2, "raw": "unknown setting", "status": "needs_training"},
    ]


def test_normalization_preserves_provenance():
    config = normalize_config("! comment\nip ssh version 2\nno ip telnet server", "cisco")
    assert config.baseline.remote_access.ssh_version == 2
    assert config.baseline.remote_access.telnet_enabled is False
    assert config.provenance["baseline.remote_access.ssh_version"]["source_line"] == 2
