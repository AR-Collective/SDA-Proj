"""
Unit tests for plugins/inputs/generic_producer.py

Tests data production, queueing, and packet processing.
"""

import pytest
import sys
import time
import json
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from plugins.inputs.generic_producer import GenericInputProducer, ProducerError


class TestProducerInit:
    """Test GenericInputProducer initialization."""

    @pytest.fixture
    def valid_config(self):
        """Load valid config from project."""
        with open("config.json") as f:
            return json.load(f)

    def test_init_valid_config(self, valid_config):
        """Test initialization with valid config."""
        producer = GenericInputProducer(valid_config, None)
        assert producer is not None
        assert producer.dataset_path == valid_config["dataset_path"]
        assert producer.input_delay_seconds == 0.01

    def test_init_invalid_config_missing_dataset(self):
        """Test error when dataset_path missing."""
        config = {
            "schema_mapping": {"columns": []},
            "pipeline_dynamics": {}
        }
        with pytest.raises(ProducerError):
            GenericInputProducer(config, None)

    def test_init_invalid_config_bad_schema(self):
        """Test error when schema_mapping invalid."""
        config = {
            "dataset_path": "data/sample_sensor_data.csv",
            "schema_mapping": {"columns": []},
            "pipeline_dynamics": {
                "input_delay_seconds": 0.01,
                "core_parallelism": 4,
                "stream_queue_max_size": 50
            }
        }
        with pytest.raises(ProducerError):
            GenericInputProducer(config, None)

    def test_schema_mapper_initialized(self, valid_config):
        """Test that schema mapper is properly initialized."""
        producer = GenericInputProducer(valid_config, None)
        assert producer.schema_mapper is not None
        assert len(producer.schema_mapper.columns) == 4


class TestCSVReading:
    """Test CSV row reading functionality."""

    @pytest.fixture
    def valid_config(self):
        """Load valid config from project."""
        with open("config.json") as f:
            return json.load(f)

    @pytest.fixture
    def producer(self, valid_config):
        """Create producer instance."""
        return GenericInputProducer(valid_config, None)

    def test_read_csv_rows(self, producer):
        """Test reading CSV rows."""
        rows = list(producer._read_csv_rows())
        assert len(rows) > 0
        assert "Sensor_ID" in rows[0]
        assert "Timestamp" in rows[0]
        assert "Raw_Value" in rows[0]

    def test_read_csv_columns(self, producer):
        """Test that CSV columns are read correctly."""
        rows = list(producer._read_csv_rows())
        first_row = rows[0]
        assert "Sensor_ID" in first_row
        assert "Timestamp" in first_row
        assert "Raw_Value" in first_row
        assert "Auth_Signature" in first_row

    def test_read_csv_all_rows_have_columns(self, producer):
        """Test that all rows have all required columns."""
        rows = list(producer._read_csv_rows())
        required_cols = {"Sensor_ID", "Timestamp", "Raw_Value", "Auth_Signature"}
        for i, row in enumerate(rows):
            assert required_cols.issubset(set(row.keys())), f"Row {i} missing columns"


class TestRowProcessing:
    """Test row processing (mapping + casting)."""

    @pytest.fixture
    def valid_config(self):
        """Load valid config from project."""
        with open("config.json") as f:
            return json.load(f)

    @pytest.fixture
    def producer(self, valid_config):
        """Create producer instance."""
        return GenericInputProducer(valid_config, None)

    def test_process_row_basic(self, producer):
        """Test processing a single row."""
        raw_row = {
            "Sensor_ID": "Sensor_Alpha",
            "Timestamp": "1773037623",
            "Raw_Value": "24.99",
            "Auth_Signature": "abc123"
        }
        packet = producer._process_row(raw_row, 1)
        assert packet is not None
        assert packet["entity_name"] == "Sensor_Alpha"
        assert packet["time_period"] == 1773037623
        assert packet["metric_value"] == 24.99
        assert packet["security_hash"] == "abc123"

    def test_process_row_types(self, producer):
        """Test that processed row has correct types."""
        raw_row = {
            "Sensor_ID": "Alpha",
            "Timestamp": "1000",
            "Raw_Value": "10.5",
            "Auth_Signature": "sig"
        }
        packet = producer._process_row(raw_row, 1)
        assert isinstance(packet["entity_name"], str)
        assert isinstance(packet["time_period"], int)
        assert isinstance(packet["metric_value"], float)
        assert isinstance(packet["security_hash"], str)

    def test_process_row_metadata(self, producer):
        """Test that metadata is added to packet."""
        raw_row = {
            "Sensor_ID": "Alpha",
            "Timestamp": "1000",
            "Raw_Value": "10.5",
            "Auth_Signature": "sig"
        }
        packet = producer._process_row(raw_row, 42)
        assert "_source_row" in packet
        assert packet["_source_row"] == 42
        assert "_producer_timestamp" in packet

    def test_process_row_invalid_data(self, producer):
        """Test error handling for invalid data."""
        raw_row = {
            "Sensor_ID": "Alpha",
            "Timestamp": "not_a_number",  # Invalid
            "Raw_Value": "10.5",
            "Auth_Signature": "sig"
        }
        packet = producer._process_row(raw_row, 1)
        # Should return None on error
        assert packet is None


