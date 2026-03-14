"""
Unit tests for plugins/inputs/schema_mapper.py

Tests column name mapping and type casting functionality.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from plugins.inputs.schema_mapper import (
    SchemaMapper, InvalidSchemaError, TypeCastError, ColumnMappingError
)


class TestSchemaMapperInit:
    """Test SchemaMapper initialization and validation."""

    def test_init_valid_schema(self):
        """Test initialization with valid schema."""
        schema = {
            "columns": [
                {
                    "source_name": "Sensor_ID",
                    "internal_mapping": "entity_name",
                    "data_type": "string"
                },
                {
                    "source_name": "Temperature",
                    "internal_mapping": "metric_value",
                    "data_type": "float"
                }
            ]
        }
        mapper = SchemaMapper(schema)
        assert mapper is not None
        assert len(mapper.columns) == 2

    def test_init_columns_not_list(self):
        """Test error when columns is not a list."""
        schema = {"columns": "not_a_list"}
        with pytest.raises(InvalidSchemaError, match="must be a list"):
            SchemaMapper(schema)

    def test_init_empty_columns(self):
        """Test error when columns list is empty."""
        schema = {"columns": []}
        with pytest.raises(InvalidSchemaError, match="cannot be empty"):
            SchemaMapper(schema)

    def test_init_missing_required_keys(self):
        """Test error when column entry missing required keys."""
        schema = {
            "columns": [
                {
                    "source_name": "Sensor_ID",
                    "internal_mapping": "entity_name"
                    # Missing data_type
                }
            ]
        }
        with pytest.raises(InvalidSchemaError, match="missing keys"):
            SchemaMapper(schema)

    def test_init_invalid_data_type(self):
        """Test error when data_type is invalid."""
        schema = {
            "columns": [
                {
                    "source_name": "Sensor_ID",
                    "internal_mapping": "entity_name",
                    "data_type": "invalid_type"
                }
            ]
        }
        with pytest.raises(InvalidSchemaError, match="invalid data_type"):
            SchemaMapper(schema)


class TestSchemaMappingMethods:
    """Test schema mapper utility methods."""

    @pytest.fixture
    def mapper(self):
        """Create mapper with sample schema."""
        schema = {
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
                    "source_name": "Temperature",
                    "internal_mapping": "metric_value",
                    "data_type": "float"
                }
            ]
        }
        return SchemaMapper(schema)

    def test_get_required_source_columns(self, mapper):
        """Test getting required source column names."""
        cols = mapper.get_required_source_columns()
        assert "Sensor_ID" in cols
        assert "Timestamp" in cols
        assert "Temperature" in cols
        assert len(cols) == 3

    def test_get_internal_column_names(self, mapper):
        """Test getting internal column names."""
        cols = mapper.get_internal_column_names()
        assert "entity_name" in cols
        assert "time_period" in cols
        assert "metric_value" in cols
        assert len(cols) == 3

    def test_validate_csv_columns_valid(self, mapper):
        """Test CSV column validation with valid columns."""
        csv_headers = ["Sensor_ID", "Timestamp", "Temperature", "Extra"]
        is_valid, msg = mapper.validate_csv_columns(csv_headers)
        assert is_valid is True
        assert "All required columns" in msg

    def test_validate_csv_columns_missing(self, mapper):
        """Test CSV column validation with missing columns."""
        csv_headers = ["Sensor_ID", "Temperature"]  # Missing Timestamp
        is_valid, msg = mapper.validate_csv_columns(csv_headers)
        assert is_valid is False
        assert "missing columns" in msg


class TestColumnMapping:
    """Test column name mapping."""

    @pytest.fixture
    def mapper(self):
        """Create mapper with sample schema."""
        schema = {
            "columns": [
                {
                    "source_name": "Sensor_ID",
                    "internal_mapping": "entity_name",
                    "data_type": "string"
                },
                {
                    "source_name": "Raw_Value",
                    "internal_mapping": "metric_value",
                    "data_type": "float"
                }
            ]
        }
        return SchemaMapper(schema)

    def test_map_row_basic(self, mapper):
        """Test basic row mapping."""
        raw_row = {
            "Sensor_ID": "Alpha",
            "Raw_Value": "24.99"
        }
        mapped = mapper.map_row(raw_row)
        assert "entity_name" in mapped
        assert "metric_value" in mapped
        assert mapped["entity_name"] == "Alpha"
        assert mapped["metric_value"] == "24.99"

    def test_map_row_missing_column(self, mapper):
        """Test error when required column missing from row."""
        raw_row = {"Sensor_ID": "Alpha"}  # Missing Raw_Value
        with pytest.raises(ColumnMappingError, match="Missing required column"):
            mapper.map_row(raw_row)

    def test_map_row_preserves_extra_columns(self, mapper):
        """Test that extra columns are preserved with _raw_ prefix."""
        raw_row = {
            "Sensor_ID": "Alpha",
            "Raw_Value": "24.99",
            "Extra_Field": "preserved"
        }
        mapped = mapper.map_row(raw_row)
        assert "_raw_Extra_Field" in mapped
        assert mapped["_raw_Extra_Field"] == "preserved"


class TestTypeCasting:
    """Test data type casting."""

    @pytest.fixture
    def mapper(self):
        """Create mapper."""
        schema = {
            "columns": [
                {
                    "source_name": "Name",
                    "internal_mapping": "entity_name",
                    "data_type": "string"
                },
                {
                    "source_name": "Count",
                    "internal_mapping": "count",
                    "data_type": "integer"
                },
                {
                    "source_name": "Value",
                    "internal_mapping": "metric_value",
                    "data_type": "float"
                },
                {
                    "source_name": "Active",
                    "internal_mapping": "is_active",
                    "data_type": "boolean"
                }
            ]
        }
        return SchemaMapper(schema)

    def test_cast_to_string(self, mapper):
        """Test casting to string."""
        result = mapper.cast_type(123, "string")
        assert result == "123"
        assert isinstance(result, str)

    def test_cast_to_integer(self, mapper):
        """Test casting to integer."""
        result = mapper.cast_type("42", "integer")
        assert result == 42
        assert isinstance(result, int)

    def test_cast_float_string_to_integer(self, mapper):
        """Test casting float string like '24.99' to integer."""
        result = mapper.cast_type("24.99", "integer")
        assert result == 24
        assert isinstance(result, int)

    def test_cast_to_float(self, mapper):
        """Test casting to float."""
        result = mapper.cast_type("24.99", "float")
        assert result == 24.99
        assert isinstance(result, float)

    def test_cast_integer_to_float(self, mapper):
        """Test casting integer to float."""
        result = mapper.cast_type(42, "float")
        assert result == 42.0
        assert isinstance(result, float)

    def test_cast_to_boolean_true_variants(self, mapper):
        """Test casting to boolean - true variants."""
        assert mapper.cast_type("true", "boolean") is True
        assert mapper.cast_type("yes", "boolean") is True
        assert mapper.cast_type("1", "boolean") is True
        assert mapper.cast_type("on", "boolean") is True
        assert mapper.cast_type(True, "boolean") is True
        assert mapper.cast_type(1, "boolean") is True

    def test_cast_to_boolean_false_variants(self, mapper):
        """Test casting to boolean - false variants."""
        assert mapper.cast_type("false", "boolean") is False
        assert mapper.cast_type("no", "boolean") is False
        assert mapper.cast_type("0", "boolean") is False
        assert mapper.cast_type("off", "boolean") is False
        assert mapper.cast_type(False, "boolean") is False
        assert mapper.cast_type(0, "boolean") is False

    def test_cast_none_returns_none(self, mapper):
        """Test casting None returns None."""
        assert mapper.cast_type(None, "string") is None
        assert mapper.cast_type(None, "integer") is None
        assert mapper.cast_type(None, "float") is None
        assert mapper.cast_type(None, "boolean") is None

    def test_cast_invalid_integer(self, mapper):
        """Test error when casting invalid integer."""
        with pytest.raises(TypeCastError):
            mapper.cast_type("not_a_number", "integer")

    def test_cast_invalid_float(self, mapper):
        """Test error when casting invalid float."""
        with pytest.raises(TypeCastError):
            mapper.cast_type("not_a_float", "float")

    def test_cast_types_full_row(self, mapper):
        """Test casting all types in a full row."""
        mapped_row = {
            "entity_name": "Sensor_A",
            "count": "42",
            "metric_value": "24.99",
            "is_active": "true"
        }
        cast_row = mapper.cast_types(mapped_row)
        assert cast_row["entity_name"] == "Sensor_A"
        assert cast_row["count"] == 42
        assert cast_row["metric_value"] == 24.99
        assert cast_row["is_active"] is True


class TestProcessRow:
    """Test end-to-end row processing."""

    @pytest.fixture
    def mapper(self):
        """Create mapper with realistic schema."""
        schema = {
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
                }
            ]
        }
        return SchemaMapper(schema)

    def test_process_row_complete(self, mapper):
        """Test complete row processing with mapping and casting."""
        raw_row = {
            "Sensor_ID": "Sensor_Alpha",
            "Timestamp": "1773037623",
            "Raw_Value": "24.99"
        }
        result = mapper.process_row(raw_row)

        # Check structure
        assert "entity_name" in result
        assert "time_period" in result
        assert "metric_value" in result

        # Check types
        assert isinstance(result["entity_name"], str)
        assert isinstance(result["time_period"], int)
        assert isinstance(result["metric_value"], float)

        # Check values
        assert result["entity_name"] == "Sensor_Alpha"
        assert result["time_period"] == 1773037623
        assert result["metric_value"] == 24.99

    def test_process_row_multiple_rows(self, mapper):
        """Test processing multiple rows."""
        rows = [
            {
                "Sensor_ID": "Sensor_A",
                "Timestamp": "1000",
                "Raw_Value": "10.5"
            },
            {
                "Sensor_ID": "Sensor_B",
                "Timestamp": "2000",
                "Raw_Value": "20.5"
            },
            {
                "Sensor_ID": "Sensor_C",
                "Timestamp": "3000",
                "Raw_Value": "30.5"
            }
        ]

        results = [mapper.process_row(row) for row in rows]

        assert len(results) == 3
        assert results[0]["entity_name"] == "Sensor_A"
        assert results[1]["entity_name"] == "Sensor_B"
        assert results[2]["entity_name"] == "Sensor_C"
        assert all(isinstance(r["time_period"], int) for r in results)


class TestSchemaSummary:
    """Test schema summary functionality."""

    def test_get_schema_summary(self):
        """Test schema summary formatting."""
        schema = {
            "columns": [
                {
                    "source_name": "Sensor_ID",
                    "internal_mapping": "entity_name",
                    "data_type": "string"
                },
                {
                    "source_name": "Temperature",
                    "internal_mapping": "metric_value",
                    "data_type": "float"
                }
            ]
        }
        mapper = SchemaMapper(schema)
        summary = mapper.get_schema_summary()

        assert "Schema Mapping Summary" in summary
        assert "Sensor_ID" in summary
        assert "entity_name" in summary
        assert "Temperature" in summary
        assert "metric_value" in summary
