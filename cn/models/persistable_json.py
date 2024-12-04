import numpy as np
import dataclasses_json.cfg

dataclasses_json.cfg.global_config.decoders[np.ndarray] = np.asarray
dataclasses_json.cfg.global_config.encoders[np.ndarray] = np.ndarray.tolist


class PersistableJson:
    def save_json(self, file_path: str) -> None:
        """Save the model to a JSON file."""
        with open(file_path, "w") as f:
            f.write(self.to_json())  # type: ignore

    @classmethod
    def load_json(cls, file_path: str):
        """Load a model from a JSON file."""
        with open(file_path, "rb") as f:
            data = f.read().decode("utf-8")

        print(f"cls: {cls}, data: {data}")

        # return cls.from_json(data)  # type: ignore
        return cls.schema().loads(data)  # type: ignore
