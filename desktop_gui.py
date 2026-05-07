from __future__ import annotations

from pathlib import Path
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

from database import clear_calculations, delete_calculation, fetch_calculations, init_db, save_calculation
from microscope_core import MICROSCOPE_TYPES, UNIT_LABELS, calculate_specimen_size


UPLOADS_DIR = Path("uploads")


class MicroscopeApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        init_db()
        UPLOADS_DIR.mkdir(exist_ok=True)

        self.title("Microscope Specimen Size Calculator")
        self.geometry("1200x760")
        self.configure(bg="#f3f6fb")

        self.selected_image_source = ""
        self.preview_image = None

        self.username_var = tk.StringVar()
        self.measured_size_var = tk.StringVar()
        self.microscope_var = tk.StringVar(value=list(MICROSCOPE_TYPES)[0])
        self.unit_var = tk.StringVar(value="um")
        self.result_var = tk.StringVar(value="Result will appear here.")

        self._build_layout()
        self.refresh_history()

    def _build_layout(self) -> None:
        wrapper = tk.Frame(self, bg="#f3f6fb")
        wrapper.pack(fill="both", expand=True, padx=20, pady=20)

        left = tk.Frame(wrapper, bg="white", bd=1, relief="solid")
        right = tk.Frame(wrapper, bg="white", bd=1, relief="solid")
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        right.pack(side="right", fill="both", expand=True, padx=(10, 0))

        tk.Label(left, text="Microscope Calculator", font=("Segoe UI", 18, "bold"), bg="white").pack(
            anchor="w", padx=20, pady=(20, 10)
        )

        form = tk.Frame(left, bg="white")
        form.pack(fill="x", padx=20)

        self._add_entry(form, "Username", self.username_var)
        self._add_entry(form, "Measured size (mm)", self.measured_size_var)

        self._add_combo(form, "Microscope type", self.microscope_var, list(MICROSCOPE_TYPES))
        self._add_combo(form, "Output unit", self.unit_var, list(UNIT_LABELS))

        upload_row = tk.Frame(form, bg="white")
        upload_row.pack(fill="x", pady=8)
        tk.Label(upload_row, text="Specimen image", width=18, anchor="w", bg="white").pack(side="left")
        ttk.Button(upload_row, text="Upload image", command=self.select_image).pack(side="left")

        self.image_name_label = tk.Label(form, text="No image selected.", bg="white", fg="#506070")
        self.image_name_label.pack(anchor="w", padx=(160, 0), pady=(0, 12))

        self.preview_label = tk.Label(left, text="Image preview", bg="#eef3fa", width=40, height=16)
        self.preview_label.pack(fill="both", expand=False, padx=20, pady=10)

        button_row = tk.Frame(left, bg="white")
        button_row.pack(fill="x", padx=20, pady=10)
        ttk.Button(button_row, text="Calculate and Save", command=self.run_calculation).pack(side="left")
        ttk.Button(button_row, text="Clear Form", command=self.clear_form).pack(side="left", padx=10)

        tk.Label(left, textvariable=self.result_var, justify="left", bg="white", fg="#0c2f5a").pack(
            fill="x", padx=20, pady=(10, 8)
        )

        tk.Label(left, text="Formula breakdown", font=("Segoe UI", 11, "bold"), bg="white").pack(
            anchor="w", padx=20
        )
        self.breakdown_text = tk.Text(left, height=10, wrap="word")
        self.breakdown_text.pack(fill="both", expand=True, padx=20, pady=(8, 20))

        tk.Label(right, text="Saved Records", font=("Segoe UI", 18, "bold"), bg="white").pack(
            anchor="w", padx=20, pady=(20, 10)
        )

        columns = ("id", "username", "measured", "microscope", "result", "date")
        self.tree = ttk.Treeview(right, columns=columns, show="headings", height=18)
        headings = {
            "id": "ID",
            "username": "Username",
            "measured": "Measured (mm)",
            "microscope": "Microscope",
            "result": "Result",
            "date": "Date",
        }
        widths = {"id": 40, "username": 100, "measured": 110, "microscope": 180, "result": 120, "date": 140}
        for key in columns:
            self.tree.heading(key, text=headings[key])
            self.tree.column(key, width=widths[key], anchor="center")
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        actions = tk.Frame(right, bg="white")
        actions.pack(fill="x", padx=20, pady=(0, 20))
        ttk.Button(actions, text="Refresh", command=self.refresh_history).pack(side="left")
        ttk.Button(actions, text="Delete Selected", command=self.delete_selected).pack(side="left", padx=10)
        ttk.Button(actions, text="Delete All", command=self.delete_all).pack(side="left")

    def _add_entry(self, parent: tk.Widget, label: str, variable: tk.StringVar) -> None:
        row = tk.Frame(parent, bg="white")
        row.pack(fill="x", pady=8)
        tk.Label(row, text=label, width=18, anchor="w", bg="white").pack(side="left")
        ttk.Entry(row, textvariable=variable, width=40).pack(side="left", fill="x", expand=True)

    def _add_combo(self, parent: tk.Widget, label: str, variable: tk.StringVar, values: list[str]) -> None:
        row = tk.Frame(parent, bg="white")
        row.pack(fill="x", pady=8)
        tk.Label(row, text=label, width=18, anchor="w", bg="white").pack(side="left")
        ttk.Combobox(row, textvariable=variable, values=values, state="readonly", width=37).pack(
            side="left", fill="x", expand=True
        )

    def select_image(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Select specimen image",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp"), ("All files", "*.*")],
        )
        if not file_path:
            return

        self.selected_image_source = file_path
        self.image_name_label.config(text=Path(file_path).name)

        image = Image.open(file_path)
        image.thumbnail((400, 260))
        self.preview_image = ImageTk.PhotoImage(image)
        self.preview_label.config(image=self.preview_image, text="")

    def copy_uploaded_image(self) -> str:
        if not self.selected_image_source:
            raise ValueError("Please upload a specimen image before calculating.")

        source = Path(self.selected_image_source)
        destination = UPLOADS_DIR / source.name
        shutil.copy2(source, destination)
        return str(destination)

    def run_calculation(self) -> None:
        try:
            stored_image_path = self.copy_uploaded_image()
            result = calculate_specimen_size(
                username=self.username_var.get(),
                image_path=stored_image_path,
                measured_size_mm=self.measured_size_var.get(),
                microscope_type=self.microscope_var.get(),
                output_unit=self.unit_var.get(),
            )
            save_calculation(result)
        except Exception as exc:
            messagebox.showerror("Calculation Error", str(exc))
            return

        self.result_var.set(
            f"Actual size: {result.output_value:.6f} {UNIT_LABELS[result.output_unit]} "
            f"(real size in mm: {result.real_size_mm:.6f})"
        )
        self.breakdown_text.delete("1.0", tk.END)
        self.breakdown_text.insert(tk.END, result.breakdown)
        self.refresh_history()
        messagebox.showinfo("Saved", "Calculation completed and saved to the database.")

    def clear_form(self) -> None:
        self.username_var.set("")
        self.measured_size_var.set("")
        self.microscope_var.set(list(MICROSCOPE_TYPES)[0])
        self.unit_var.set("um")
        self.selected_image_source = ""
        self.preview_image = None
        self.preview_label.config(image="", text="Image preview")
        self.image_name_label.config(text="No image selected.")
        self.result_var.set("Result will appear here.")
        self.breakdown_text.delete("1.0", tk.END)

    def refresh_history(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in fetch_calculations():
            result_text = f"{row['output_value']:.4f} {UNIT_LABELS[row['output_unit']]}"
            self.tree.insert(
                "",
                "end",
                values=(
                    row["id"],
                    row["username"],
                    f"{row['measured_size_mm']:.4f}",
                    row["microscope_type"],
                    result_text,
                    row["created_at"],
                ),
            )

    def delete_selected(self) -> None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a record to delete.")
            return

        record_id = int(self.tree.item(selected[0], "values")[0])
        delete_calculation(record_id)
        self.refresh_history()

    def delete_all(self) -> None:
        confirmed = messagebox.askyesno("Confirm", "Delete all saved records?")
        if confirmed:
            clear_calculations()
            self.refresh_history()


if __name__ == "__main__":
    app = MicroscopeApp()
    app.mainloop()
