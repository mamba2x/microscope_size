from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from microscope_core import CalculationResult


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("MICROSCOPE_DATA_DIR", BASE_DIR))
DB_PATH = DATA_DIR / "microscope_calculations.db"


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    ensure_data_dir()
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS calculations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                image_path TEXT NOT NULL,
                measured_size_mm REAL NOT NULL,
                microscope_type TEXT NOT NULL,
                magnification_factor INTEGER NOT NULL,
                real_size_mm REAL NOT NULL,
                output_unit TEXT NOT NULL,
                output_value REAL NOT NULL,
                breakdown TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()


def save_calculation(result: CalculationResult) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO calculations (
                username,
                image_path,
                measured_size_mm,
                microscope_type,
                magnification_factor,
                real_size_mm,
                output_unit,
                output_value,
                breakdown
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                result.username,
                result.image_path,
                result.measured_size_mm,
                result.microscope_type,
                result.magnification_factor,
                result.real_size_mm,
                result.output_unit,
                result.output_value,
                result.breakdown,
            ),
        )
        connection.commit()


def fetch_calculations() -> list[sqlite3.Row]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, username, image_path, measured_size_mm, microscope_type,
                   magnification_factor, real_size_mm, output_unit, output_value,
                   breakdown, created_at
            FROM calculations
            ORDER BY created_at DESC, id DESC
            """
        ).fetchall()
    return rows


def delete_calculation(record_id: int) -> None:
    with get_connection() as connection:
        connection.execute("DELETE FROM calculations WHERE id = ?", (record_id,))
        connection.commit()


def clear_calculations() -> None:
    with get_connection() as connection:
        connection.execute("DELETE FROM calculations")
        connection.commit()
