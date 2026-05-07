from __future__ import annotations

from database import clear_calculations, delete_calculation, fetch_calculations, init_db, save_calculation
from microscope_core import MICROSCOPE_TYPES, UNIT_LABELS, calculate_specimen_size


def prompt_choice(prompt: str, options: list[str]) -> str:
    print(prompt)
    for index, option in enumerate(options, start=1):
        print(f"{index}. {option}")

    while True:
        choice = input("Enter your choice number: ").strip()
        if choice.isdigit():
            position = int(choice) - 1
            if 0 <= position < len(options):
                return options[position]
        print("Invalid choice. Please try again.")


def display_history() -> None:
    rows = fetch_calculations()
    if not rows:
        print("No saved calculations found.")
        return

    print("\nSaved calculations:")
    for row in rows:
        print(
            f"[{row['id']}] {row['created_at']} | {row['username']} | "
            f"{row['measured_size_mm']:.4f} mm -> {row['output_value']:.6f} {UNIT_LABELS[row['output_unit']]}"
        )


def manage_history() -> None:
    while True:
        print("\nHistory Menu")
        print("1. View saved records")
        print("2. Delete one record")
        print("3. Delete all records")
        print("4. Back")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            display_history()
        elif choice == "2":
            display_history()
            record_id = input("Enter the record ID to delete: ").strip()
            if record_id.isdigit():
                delete_calculation(int(record_id))
                print("Record deleted.")
            else:
                print("Please enter a valid numeric ID.")
        elif choice == "3":
            confirm = input("Type YES to delete all records: ").strip()
            if confirm == "YES":
                clear_calculations()
                print("All records deleted.")
            else:
                print("Deletion cancelled.")
        elif choice == "4":
            return
        else:
            print("Invalid choice. Please try again.")


def perform_calculation() -> None:
    username = input("Enter username: ").strip()
    image_path = input("Enter specimen image path: ").strip()
    measured_size_mm = input("Enter measured specimen size in mm: ").strip()
    microscope_type = prompt_choice("Select microscope type:", list(MICROSCOPE_TYPES))
    output_unit = prompt_choice("Select output unit:", list(UNIT_LABELS))

    try:
        result = calculate_specimen_size(
            username=username,
            image_path=image_path,
            measured_size_mm=measured_size_mm,
            microscope_type=microscope_type,
            output_unit=output_unit,
        )
    except ValueError as exc:
        print(f"Error: {exc}")
        return

    save_calculation(result)

    print("\nCalculation Result")
    print(f"Username: {result.username}")
    print(f"Measured Size: {result.measured_size_mm:.6f} mm")
    print(f"Microscope Type: {result.microscope_type}")
    print(f"Magnification Factor: {result.magnification_factor}x")
    print(f"Actual Size: {result.output_value:.6f} {UNIT_LABELS[result.output_unit]}")
    print("\nBreakdown")
    print(result.breakdown)


def main() -> None:
    init_db()

    while True:
        print("\nMicroscope Specimen Size Calculator")
        print("1. New calculation")
        print("2. Manage saved records")
        print("3. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            perform_calculation()
        elif choice == "2":
            manage_history()
        elif choice == "3":
            print("Goodbye.")
            return
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
