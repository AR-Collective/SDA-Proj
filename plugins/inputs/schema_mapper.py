"""
Schema Mapper for Phase 3 - Generic Column Mapping & Type Casting

This module provides a SchemaMapper class that dynamically maps CSV column names
to internal generic variable names and performs type casting based on a schema
defined in config.json.

The mapper makes the system domain-agnostic: the same code works with any CSV
as long as the schema_mapping in config.json is updated.

Example:
    CSV Input: {Sensor_ID: "Alpha", Timestamp: "1234", Raw_Value: "24.99", ...}

    After mapping: {entity_name: "Alpha", time_period: 1234, metric_value: 24.99, ...}

This allows the core module to work with ANY dataset without code changes.
"""

from typing import Dict, Any, List, Tuple
from pathlib import Path
import sys


class SchemaMapperError(Exception):
    """Base exception for schema mapping errors."""
    pass


class InvalidSchemaError(SchemaMapperError):
    """Raised when schema structure is invalid."""
    pass


class TypeCastError(SchemaMapperError):
    """Raised when type casting fails."""
    pass


class ColumnMappingError(SchemaMapperError):
    """Raised when column mapping fails."""
    pass


class SchemaMapper:
    """
    Maps CSV column names to internal generic names and casts data types.

    This class makes the pipeline generic - it can work with ANY CSV schema
    by reading the column mappings from config.json.

    Supported data types: string, integer, float, boolean
    """

    def __init__(self, schema_config: Dict[str, Any]):
        """
        Initialize schema mapper with config.

        Args:
            schema_config: The 'schema_mapping' dict from config.json with structure:
                {
                    "columns": [
                        {
                            "source_name": "CSV_Column",
                            "internal_mapping": "generic_name",
                            "data_type": "string|integer|float|boolean"
                        },
                        ...
                    ]
                }

        Raises:
            InvalidSchemaError: If schema structure is invalid
        """
        self.schema_config = schema_config
        self.columns = schema_config.get("columns", [])

        # Build lookup dictionaries for fast access
        self._source_to_internal = {}  # CSV column name → internal name
        self._source_to_type = {}      # CSV column name → data type
        self._internal_names = set()   # All internal names (for validation)

        self._validate_schema_structure()
        self._build_mappings()

    def _validate_schema_structure(self) -> None:
        """
        Validate that schema has correct structure.

        Raises:
            InvalidSchemaError: If schema is malformed
        """
        if not isinstance(self.columns, list):
            raise InvalidSchemaError("schema_mapping.columns must be a list")

        if len(self.columns) == 0:
            raise InvalidSchemaError("schema_mapping.columns cannot be empty")

        for i, col in enumerate(self.columns):
            if not isinstance(col, dict):
                raise InvalidSchemaError(f"Column {i} is not a dict")

            required_keys = {"source_name", "internal_mapping", "data_type"}
            missing_keys = required_keys - set(col.keys())

            if missing_keys:
                raise InvalidSchemaError(
                    f"Column {i} missing keys: {missing_keys}"
                )

            if col["data_type"] not in {"string", "integer", "float", "boolean"}:
                raise InvalidSchemaError(
                    f"Column {i}: invalid data_type '{col['data_type']}'. "
                    f"Must be: string, integer, float, or boolean"
                )

    def _build_mappings(self) -> None:
        """Build internal lookup dictionaries from schema."""
        for col in self.columns:
            source = col["source_name"]
            internal = col["internal_mapping"]
            dtype = col["data_type"]

            self._source_to_internal[source] = internal
            self._source_to_type[source] = dtype
            self._internal_names.add(internal)

    def get_required_source_columns(self) -> List[str]:
        """
        Get list of CSV column names required by schema.

        Returns:
            List of source column names that must exist in CSV
        """
        return list(self._source_to_internal.keys())

    def get_internal_column_names(self) -> List[str]:
        """
        Get list of internal (generic) column names after mapping.

        Returns:
            List of internal column names
        """
        return list(self._internal_names)

    def validate_csv_columns(self, csv_headers: List[str]) -> Tuple[bool, str]:
        """
        Validate that CSV has all required columns.

        Args:
            csv_headers: List of column names from CSV header row

        Returns:
            Tuple of (is_valid: bool, message: str)
        """
        required = set(self.get_required_source_columns())
        available = set(csv_headers)

        missing = required - available
        if missing:
            return False, f"CSV missing columns: {missing}"

        return True, "All required columns present"

    def map_row(self, raw_row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map a raw row from CSV to internal schema.

        Takes a dict with CSV column names as keys and maps them to
        internal generic names without type casting.

        Args:
            raw_row: Dict with CSV column names as keys

        Returns:
            Dict with internal column names as keys, values still raw

        Raises:
            ColumnMappingError: If required columns are missing from row
        """
        mapped_row = {}

        for source_col, internal_col in self._source_to_internal.items():
            if source_col not in raw_row:
                raise ColumnMappingError(
                    f"Missing required column in row: '{source_col}'"
                )

            mapped_row[internal_col] = raw_row[source_col]

        # Copy any extra columns from raw_row (for debugging/metadata)
        for key, value in raw_row.items():
            if key not in self._source_to_internal:
                mapped_row[f"_raw_{key}"] = value

        return mapped_row

    def cast_type(self, value: Any, data_type: str) -> Any:
        """
        Cast a single value to the specified data type.

        Args:
            value: The value to cast
            data_type: Target type: "string", "integer", "float", or "boolean"

        Returns:
            Value cast to specified type

        Raises:
            TypeCastError: If casting fails
        """
        if value is None:
            return None

        try:
            if data_type == "string":
                return str(value)

            elif data_type == "integer":
                # Handle float strings like "24.99" → convert to int
                if isinstance(value, str):
                    # Try float first to handle "24.99" → 24
                    return int(float(value))
                return int(value)

            elif data_type == "float":
                return float(value)

            elif data_type == "boolean":
                if isinstance(value, bool):
                    return value
                if isinstance(value, str):
                    return value.lower() in {"true", "yes", "1", "on"}
                return bool(value)

            else:
                raise TypeCastError(f"Unknown data type: {data_type}")

        except (ValueError, TypeError) as e:
            raise TypeCastError(
                f"Cannot cast '{value}' to {data_type}: {str(e)}"
            )

    def cast_types(self, mapped_row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cast all values in a mapped row to their correct types.

        Args:
            mapped_row: Dict with internal column names (from map_row())

        Returns:
            Dict with all values cast to correct types

        Raises:
            TypeCastError: If any casting fails
        """
        cast_row = {}

        for source_col, internal_col in self._source_to_internal.items():
            if internal_col not in mapped_row:
                raise TypeCastError(f"Missing column after mapping: {internal_col}")

            raw_value = mapped_row[internal_col]
            target_type = self._source_to_type[source_col]

            cast_value = self.cast_type(raw_value, target_type)
            cast_row[internal_col] = cast_value

        # Copy over any extra/metadata columns (with _raw_ prefix)
        for key, value in mapped_row.items():
            if key not in cast_row:
                cast_row[key] = value

        return cast_row

    def process_row(self, raw_row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a raw row: map columns AND cast types in one call.

        This is the main method to use - it does both mapping and casting.

        Args:
            raw_row: Dict with CSV column names as keys

        Returns:
            Dict with internal column names as keys and correct types

        Raises:
            ColumnMappingError: If mapping fails
            TypeCastError: If type casting fails
        """
        mapped = self.map_row(raw_row)
        return self.cast_types(mapped)

    def get_schema_summary(self) -> str:
        """
        Get a human-readable summary of the schema mapping.

        Returns:
            Formatted string describing the schema
        """
        lines = ["Schema Mapping Summary:"]
        lines.append("-" * 60)

        for col in self.columns:
            source = col["source_name"]
            internal = col["internal_mapping"]
            dtype = col["data_type"]
            lines.append(f"  {source:20} → {internal:20} ({dtype})")

        lines.append("-" * 60)
        return "\n".join(lines)


def load_schema_from_config(config_dict: Dict[str, Any]) -> SchemaMapper:
    """
    Convenience function to load SchemaMapper from config dict.

    Args:
        config_dict: The full config.json as dict

    Returns:
        SchemaMapper instance

    Raises:
        InvalidSchemaError: If schema_mapping is missing or invalid
    """
    if "schema_mapping" not in config_dict:
        raise InvalidSchemaError("config.json missing 'schema_mapping' key")

    return SchemaMapper(config_dict["schema_mapping"])


