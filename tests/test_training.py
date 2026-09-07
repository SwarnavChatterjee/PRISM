from src.training.loop import TrainingLoop


def test_confirmed_mapping_is_persisted_and_reused(tmp_path):
    loop = TrainingLoop(str(tmp_path / "training.db"))
    assert loop.save_mapping(
        "unknown_vendor",
        "secure transport version 2",
        "baseline.remote_access.ssh_version",
        mapped_value=2,
    )
    assert loop.apply_learned_mapping(
        "secure transport version 2", "unknown_vendor"
    ) == ("baseline.remote_access.ssh_version", 2, 1.0)


def test_unrelated_line_does_not_match_confirmed_mapping(tmp_path):
    loop = TrainingLoop(str(tmp_path / "training.db"))
    loop.save_mapping("vendor", "security mode 2", "baseline.authentication.aaa_enabled")
    assert loop.apply_learned_mapping("security mode 3", "vendor") is None
