"""
Unit tests for plugins/inputs/input_validator.py

Tests configuration validation for the input module.
"""

import pytest
import sys
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from plugins.inputs.input_validator import InputValidator


class TestValidatorInit:
    """Test InputValidator initialization."""

    def test_init_with_config(self):
        """Test validator initialization with config."""
        config = {"schema_mapping": {"columns": []}}
        validator = InputValidator(config)
        assert validator is not None
        assert validator.config == config


class TestDatasetPathValidation:
    """Test dataset_path validation."""

    def test_valid_dataset_path(self):
        """Test validation with valid dataset path."""
        config = {
            "dataset_path": "data/sample_sensor_data.csv",
            "schema_mapping": {
                "columns": [
                    {
                        "source_name": "Sensor_ID",
                        "internal_mapping": "entity_name",
                        "data_type": "string"
                    }
                ]
            },
            "pipeline_dynamics": {
                "input_delay_seconds": 0.01,
                "core_parallelism": 4,
                "stream_queue_max_size": 50
            }
        }
        validator = InputValidator(config)
        is_valid, msg = validator.validate_all()
        assert is_valid is True

    def test_missing_dataset_path(self):
        """Test error when dataset_path missing."""
        config = {
            "schema_mapping": {"columns": []},
            "pipeline_dynamics": {}
        }
        validator = InputValidator(config)
        is_valid, msg = validator.validate_all()
        assert is_valid is False
        assert "dataset_path" in msg

    def test_nonexistent_file(self):
        """Test error when dataset file doesn't exist."""
        config = {
            "dataset_path": "data/nonexistent_file_12345.csv",
            "schema_mapping": {
                "columns": [
                    {
                        "source_name": "Col1",
                        "internal_mapping": "col1",
                        "data_type": "string"
                    }
                ]
            },
            "pipeline_dynamics": {
                "input_delay_seconds": 0.01,
                "core_parallelism": 4,
                "stream_queue_max_size": 50
            }
        }
        validator = InputValidator(config)
        is_valid, msg = validator.validate_all()
        assert is_valid is False
        assert "not found" in msg.lower()

    def test_empty_file(self):
        """Test error when dataset file is empty."""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            empty_file = f.name

        try:
            config = {
                "dataset_path": empty_file,
                "schema_mapping": {
                    "columns": [
                        {
                            "source_name": "Col1",
                            "internal_mapping": "col1",
                            "data_type": "string"
                        }
                    ]
                },
                "pipeline_dynamics": {
                    "input_delay_seconds": 0.01,
                    "core_parallelism": 4,
                    "stream_queue_max_size": 50
                }
            }
            validator = InputValidator(config)
            is_valid, msg = validator.validate_all()
            assert is_valid is False
            assert "empty" in msg.lower()
        finally:
            Path(empty_file).unlink()


