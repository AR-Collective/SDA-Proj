"""
Input Module Validator for Phase 3 - Validates Configuration

This module validates the input module configuration to ensure all required
files exist, schema is properly structured, and CSV columns match the schema.

It provides early validation before attempting to read data, catching errors
with helpful messages instead of failing mid-pipeline.

Example:
    validator = InputValidator(config)
    is_valid, message = validator.validate_all()
    if not is_valid:
        print(f"Validation failed: {message}")
        sys.exit(2)
"""

import sys
from pathlib import Path
from typing import Tuple, Dict, Any, List
import csv as csv_module


class InputValidatorError(Exception):
    """Base exception for input validation errors."""
    pass


class InputValidator:
    """
    Validates the input module configuration.

    Checks:
    - dataset_path file exists and is readable
    - schema_mapping structure is valid
    - pipeline_dynamics are properly configured
    - CSV columns match schema requirements
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize validator with config.

        Args:
            config: The full config.json as dict
        """
        self.config = config
        self.errors = []
        self.warnings = []

    def validate_all(self) -> Tuple[bool, str]:
        """
        Run all validation checks.

        Returns:
            Tuple of (is_valid: bool, message: str)
            If validation passes: (True, "All validations passed")
            If validation fails: (False, "error message with details")
        """
        self.errors = []
        self.warnings = []

        # Run all validation checks
        self._validate_dataset_path()
        self._validate_schema_mapping()
        self._validate_pipeline_dynamics()
        self._validate_csv_columns()

        # Compile results
        if self.errors:
            message = "Validation FAILED:\n" + "\n".join(self.errors)
            return False, message

        if self.warnings:
            message = "Validation passed with warnings:\n" + "\n".join(self.warnings)
            return True, message

        return True, "✓ All validations passed"

    def _validate_dataset_path(self) -> None:
        """Check that dataset_path exists and is readable."""
        if "dataset_path" not in self.config:
            self.errors.append("❌ config.json missing 'dataset_path' key")
            return

        filepath = self.config["dataset_path"]

        # Check path exists
        path = Path(filepath)
        if not path.exists():
            self.errors.append(
                f"❌ Dataset file not found: '{filepath}'"
            )
            return

        # Check it's a file (not directory)
        if not path.is_file():
            self.errors.append(
                f"❌ dataset_path is not a file: '{filepath}'"
            )
            return

        # Check file is readable
        if not path.stat().st_size > 0:
            self.errors.append(
                f"❌ Dataset file is empty: '{filepath}'"
            )
            return

        # Check file extension
        if path.suffix.lower() not in {".csv", ".json"}:
            self.warnings.append(
                f"⚠ Dataset file extension '{path.suffix}' is not .csv or .json"
            )

    def _validate_schema_mapping(self) -> None:
        """Validate schema_mapping structure."""
        if "schema_mapping" not in self.config:
            self.errors.append("❌ config.json missing 'schema_mapping' key")
            return

        schema = self.config["schema_mapping"]

        # Check columns exists
        if "columns" not in schema:
            self.errors.append("❌ schema_mapping missing 'columns' key")
            return

        columns = schema["columns"]

        # Check columns is a list
        if not isinstance(columns, list):
            self.errors.append("❌ schema_mapping.columns must be a list")
            return

        # Check columns is not empty
        if len(columns) == 0:
            self.errors.append("❌ schema_mapping.columns cannot be empty")
            return

        # Validate each column entry
        for i, col in enumerate(columns):
            if not isinstance(col, dict):
                self.errors.append(
                    f"❌ schema_mapping.columns[{i}] is not a dict"
                )
                continue

            # Check required keys
            required_keys = {"source_name", "internal_mapping", "data_type"}
            missing_keys = required_keys - set(col.keys())
            if missing_keys:
                self.errors.append(
                    f"❌ schema_mapping.columns[{i}] missing keys: {missing_keys}"
                )
                continue

            # Check data_type is valid
            valid_types = {"string", "integer", "float", "boolean"}
            if col["data_type"] not in valid_types:
                self.errors.append(
                    f"❌ schema_mapping.columns[{i}]: invalid data_type "
                    f"'{col['data_type']}'. Must be: {valid_types}"
                )
                continue

            # Check for duplicate source_name
            duplicates = [
                c["source_name"] for idx, c in enumerate(columns)
                if c["source_name"] == col["source_name"] and idx != i
            ]
            if duplicates:
                self.errors.append(
                    f"❌ schema_mapping.columns: duplicate source_name "
                    f"'{col['source_name']}' at indices {i} and others"
                )

    def _validate_pipeline_dynamics(self) -> None:
        """Validate pipeline_dynamics configuration."""
        if "pipeline_dynamics" not in self.config:
            self.errors.append("❌ config.json missing 'pipeline_dynamics' key")
            return

        dynamics = self.config["pipeline_dynamics"]

        # Check input_delay_seconds
        if "input_delay_seconds" not in dynamics:
            self.errors.append(
                "❌ pipeline_dynamics missing 'input_delay_seconds' key"
            )
        else:
            delay = dynamics["input_delay_seconds"]
            try:
                delay_float = float(delay)
                if delay_float < 0:
                    self.errors.append(
                        f"❌ input_delay_seconds must be >= 0, got {delay_float}"
                    )
                elif delay_float > 10:
                    self.warnings.append(
                        f"⚠ input_delay_seconds is very large ({delay_float}s)"
                    )
            except (ValueError, TypeError):
                self.errors.append(
                    f"❌ input_delay_seconds must be a number, got '{delay}'"
                )

        # Check core_parallelism
        if "core_parallelism" not in dynamics:
            self.errors.append(
                "❌ pipeline_dynamics missing 'core_parallelism' key"
            )
        else:
            parallelism = dynamics["core_parallelism"]
            try:
                parallelism_int = int(parallelism)
                if parallelism_int < 1:
                    self.errors.append(
                        f"❌ core_parallelism must be >= 1, got {parallelism_int}"
                    )
                elif parallelism_int > 16:
                    self.warnings.append(
                        f"⚠ core_parallelism is very high ({parallelism_int}), "
                        f"may exceed available CPU cores"
                    )
            except (ValueError, TypeError):
                self.errors.append(
                    f"❌ core_parallelism must be an integer, got '{parallelism}'"
                )

        # Check stream_queue_max_size
        if "stream_queue_max_size" not in dynamics:
            self.errors.append(
                "❌ pipeline_dynamics missing 'stream_queue_max_size' key"
            )
        else:
            size = dynamics["stream_queue_max_size"]
            try:
                size_int = int(size)
                if size_int < 10:
                    self.warnings.append(
                        f"⚠ stream_queue_max_size is small ({size_int}), "
                        f"may cause backpressure"
                    )
                if size_int > 10000:
                    self.warnings.append(
                        f"⚠ stream_queue_max_size is very large ({size_int}), "
                        f"may use excessive memory"
                    )
            except (ValueError, TypeError):
                self.errors.append(
                    f"❌ stream_queue_max_size must be an integer, got '{size}'"
                )

    def _validate_csv_columns(self) -> None:
        """Validate that CSV file has all required columns."""
        # Skip if dataset_path validation already failed
        if not self.config.get("dataset_path"):
            return

        if not self.config.get("schema_mapping"):
            return

        filepath = self.config["dataset_path"]
        path = Path(filepath)

        # Only validate CSV files
        if path.suffix.lower() != ".csv":
            return

        # Try to read CSV header
        try:
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv_module.DictReader(f)
                if reader.fieldnames is None:
                    self.errors.append(
                        f"❌ Cannot read CSV header from {filepath}"
                    )
                    return

                csv_columns = set(reader.fieldnames)
        except Exception as e:
            self.errors.append(
                f"❌ Error reading CSV file {filepath}: {str(e)}"
            )
            return

        # Get required columns from schema
        schema = self.config["schema_mapping"]
        required_columns = {
            col["source_name"] for col in schema.get("columns", [])
        }

        # Check all required columns exist in CSV
        missing = required_columns - csv_columns
        if missing:
            self.errors.append(
                f"❌ CSV missing required columns: {missing}\n"
                f"   Available columns: {sorted(csv_columns)}"
            )
            return

        # Warn about extra columns in CSV
        extra = csv_columns - required_columns
        if extra:
            self.warnings.append(
                f"⚠ CSV has extra columns not in schema: {extra}"
            )

    @staticmethod
    def print_validation_result(is_valid: bool, message: str) -> int:
        """
        Print validation result and return exit code.

        Args:
            is_valid: Whether validation passed
            message: Message to display

        Returns:
            Exit code: 0 if valid, 2 if invalid
        """
        print("\n" + "=" * 70)
        print("INPUT MODULE VALIDATION RESULT")
        print("=" * 70)
        print(message)
        print("=" * 70 + "\n")

        if is_valid:
            return 0
        else:
            return 2


def validate_input_config(config: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Convenience function to validate input config.

    Args:
        config: The full config.json as dict

    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    validator = InputValidator(config)
    return validator.validate_all()


# Example usage (for testing)
if __name__ == "__main__":
    import json

    # Try to load and validate the actual config.json
    config_path = Path("config.json")

    if not config_path.exists():
        print("config.json not found in current directory")
        sys.exit(1)

    with open(config_path) as f:
        config = json.load(f)

    validator = InputValidator(config)
    is_valid, message = validator.validate_all()

    exit_code = validator.print_validation_result(is_valid, message)
    sys.exit(exit_code)
