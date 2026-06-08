import pytest

from solaredge_ops.config import load_config
from solaredge_ops.models import Severity


VALID_YAML = """
solaredge:
  api_key: "real-key-123"
  max_requests_per_day: 300
sites:
  - id: 111
    name: "Site A"
    expected_daily_kwh: 400
  - id: 222
    name: "Site B"
polling:
  interval_minutes: 15
  active_hours:
    start: "06:30"
    end: "18:45"
alert_rules:
  equipment_offline:
    enabled: true
    grace_minutes: 90
  low_production:
    enabled: false
notifications:
  telegram:
    enabled: true
    bot_token: "abc:def"
  email:
    enabled: false
recipients:
  - name: "Danny - Maintenance lead"
    role: maintenance
    phone: "+972-50-0000000"
    telegram_chat_id: -100123
    categories: [equipment_offline, low_production]
    min_severity: warning
  - name: "Ronit - Finance"
    role: finance
    email: "ronit@example.com"
    categories: [monthly_report]
reporting:
  monthly:
    enabled: true
    day_of_month: 3
storage:
  state_db_path: "/tmp/state.db"
"""


def test_load_config_parses_all_sections(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(VALID_YAML, encoding="utf-8")

    config = load_config(config_path)

    assert config.api_key == "real-key-123"
    assert config.max_requests_per_day == 300
    assert [s.id for s in config.sites] == [111, 222]
    assert config.sites[0].expected_daily_kwh == 400
    assert config.sites[1].expected_daily_kwh is None

    assert config.polling.interval_minutes == 15
    assert config.polling.active_hours.start.hour == 6
    assert config.polling.active_hours.start.minute == 30
    assert config.polling.active_hours.end.minute == 45

    assert config.alert_rules["equipment_offline"].enabled is True
    assert config.alert_rules["equipment_offline"].get("grace_minutes") == 90
    assert config.alert_rules["low_production"].enabled is False

    assert config.telegram.enabled is True
    assert config.telegram.bot_token == "abc:def"

    assert config.monthly_report.day_of_month == 3
    assert config.state_db_path == "/tmp/state.db"

    assert [r.name for r in config.recipients] == ["Danny - Maintenance lead", "Ronit - Finance"]

    danny = config.recipients[0]
    assert danny.role == "maintenance"
    assert danny.phone == "+972-50-0000000"
    assert danny.telegram_chat_id == "-100123"
    assert danny.email is None
    assert danny.categories == ["equipment_offline", "low_production"]
    assert danny.min_severity == Severity.WARNING

    ronit = config.recipients[1]
    assert ronit.email == "ronit@example.com"
    assert ronit.telegram_chat_id is None
    assert ronit.min_severity == Severity.INFO  # default


def test_load_config_rejects_placeholder_api_key(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(VALID_YAML.replace('"real-key-123"', '"YOUR_ACCOUNT_OR_SITE_API_KEY"'), encoding="utf-8")

    with pytest.raises(ValueError, match="api_key"):
        load_config(config_path)


def test_load_config_requires_at_least_one_site(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text('solaredge:\n  api_key: "real-key"\nsites: []\n', encoding="utf-8")

    with pytest.raises(ValueError, match="site"):
        load_config(config_path)


def test_load_config_rejects_recipient_without_a_channel(tmp_path):
    config_path = tmp_path / "config.yaml"
    bad_yaml = VALID_YAML.replace(
        '    email: "ronit@example.com"\n',
        "",
    )
    config_path.write_text(bad_yaml, encoding="utf-8")

    with pytest.raises(ValueError, match="Ronit - Finance.*telegram_chat_id nor email"):
        load_config(config_path)


def test_load_config_rejects_invalid_min_severity(tmp_path):
    config_path = tmp_path / "config.yaml"
    bad_yaml = VALID_YAML.replace("min_severity: warning", "min_severity: urgent")
    config_path.write_text(bad_yaml, encoding="utf-8")

    with pytest.raises(ValueError, match="invalid min_severity 'urgent'"):
        load_config(config_path)


def test_site_by_id_lookup(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(VALID_YAML, encoding="utf-8")
    config = load_config(config_path)

    assert config.site_by_id(111).name == "Site A"
    assert config.site_by_id(999) is None
