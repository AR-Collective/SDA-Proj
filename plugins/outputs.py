from typing import Any, List
import pandas as pd


class ConsoleWriter:
    """
    Writes data to the console in a formatted way.
    Implements the DataSink protocol from core/contracts.py
    """

    def write(self, records: Any) -> None:
        """
        Write records to console with nice formatting.
        Handles both dict with DataFrames and List[dict].

        Args:
            records: Data to write (can be dict with DataFrames or List[dict])
        """
        if isinstance(records, dict):
            self._write_dict(records)
        elif isinstance(records, list):
            self._write_list(records)
        else:
            print(f"DEBUG: {records}")

    def _write_dict(self, data: dict) -> None:
        """Write dictionary containing DataFrames or other data."""
        for key, value in data.items():
            print(f"\n{'='*60}")
            print(f"  {key}")
            print(f"{'='*60}")

            if isinstance(value, pd.DataFrame):
                print(value.to_string())
            else:
                print(value)

    def _write_list(self, records: List[dict]) -> None:
        """Write list of dictionaries (records)."""
        print(f"\n{'='*60}")
        print(f"  Records ({len(records)} items)")
        print(f"{'='*60}")

        for i, record in enumerate(records, 1):
            print(f"\n[Record {i}]")
            for key, value in record.items():
                print(f"  {key}: {value}")
