"""
Phase 3 Input Module

Provides a generic, domain-agnostic input producer that:
1. Reads CSV files with arbitrary column names
2. Maps CSV columns to internal generic names via schema_mapping
3. Casts data types according to the schema
4. Validates configuration before processing
5. Queues processed packets for the core module

All behavior is driven by config.json - same code works with ANY CSV dataset.
"""

from .schema_mapper import SchemaMapper, InvalidSchemaError, TypeCastError, ColumnMappingError
from .input_validator import InputValidator, InputValidatorError, validate_input_config
from .generic_producer import GenericInputProducer, ProducerError

__all__ = [
    'SchemaMapper',
    'InvalidSchemaError',
    'TypeCastError',
    'ColumnMappingError',
    'InputValidator',
    'InputValidatorError',
    'validate_input_config',
    'GenericInputProducer',
    'ProducerError',
]
