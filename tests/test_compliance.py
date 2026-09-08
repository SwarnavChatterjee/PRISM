from src.compliance.engine import evaluate_device
from src.normalization.engine import normalize_config


def test_evaluate_normalized_device_and_trace_source():
    config = normalize_config(
        "\n".join(
            [
                "ip ssh version 2",
                "no ip telnet server",
                "no ip http server",
                "aaa new-model",
                "service password-encryption",
                "security passwords min-length 8",
                "logging host 198.51.100.10",
                "aaa accounting exec default start-stop group tacacs+",
                "ip access-list extended MGMT-IN",
                "deny ip any any log",
            ]
        ),
        "cisco",
    )
    result = evaluate_device(config.model_dump(), "cis_benchmarks")
    assert result["passed"] == 10
    assert result["failed"] == 0
    assert result["findings"][0]["source_line"] == 1


def test_missing_control_is_a_fail_not_a_pass():
    config = normalize_config("ip ssh version 2", "cisco")
    result = evaluate_device(config.model_dump(), "cis_benchmarks")
    assert result["passed"] == 1
    assert result["failed"] == 9
    assert result["critical_count"] == 0
