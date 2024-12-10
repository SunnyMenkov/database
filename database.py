import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os
import json

class MuseumDatabase:
    def __init__(self, filename="database.json"):
        self.filename = filename
        if not os.path.exists(self.filename):
            self._initialize_file()

    def _initialize_file(self):
        with open(self.filename, "w") as file:
            json.dump({"records": {}, "next_id": 1}, file)

    def _read_file(self):
        with open(self.filename, "r") as file:
            return json.load(file)

    def _write_file(self, data):
        with open(self.filename, "w") as file:
            json.dump(data, file)

    def create(self):
        self._initialize_file()

    def open(self, filename):
        try:
            with open(filename, "r") as file:
                data = json.load(file)
            self.filename = filename
            self._write_file(data)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {e}")

    def save(self, filename):
        try:
            data = self._read_file()
            with open(filename, "w") as file:
                json.dump(data, file)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")

    def delete(self):
        self._initialize_file()

    def clear(self):
        data = {"records": {}, "next_id": self._read_file()["next_id"]}
        self._write_file(data)

    def add_record(self, title, year, artist, style):
        data = self._read_file()

        # Create a unique key from the key fields
        record_key = f"{title}{year}{artist}"

        # Check if the record already exists
        if record_key in data["records"]:
            raise ValueError("Duplicate record.")

        # Add the new record
        new_record = {
            "id": data["next_id"],
            "title": title,
            "year": year,
            "artist": artist,
            "style": style
        }
        data["records"][record_key] = new_record
        data["next_id"] += 1

        # Save changes to the file
        self._write_file(data)

    def delete_record(self, record_id, title, year, artist, style):
        data = self._read_file()
        new_key = f"{title}{year}{artist}"
        if new_key in data["records"]:
            del data["records"][new_key]
            self._write_file(data)
            return
        raise ValueError("Record not found.")

    def search(self, field, value):
        data = self._read_file()
        return [record for record in data["records"].values() if str(record.get(field)) == str(value)]

    def edit_record(self, record_id, title, year, artist, style):
        data = self._read_file()
        for key, record in list(data["records"].items()):
            if record["id"] == record_id:
                new_key = f"{title}{year}{artist}"

                # Check for potential key collision
                if new_key != key and new_key in data["records"]:
                    raise ValueError("Duplicate record.")

                # Update record and key if necessary
                data["records"][new_key] = {
                    "id": record_id,
                    "title": title,
                    "year": year,
                    "artist": artist,
                    "style": style
                }
                if new_key != key:
                    del data["records"][key]

                self._write_file(data)
                return
        raise ValueError("Record not found.")

    def backup(self, filename):
        self.save(filename)

    def restore(self, filename):
        self.open(filename)

    def export_to_csv(self, filename):
        try:
            data = self._read_file()
            with open(filename, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["id", "title", "year", "artist", "style"])
                for record in data["records"].values():
                    writer.writerow([record["id"], record["title"], record["year"], record["artist"], record["style"]])
        except Exception as e:
            messagebox.showerror("Error", f"Could not export to CSV: {e}")


