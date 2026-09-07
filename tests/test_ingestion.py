from src.ingestion.uploader import decode_config, detect_vendor


def test_decode_config_and_detect_cisco():
    raw = decode_config("router.cfg", b"ip ssh version 2\nno ip http server")
    assert detect_vendor(raw) == ("cisco", 0.65)


def test_detect_juniper_style():
    assert detect_vendor("set system services ssh") == ("juniper", 0.85)


def test_reject_binary_or_unsupported_files():
    try:
        decode_config("router.pdf", b"config")
    except ValueError as exc:
        assert "Unsupported" in str(exc)
    else:
        raise AssertionError("Expected unsupported file type to fail")
