from src.compliance.engine import evaluate_device
from src.normalization.engine import normalize_config


def test_evaluate_normalized_device_and_trace_source():
    config = normalize_config(
        "ip ssh version 2\nno ip telnet server\nno ip http server\naaa new-model", "cisco"
    )
    result = evaluate_device(config.model_dump(), "cis_benchmarks")
    assert result["passed"] == 4
    assert result["failed"] == 0
    assert result["findings"][0]["source_line"] == 1


def test_missing_control_is_a_fail_not_a_pass():
    config = normalize_config("ip ssh version 2", "cisco")
    result = evaluate_device(config.model_dump(), "cis_benchmarks")
    assert result["passed"] == 1
    assert result["failed"] == 3
    assert result["critical_count"] == 1
