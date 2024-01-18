from dynaconf import Dynaconf

settings = Dynaconf(
    settings_files=['settings_local.toml', '.secrets.toml'],
)