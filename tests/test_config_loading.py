import os
import json
import logging
from agent.config_loader import load_config


def test_load_config_file_not_found(tmp_path, caplog):
    os.chdir(tmp_path)
    caplog.set_level(logging.ERROR)
    config = load_config()
    assert config == {}
    assert "hephaestus_config.json" in caplog.text
    assert "not found" in caplog.text


def test_load_config_malformed_json(tmp_path, caplog):
    os.chdir(tmp_path)
    with open("hephaestus_config.json", "w", encoding="utf-8") as f:
        f.write("{ invalid json")
    fallback = {"default": True}
    with open("example_config.json", "w", encoding="utf-8") as f:
        json.dump(fallback, f)
    caplog.set_level(logging.INFO)
    config = load_config()
    assert config == fallback
    assert "Error parsing" in caplog.text
    assert "example_config.json" in caplog.text