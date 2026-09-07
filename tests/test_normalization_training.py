from src.normalization.engine import normalize_config
from src.training.loop import TrainingLoop


def test_normalizer_uses_confirmed_mapping(tmp_path):
    db_path = str(tmp_path / "knowledge.db")
    TrainingLoop(db_path).save_mapping(
        "unknown_vendor",
        "secure transport version 2",
        "baseline.remote_access.ssh_version",
        mapped_value=2,
    )
    config = normalize_config(
        "secure transport version 2", "unknown_vendor", db_path=db_path
    )
    assert config.baseline.remote_access.ssh_version == 2
    assert config.unmapped_lines == []
