import json
from pathlib import Path

class Config:
    def __init__(
        self,
        save_path: str = "./data/jmcomic",
        max_workers: int = 3,
        proxy: str = None,
        allow_groups: list = []
    ):
        self.save_path = Path(save_path).absolute().as_posix()
        self.max_workers = max_workers
        self.proxy = proxy
        self.allow_groups = allow_groups

    @classmethod
    def load(cls):
        config_file = Path(__file__).parent / "data/config.json"
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                return cls(**json.load(f))
        except FileNotFoundError:
            default = cls()
            default.save()
            return default

    def save(self):
        config_file = Path(__file__).parent / "data/config.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "save_path": self.save_path,
                    "max_workers": self.max_workers,
                    "proxy": self.proxy,
                    "allow_groups": self.allow_groups
                },
                f,
                ensure_ascii=False,
                indent=2
            )