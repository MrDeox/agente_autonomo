def test_strict_mode_rejects_unauthorized_fields(caplog):
    invalid_config = {"unauthorized_key": "value"}
    with pytest.raises(ValueError):
        validate_config_structure(invalid_config, logger=logging.getLogger())
    assert "Config validation failed: 'unauthorized_key' was unexpected" in caplog.text

    caplog.clear()
    valid_config = {"authorized_key": "value"}
    validate_config_structure(valid_config, logger=logging.getLogger())
    assert "Validation error:" not in caplog.text