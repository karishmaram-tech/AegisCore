"""Unit tests for aegiscore_core.utils.config"""

from aegiscore_core.utils.config import AegiscoreConfig, load_config


class TestAegiscoreConfig:
    def test_default_values(self):
        config = AegiscoreConfig()
        assert config.debug is False

    def test_llm_defaults(self):
        config = AegiscoreConfig()
        assert config.llm.proxy_url == "http://localhost:4000"
        assert config.llm.proxy_api_key == "sk-aegiscore-master"

    def test_env_override(self, monkeypatch):
        monkeypatch.setenv("AEGISCORE_DEBUG", "true")
        config = AegiscoreConfig()
        assert config.debug is True


class TestLoadConfig:
    def test_returns_defaults(self):
        config = load_config()
        assert config.llm.proxy_url == "http://localhost:4000"