class TestSchemaMappingValidation:
    """Test schema_mapping validation."""

    def test_missing_schema_mapping(self):
        """Test error when schema_mapping missing."""
        config = {
            "dataset_path": "data/sample_sensor_data.csv",
            "pipeline_dynamics": {}
        }
        validator = InputValidator(config)
        is_valid, msg = validator.validate_all()
        assert is_valid is False
        assert "schema_mapping" in msg

    def test_missing_columns_in_schema(self):
        """Test error when columns missing from schema_mapping."""
        config = {
            "dataset_path": "data/sample_sensor_data.csv",
            "schema_mapping": {},
            "pipeline_dynamics": {}
        }
        validator = InputValidator(config)
        is_valid, msg = validator.validate_all()
        assert is_valid is False
        assert "columns" in msg

    def test_columns_not_list(self):
        """Test error when columns is not a list."""
        config = {
            "dataset_path": "data/sample_sensor_data.csv",
            "schema_mapping": {"columns": "not_a_list"},
            "pipeline_dynamics": {}
        }
        validator = InputValidator(config)
        is_valid, msg = validator.validate_all()
        assert is_valid is False
        assert "must be a list" in msg

    def test_empty_columns(self):
        """Test error when columns list is empty."""
        config = {
            "dataset_path": "data/sample_sensor_data.csv",
            "schema_mapping": {"columns": []},
            "pipeline_dynamics": {}
        }
        validator = InputValidator(config)
        is_valid, msg = validator.validate_all()
        assert is_valid is False
        assert "cannot be empty" in msg

    def test_column_not_dict(self):
        """Test error when column entry is not a dict."""
        config = {
            "dataset_path": "data/sample_sensor_data.csv",
            "schema_mapping": {
                "columns": ["not_a_dict"]
            },
            "pipeline_dynamics": {}
        }
        validator = InputValidator(config)
        is_valid, msg = validator.validate_all()
        assert is_valid is False
        assert "not a dict" in msg

    def test_missing_column_keys(self):
        """Test error when column dict missing required keys."""
        config = {
            "dataset_path": "data/sample_sensor_data.csv",
            "schema_mapping": {
                "columns": [
                    {
                        "source_name": "Col1"
                        # Missing internal_mapping and data_type
                    }
                ]
            },
            "pipeline_dynamics": {}
        }
        validator = InputValidator(config)
        is_valid, msg = validator.validate_all()
        assert is_valid is False
        assert "missing keys" in msg

    def test_invalid_data_type(self):
        """Test error when data_type is invalid."""
        config = {
            "dataset_path": "data/sample_sensor_data.csv",
            "schema_mapping": {
                "columns": [
                    {
                        "source_name": "Col1",
                        "internal_mapping": "col1",
                        "data_type": "invalid_type"
                    }
                ]
            },
            "pipeline_dynamics": {}
        }
        validator = InputValidator(config)
        is_valid, msg = validator.validate_all()
        assert is_valid is False
        assert "invalid data_type" in msg


class TestPipelineDynamicsValidation:
    """Test pipeline_dynamics validation."""

    def test_missing_pipeline_dynamics(self):
        """Test error when pipeline_dynamics missing."""
        config = {
            "dataset_path": "data/sample_sensor_data.csv",
            "schema_mapping": {
                "columns": [
                    {
                        "source_name": "Col1",
                        "internal_mapping": "col1",
                        "data_type": "string"
                    }
                ]
            }
        }
        validator = InputValidator(config)
        is_valid, msg = validator.validate_all()
        assert is_valid is False
        assert "pipeline_dynamics" in msg

    def test_missing_input_delay_seconds(self):
        """Test error when input_delay_seconds missing."""
        config = {
            "dataset_path": "data/sample_sensor_data.csv",
            "schema_mapping": {
                "columns": [
                    {
                        "source_name": "Col1",
                        "internal_mapping": "col1",
                        "data_type": "string"
                    }
                ]
            },
            "pipeline_dynamics": {
                "core_parallelism": 4,
                "stream_queue_max_size": 50
            }
        }
        validator = InputValidator(config)
        is_valid, msg = validator.validate_all()
        assert is_valid is False
        assert "input_delay_seconds" in msg

    def test_invalid_input_delay_seconds_negative(self):
        """Test error when input_delay_seconds is negative."""
        config = {
            "dataset_path": "data/sample_sensor_data.csv",
            "schema_mapping": {
                "columns": [
                    {
                        "source_name": "Col1",
                        "internal_mapping": "col1",
                        "data_type": "string"
                    }
                ]
            },
            "pipeline_dynamics": {
                "input_delay_seconds": -0.5,  # INVALID
                "core_parallelism": 4,
                "stream_queue_max_size": 50
            }
        }
        validator = InputValidator(config)
        is_valid, msg = validator.validate_all()
        assert is_valid is False
        assert "input_delay_seconds" in msg

    def test_invalid_input_delay_seconds_string(self):
        """Test error when input_delay_seconds is not a number."""
        config = {
            "dataset_path": "data/sample_sensor_data.csv",
            "schema_mapping": {
                "columns": [
                    {
                        "source_name": "Col1",
                        "internal_mapping": "col1",
                        "data_type": "string"
                    }
                ]
            },
            "pipeline_dynamics": {
                "input_delay_seconds": "not_a_number",
                "core_parallelism": 4,
                "stream_queue_max_size": 50
            }
        }
        validator = InputValidator(config)
        is_valid, msg = validator.validate_all()
        assert is_valid is False
        assert "input_delay_seconds" in msg

    def test_invalid_core_parallelism_zero(self):
        """Test error when core_parallelism is zero."""
        config = {
            "dataset_path": "data/sample_sensor_data.csv",
            "schema_mapping": {
                "columns": [
                    {
                        "source_name": "Col1",
                        "internal_mapping": "col1",
                        "data_type": "string"
                    }
                ]
            },
            "pipeline_dynamics": {
                "input_delay_seconds": 0.01,
                "core_parallelism": 0,  # INVALID
                "stream_queue_max_size": 50
            }
        }
        validator = InputValidator(config)
        is_valid, msg = validator.validate_all()
        assert is_valid is False
        assert "core_parallelism" in msg

    def test_invalid_stream_queue_max_size_string(self):
        """Test error when stream_queue_max_size is not an integer."""
        config = {
            "dataset_path": "data/sample_sensor_data.csv",
            "schema_mapping": {
                "columns": [
                    {
                        "source_name": "Col1",
                        "internal_mapping": "col1",
                        "data_type": "string"
                    }
                ]
            },
            "pipeline_dynamics": {
                "input_delay_seconds": 0.01,
                "core_parallelism": 4,
                "stream_queue_max_size": "not_an_integer"
            }
        }
        validator = InputValidator(config)
        is_valid, msg = validator.validate_all()
        assert is_valid is False
        assert "stream_queue_max_size" in msg

    def test_valid_pipeline_dynamics(self):
        """Test validation with valid pipeline_dynamics."""
        config = {
            "dataset_path": "data/sample_sensor_data.csv",
            "schema_mapping": {
                "columns": [
                    {
                        "source_name": "Sensor_ID",
                        "internal_mapping": "entity_name",
                        "data_type": "string"
                    }
                ]
            },
            "pipeline_dynamics": {
                "input_delay_seconds": 0.01,
                "core_parallelism": 4,
                "stream_queue_max_size": 50
            }
        }
        validator = InputValidator(config)
        is_valid, msg = validator.validate_all()
        assert is_valid is True


