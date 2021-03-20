import json
from pathlib import Path
from typing import Dict, Set

from dtags.commons import normalize_tags
from dtags.exceptions import DtagsError

CONFIG_ROOT = ".dtags"
CONFIG_FILE = "config.json"
COMP_FILE = "completion"  # used for tag name completion
DEST_FILE = "destination"  # used for d command

ConfigType = Dict[str, Dict[Path, Set[str]]]


def get_file_path(filename: str) -> Path:
    return Path.home() / CONFIG_ROOT / filename


def get_new_config() -> ConfigType:
    return {"tags": {}}


def load_config_file() -> ConfigType:
    config_file_path = get_file_path(CONFIG_FILE)
    try:
        with open(config_file_path, "r") as fp:
            config_data = json.load(fp)

    except FileNotFoundError:
        new_data = get_new_config()
        save_config_file(new_data)
        return new_data

    except ValueError as err:  # pragma no cover
        raise DtagsError(f"Bad data in {config_file_path.as_posix()}: {err}")
    else:
        tag_config = config_data["tags"]
        return {
            "tags": {
                Path(dirpath): normalize_tags(tags)
                for dirpath, tags in tag_config.items()
            }
        }


def save_config_file(config: ConfigType) -> None:
    config_file_path = get_file_path(CONFIG_FILE)
    config_file_path.parent.mkdir(mode=0o755, exist_ok=True)

    config_data = {
        "tags": {
            dirpath.as_posix(): sorted(tags)
            for dirpath, tags in config["tags"].items()
            if len(tags) > 0
        }
    }
    with open(config_file_path, "w") as fp:
        json.dump(config_data, fp, sort_keys=True, indent=2)

    save_completion_file(config)


def save_completion_file(config: ConfigType) -> None:
    all_tags: Set[str] = set()

    for tags in config["tags"].values():
        all_tags.update(tags)

    with open(get_file_path(COMP_FILE), "w") as fp:
        fp.write(" ".join(all_tags))


def save_destination_file(dirpath: Path) -> None:
    with open(get_file_path(DEST_FILE), "w") as fp:
        fp.write(dirpath.as_posix())
