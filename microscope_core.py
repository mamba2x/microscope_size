from __future__ import annotations

from dataclasses import dataclass


MICROSCOPE_TYPES = {
    "Compound Microscope (40x)": 40,
    "Compound Microscope (100x)": 100,
    "Compound Microscope (400x)": 400,
    "Stereo Microscope (20x)": 20,
    "Electron Microscope (1000x)": 1000,
}

UNIT_FACTORS_FROM_MM = {
    "nm": 1_000_000.0,
    "um": 1_000.0,
    "mm": 1.0,
    "cm": 0.1,
    "m": 0.001,
}

UNIT_LABELS = {
    "nm": "nm",
    "um": "um",
    "mm": "mm",
    "cm": "cm",
    "m": "m",
}


@dataclass
class CalculationResult:
    username: str
    image_path: str
    measured_size_mm: float
    microscope_type: str
    magnification_factor: int
    real_size_mm: float
    output_unit: str
    output_value: float
    breakdown: str


def validate_username(username: str) -> str:
    cleaned = username.strip()
    if not cleaned:
        raise ValueError("Username is required.")
    return cleaned


def validate_measured_size(value: str | float | int) -> float:
    try:
        measured = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Measured specimen size must be a number.") from exc

    if measured <= 0:
        raise ValueError("Measured specimen size must be greater than zero.")

    return measured


def validate_microscope_type(microscope_type: str) -> str:
    if microscope_type not in MICROSCOPE_TYPES:
        raise ValueError("Please choose a microscope type from the list.")
    return microscope_type


def validate_output_unit(output_unit: str) -> str:
    if output_unit not in UNIT_FACTORS_FROM_MM:
        raise ValueError("Please choose a supported output unit.")
    return output_unit


def convert_from_mm(value_mm: float, output_unit: str) -> float:
    validate_output_unit(output_unit)
    return value_mm * UNIT_FACTORS_FROM_MM[output_unit]


def build_breakdown(
    measured_size_mm: float,
    microscope_type: str,
    magnification_factor: int,
    real_size_mm: float,
    output_value: float,
    output_unit: str,
) -> str:
    unit_label = UNIT_LABELS[output_unit]
    return (
        "Real Size = Measured Size / Magnification Factor\n"
        f"Real Size = {measured_size_mm:.6f} mm / {magnification_factor}\n"
        f"Real Size = {real_size_mm:.6f} mm\n"
        f"Converted Result = {real_size_mm:.6f} mm x {UNIT_FACTORS_FROM_MM[output_unit]:,.6f}\n"
        f"Final Answer = {output_value:.6f} {unit_label}\n"
        f"Microscope Type = {microscope_type}"
    )


def calculate_specimen_size(
    username: str,
    image_path: str,
    measured_size_mm: str | float | int,
    microscope_type: str,
    output_unit: str,
) -> CalculationResult:
    cleaned_username = validate_username(username)
    measured_value = validate_measured_size(measured_size_mm)
    cleaned_microscope_type = validate_microscope_type(microscope_type)
    cleaned_output_unit = validate_output_unit(output_unit)

    magnification_factor = MICROSCOPE_TYPES[cleaned_microscope_type]
    real_size_mm = measured_value / magnification_factor
    output_value = convert_from_mm(real_size_mm, cleaned_output_unit)
    breakdown = build_breakdown(
        measured_value,
        cleaned_microscope_type,
        magnification_factor,
        real_size_mm,
        output_value,
        cleaned_output_unit,
    )

    return CalculationResult(
        username=cleaned_username,
        image_path=image_path,
        measured_size_mm=measured_value,
        microscope_type=cleaned_microscope_type,
        magnification_factor=magnification_factor,
        real_size_mm=real_size_mm,
        output_unit=cleaned_output_unit,
        output_value=output_value,
        breakdown=breakdown,
    )