class TestCSVColumnValidation:
    """Test CSV column validation."""

    def test_csv_columns_match(self):
        """Test validation when CSV columns match schema."""
        config = {
            "dataset_path": "data/sample_sensor_data.csv",
            "schema_mapping": {
                "columns": [
                    {
                        "source_name": "Sensor_ID",
                        "internal_mapping": "entity_name",
                        "data_type": "string"
                    },
                    {
                        "source_name": "Timestamp",
                        "internal_mapping": "time_period",
                        "data_type": "integer"
                    },
                    {
                        "source_name": "Raw_Value",
                        "internal_mapping": "metric_value",
                        "data_type": "float"
                    },
                    {
                        "source_name": "Auth_Signature",
                        "internal_mapping": "security_hash",
                        "data_type": "string"
                    }
                ]
            },
            "pipeline_dynamics": {
                "input_delay_seconds": 0.01,
                "core_parallelism": 4,
                "stream_queue_max_size": 50
            }
        }
        validator = InputValidator(config)
        is_valid, msg = validator.validate_all()
        # Should be valid - actual data matches
        assert is_valid is True

    def test_csv_columns_missing(self):
        """Test validation when CSV columns are missing."""
        config = {
            "dataset_path": "data/sample_sensor_data.csv",
            "schema_mapping": {
                "columns": [
                    {
                        "source_name": "Sensor_ID",
                        "internal_mapping": "entity_name",
                        "data_type": "string"
                    },
                    {
                        "source_name": "NonExistentColumn",
                        "internal_mapping": "nonexistent",
                        "data_type": "string"
                    }
                ]
            },
            "pipeline_dynamics": {
                "input_delay_seconds": 0.01,
                "core_parallelism": 4,
                "stream_queue_max_size": 50
            }
        }
        validator = InputValidator(config)
        is_valid, msg = validator.validate_all()
        assert is_valid is False
        assert "missing" in msg.lower()


class TestPrintValidationResult:
    """Test validation result printing."""

    def test_print_valid_result(self, capsys):
        """Test printing valid validation result."""
        exit_code = InputValidator.print_validation_result(True, "Test passed")
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "Test passed" in captured.out

    def test_print_invalid_result(self, capsys):
        """Test printing invalid validation result."""
        exit_code = InputValidator.print_validation_result(False, "Test failed")
        assert exit_code == 2
        captured = capsys.readouterr()
        assert "Test failed" in captured.out
