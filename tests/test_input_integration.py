"""
Integration tests for Input Module

Tests the complete input module flow: config validation → schema mapping → production.
"""

import pytest
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from plugins.inputs.schema_mapper import SchemaMapper
from plugins.inputs.input_validator import InputValidator
from plugins.inputs.generic_producer import GenericInputProducer


class TestInputModuleIntegration:
    """Integration tests for complete input module."""

    @pytest.fixture
    def config(self):
        """Load config from project."""
        with open("config.json") as f:
            return json.load(f)

    def test_config_validation_passes(self, config):
        """Test that config validates successfully."""
        validator = InputValidator(config)
        is_valid, msg = validator.validate_all()
        assert is_valid is True
        assert "passed" in msg.lower()

    def test_schema_mapper_from_config(self, config):
        """Test creating schema mapper from config."""
        schema = config["schema_mapping"]
        mapper = SchemaMapper(schema)
        assert len(mapper.columns) == 4
        assert "entity_name" in mapper.get_internal_column_names()

    def test_producer_from_config(self, config):
        """Test creating producer from config."""
        producer = GenericInputProducer(config, None)
        assert producer is not None
        assert producer.schema_mapper is not None

    def test_full_pipeline_config_to_packets(self, config):
        """Test complete pipeline: config → validation → mapper → producer → packets."""
        # 1. Validate config
        validator = InputValidator(config)
        is_valid, msg = validator.validate_all()
        assert is_valid is True

        # 2. Create producer (validates internally)
        producer = GenericInputProducer(config, None)
        assert producer is not None

        # 3. Process batch
        packets = producer.run_single_batch(batch_size=5)
        assert len(packets) == 5

        # 4. Verify packets have correct structure
        for packet in packets:
            # All required internal fields present
            assert "entity_name" in packet
            assert "time_period" in packet
            assert "metric_value" in packet
            assert "security_hash" in packet

            # Correct types
            assert isinstance(packet["entity_name"], str)
            assert isinstance(packet["time_period"], int)
            assert isinstance(packet["metric_value"], float)
            assert isinstance(packet["security_hash"], str)

    def test_config_driven_mapping(self, config):
        """Test that schema mapping is fully config-driven."""
        # Extract schema from config
        schema = config["schema_mapping"]
        mapper = SchemaMapper(schema)

        # Verify mapping matches config
        internal_names = mapper.get_internal_column_names()
        for col in schema["columns"]:
            assert col["internal_mapping"] in internal_names

    def test_multiple_datasets_same_schema(self, config):
        """Test that producer works with configured dataset."""
        # Producer should work with dataset_path from config
        producer = GenericInputProducer(config, None)
        packets = producer.run_single_batch(batch_size=5)

        # All packets should have entity_name from Sensor_ID
        assert all("entity_name" in p for p in packets)
        # All should have values from the CSV
        assert all(p["entity_name"] in ["Sensor_Alpha", "Sensor_Beta"] for p in packets)

    def test_dataset_path_from_config(self, config):
        """Test that dataset_path is read from config."""
        expected_path = config["dataset_path"]
        producer = GenericInputProducer(config, None)
        assert producer.dataset_path == expected_path

    def test_throttling_from_config(self, config):
        """Test that throttling reads from config."""
        expected_delay = config["pipeline_dynamics"]["input_delay_seconds"]
        producer = GenericInputProducer(config, None)
        assert producer.input_delay_seconds == expected_delay

    def test_queue_size_from_config(self, config):
        """Test that queue size reads from config."""
        expected_size = config["pipeline_dynamics"]["stream_queue_max_size"]
        producer = GenericInputProducer(config, None)
        assert producer.queue_max_size == expected_size

    def test_parallelism_config_available(self, config):
        """Test that core_parallelism is available in config."""
        parallelism = config["pipeline_dynamics"]["core_parallelism"]
        assert parallelism > 0
        assert isinstance(parallelism, int)

    def test_packet_structure_consistency(self, config):
        """Test that all packets have consistent structure."""
        producer = GenericInputProducer(config, None)
        packets = producer.run_single_batch(batch_size=20)

        # All packets should have same keys (except metadata)
        required_keys = {"entity_name", "time_period", "metric_value", "security_hash", "_source_row", "_producer_timestamp"}

        for packet in packets:
            assert required_keys.issubset(set(packet.keys()))

    def test_config_changes_behavior(self):
        """Test that changing config changes producer behavior."""
        with open("config.json") as f:
            config1 = json.load(f)

        # Create producer with original config
        producer1 = GenericInputProducer(config1, None)
        original_delay = producer1.input_delay_seconds

        # Create modified config
        config2 = config1.copy()
        config2["pipeline_dynamics"] = config1["pipeline_dynamics"].copy()
        config2["pipeline_dynamics"]["input_delay_seconds"] = original_delay * 2

        # Create producer with modified config
        producer2 = GenericInputProducer(config2, None)
        modified_delay = producer2.input_delay_seconds

        # Should be different
        assert modified_delay == original_delay * 2

    def test_error_in_config_propagates(self):
        """Test that config errors are caught early."""
        bad_config = {
            "dataset_path": "nonexistent.csv",
            "schema_mapping": {"columns": []},
            "pipeline_dynamics": {}
        }

        # Should raise error during validation (before producer setup)
        with pytest.raises(Exception):
            GenericInputProducer(bad_config, None)

    def test_complete_flow_produces_valid_packets(self, config):
        """Test complete flow produces packets valid for core module."""
        producer = GenericInputProducer(config, None)
        packets = producer.run_single_batch(batch_size=10)

        # Verify packets are "core-ready"
        for packet in packets:
            # Core module expects these fields
            assert "entity_name" in packet
            assert "time_period" in packet
            assert "metric_value" in packet
            assert "security_hash" in packet

            # Correct types for core processing
            assert isinstance(packet["entity_name"], str)
            assert isinstance(packet["time_period"], int)
            assert isinstance(packet["metric_value"], float)
            assert isinstance(packet["security_hash"], str)

            # Metadata for tracing
            assert "_source_row" in packet
            assert "_producer_timestamp" in packet

            # Ready for crypto verification (core's first step)
            assert packet["metric_value"] > 0
            assert len(packet["security_hash"]) > 0
