"""CLI: python -m ml"""

from __future__ import annotations

import json
import sys

from ml.train import run_training


def main() -> int:
    report = run_training()
    print(json.dumps(
        {
            "regression_best": report["regression"]["best_model"],
            "regression_test": report["regression"]["best_test_metrics"],
            "classification_best": report["classification"]["best_model"],
            "classification_test": report["classification"]["best_test_metrics"],
            "metrics_file": report["metrics_path"],
        },
        ensure_ascii=False,
        indent=2,
    ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