class MuseumApp:
    def __init__(self, root):
        self.db = MuseumDatabase()
        self.root = root
        self.root.title("Museum Database")

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        # Input fields
        tk.Label(self.root, text="Title:").grid(row=0, column=0, padx=5, pady=5)
        self.title_entry = tk.Entry(self.root)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.root, text="Year:").grid(row=1, column=0, padx=5, pady=5)
        self.year_entry = tk.Entry(self.root)
        self.year_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.root, text="Artist:").grid(row=2, column=0, padx=5, pady=5)
        self.artist_entry = tk.Entry(self.root)
        self.artist_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self.root, text="Style:").grid(row=3, column=0, padx=5, pady=5)
        self.style_entry = tk.Entry(self.root)
        self.style_entry.grid(row=3, column=1, padx=5, pady=5)

        # Buttons
        tk.Button(self.root, text="Add Record", command=self.add_record).grid(row=4, column=0, padx=5, pady=5)
        tk.Button(self.root, text="Search", command=self.search).grid(row=4, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Clear All", command=self.clear).grid(row=4, column=2, padx=5, pady=5)

        tk.Button(self.root, text="Export CSV", command=self.export_csv).grid(row=5, column=0, padx=5, pady=5)
        tk.Button(self.root, text="Backup", command=self.backup).grid(row=5, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Restore", command=self.restore).grid(row=5, column=2, padx=5, pady=5)

        tk.Button(self.root, text="Delete Record", command=self.delete_record).grid(row=6, column=0, padx=5, pady=5)
        tk.Button(self.root, text="Edit Record", command=self.edit_record).grid(row=6, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Open DB", command=self.open_db).grid(row=6, column=2, padx=5, pady=5)
        tk.Button(self.root, text="Create DB", command=self.create_db).grid(row=6, column=3, padx=5, pady=5)

        # Results Table
        self.tree = ttk.Treeview(self.root, columns=("id", "title", "year", "artist", "style"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="Title")
        self.tree.heading("year", text="Year")
        self.tree.heading("artist", text="Artist")
        self.tree.heading("style", text="Style")
        self.tree.grid(row=7, column=0, columnspan=4, padx=5, pady=5)

    def add_record(self):
        try:
            title = self.title_entry.get()
            year = int(self.year_entry.get())
            artist = self.artist_entry.get()
            style = self.style_entry.get()
            self.db.add_record(title, year, artist, style)
            self.update_table()
        except Exception as e:
            messagebox.showerror("Error", f"Could not add record: {e}")

    def delete_record(self):
        try:
            selected_item = self.tree.selection()[0]
            record_id = int(self.tree.item(selected_item, "values")[0])

            title = self.title_entry.get()
            year = int(self.year_entry.get())
            artist = self.artist_entry.get()
            style = self.style_entry.get()

            self.db.delete_record(record_id, title, year, artist, style)
            self.update_table()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not delete record: {e}")

    def edit_record(self):
        try:
            selected_item = self.tree.selection()[0]
            record_id = int(self.tree.item(selected_item, "values")[0])

            title = self.title_entry.get()
            year = int(self.year_entry.get())
            artist = self.artist_entry.get()
            style = self.style_entry.get()

            self.db.edit_record(record_id, title, year, artist, style)
            self.update_table()
        except IndexError:
            messagebox.showerror("Error", "No record selected for editing.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not edit record: {e}")

    def open_db(self):
        filename = filedialog.askopenfilename(
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        if filename:
            try:
                self.db.open(filename)
                self.update_table()
                messagebox.showinfo("Success", f"Opened database file: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open database: {e}")

    def create_db(self):
        try:
            self.db.create()
            self.update_table()
            messagebox.showinfo("Success", "New database file created.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not create database: {e}")

    def update_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            records = self.db._read_file()["records"].values()
            for record in records:
                self.tree.insert("", "end", values=(
                    record["id"], record["title"], record["year"], record["artist"], record["style"]
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Could not update table: {e}")

    def search(self):
        field = "title"  # For simplicity, you could add dropdowns to choose fields
        value = self.title_entry.get()
        try:
            results = self.db.search(field, value)
            for row in self.tree.get_children():
                self.tree.delete(row)
            for record in results:
                self.tree.insert("", "end", values=(
                    record["id"], record["title"], record["year"], record["artist"], record["style"]
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Could not search records: {e}")

    def clear(self):
        try:
            self.db.clear()
            self.update_table()
            messagebox.showinfo("Success", "Database cleared.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not clear database: {e}")

    def export_csv(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
        )
        if filename:
            try:
                self.db.export_to_csv(filename)
                messagebox.showinfo("Success", f"Database exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not export to CSV: {e}")

    def backup(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        if filename:
            try:
                self.db.backup(filename)
                messagebox.showinfo("Success", f"Database backed up to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not create backup: {e}")

    def restore(self):
        filename = filedialog.askopenfilename(
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        if filename:
            try:
                self.db.restore(filename)
                self.update_table()
                messagebox.showinfo("Success", f"Database restored from {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not restore database: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = MuseumApp(root)
    root.mainloop()