class TestBatchProcessing:
    """Test batch processing mode."""

    @pytest.fixture
    def valid_config(self):
        """Load valid config from project."""
        with open("config.json") as f:
            return json.load(f)

    @pytest.fixture
    def producer(self, valid_config):
        """Create producer instance."""
        return GenericInputProducer(valid_config, None)

    def test_run_single_batch_default(self, producer):
        """Test batch processing with default size."""
        packets = producer.run_single_batch(batch_size=5)
        assert len(packets) == 5
        assert all("entity_name" in p for p in packets)
        assert all("metric_value" in p for p in packets)

    def test_run_single_batch_small(self, producer):
        """Test batch processing with small batch."""
        packets = producer.run_single_batch(batch_size=3)
        assert len(packets) == 3

    def test_run_single_batch_large(self, producer):
        """Test batch processing with large batch."""
        packets = producer.run_single_batch(batch_size=50)
        # File has 200 rows, so we should get 50
        assert len(packets) == 50

    def test_run_single_batch_packets_valid(self, producer):
        """Test that batched packets are properly formatted."""
        packets = producer.run_single_batch(batch_size=10)
        for packet in packets:
            assert "entity_name" in packet
            assert "time_period" in packet
            assert "metric_value" in packet
            assert "security_hash" in packet
            assert "_source_row" in packet
            assert "_producer_timestamp" in packet


class TestThrottling:
    """Test input delay throttling."""

    @pytest.fixture
    def valid_config(self):
        """Load valid config from project."""
        with open("config.json") as f:
            return json.load(f)

    @pytest.fixture
    def producer(self, valid_config):
        """Create producer instance."""
        return GenericInputProducer(valid_config, None)

    def test_apply_throttle_no_delay(self, producer):
        """Test throttling with zero delay."""
        producer.input_delay_seconds = 0
        start = time.time()
        producer._apply_throttle()
        elapsed = time.time() - start
        assert elapsed < 0.1  # Should be nearly instant

    def test_apply_throttle_with_delay(self, producer):
        """Test throttling with delay."""
        producer.input_delay_seconds = 0.1
        start = time.time()
        producer._apply_throttle()
        elapsed = time.time() - start
        assert elapsed >= 0.08  # Allow some tolerance


class TestProducerIntegration:
    """Integration tests for producer."""

    @pytest.fixture
    def valid_config(self):
        """Load valid config from project."""
        with open("config.json") as f:
            return json.load(f)

    def test_producer_creation_and_batch(self, valid_config):
        """Test creating producer and processing batch."""
        producer = GenericInputProducer(valid_config, None)
        packets = producer.run_single_batch(batch_size=10)

        assert len(packets) == 10
        # Verify each packet
        for i, packet in enumerate(packets):
            assert isinstance(packet, dict)
            assert "entity_name" in packet
            assert isinstance(packet["entity_name"], str)
            assert isinstance(packet["time_period"], int)
            assert isinstance(packet["metric_value"], float)

    def test_producer_multiple_batches(self, valid_config):
        """Test processing multiple batches in sequence."""
        producer = GenericInputProducer(valid_config, None)

        batch1 = producer.run_single_batch(batch_size=10)
        assert len(batch1) == 10

        # Create new producer to read from start again
        producer2 = GenericInputProducer(valid_config, None)
        batch2 = producer2.run_single_batch(batch_size=10)
        assert len(batch2) == 10

        # Batches should have same data (reading same CSV from start)
        assert batch1[0]["entity_name"] == batch2[0]["entity_name"]


class TestProducerErrorHandling:
    """Test error handling in producer."""

    def test_producer_error_on_bad_queue(self):
        """Test that proper error is raised on queue issues."""
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

        # Create producer with None queue - should fail when trying to queue
        producer = GenericInputProducer(config, None)
        raw_row = {
            "Sensor_ID": "Alpha",
            "Timestamp": "1000",
            "Raw_Value": "10.5",
            "Auth_Signature": "sig"
        }
        packet = producer._process_row(raw_row, 1)

        # Trying to queue with None should raise error
        with pytest.raises(ProducerError):
            producer._queue_packet(packet, 1)
