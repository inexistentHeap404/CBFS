
import tkinter as tk

from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import shutil
import os

import main


# ==========================================
# CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
DOCUMENT_DIR = BASE_DIR / "documents"

DOCUMENT_DIR.mkdir(exist_ok=True)


# ==========================================
# APPLICATION
# ==========================================

class LocalSearch:

    def __init__(self, root):

        self.root = root

        self.root.title("LocalSearch")
        self.root.geometry("950x650")
        self.root.minsize(750, 500)

        self.documents = {}

        self.setup_ui()
        self.load_documents()

    # ======================================
    # UI
    # ======================================

    def setup_ui(self):

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            rowheight=32,
            font=("Arial", 10)
        )

        header = ttk.Frame(
            self.root,
            padding=20
        )

        header.pack(fill="x")

        ttk.Label(
            header,
            text="LocalSearch",
            font=("Arial", 23, "bold")
        ).pack(side="left")

        self.count_label = ttk.Label(
            header,
            text="0 documents"
        )

        self.count_label.pack(side="right")

        # SEARCH

        search_frame = ttk.Frame(
            self.root,
            padding=(20, 5, 20, 15)
        )

        search_frame.pack(fill="x")

        self.search_entry = ttk.Entry(
            search_frame,
            font=("Arial", 13)
        )

        self.search_entry.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=8
        )

        self.search_entry.bind(
            "<Return>",
            lambda event: self.search()
        )

        ttk.Button(
            search_frame,
            text="Search",
            command=self.search
        ).pack(side="left", padx=8)

        # ACTIONS

        actions = ttk.Frame(
            self.root,
            padding=(20, 0, 20, 12)
        )

        actions.pack(fill="x")

        ttk.Button(
            actions,
            text="+ Upload files",
            command=self.upload
        ).pack(side="left")

        ttk.Button(
            actions,
            text="Show all",
            command=self.show_all
        ).pack(side="left", padx=8)

        ttk.Button(
            actions,
            text="Delete selected",
            command=self.delete_selected
        ).pack(side="left")

        # RESULTS

        table_frame = ttk.Frame(
            self.root,
            padding=(20, 5, 20, 10)
        )

        table_frame.pack(
            fill="both",
            expand=True
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=("filename", "similarity"),
            show="headings",
            selectmode="browse"
        )

        self.tree.heading(
            "filename",
            text="Document"
        )

        self.tree.heading(
            "similarity",
            text="Similarity"
        )

        self.tree.column(
            "filename",
            width=650
        )

        self.tree.column(
            "similarity",
            width=150,
            anchor="center"
        )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.tree.bind(
            "<Double-1>",
            self.open_document
        )

        # STATUS

        self.status = tk.StringVar(
            value="Ready"
        )

        ttk.Label(
            self.root,
            textvariable=self.status,
            relief="sunken",
            padding=6,
            anchor="w"
        ).pack(fill="x", side="bottom")

    # ======================================
    # LOAD EXISTING FILES
    # ======================================

    def load_documents(self):

        self.documents.clear()

        errors = []

        for path in DOCUMENT_DIR.iterdir():

            if not path.is_file():
                continue

            try:

                content = main.extract_text(path)

                if content.strip():
                    self.documents[path.name] = content

            except Exception as error:

                errors.append(
                    f"{path.name}: {error}"
                )

        self.update_count()
        self.show_all()

        if errors:
            self.status.set(
                f"Skipped {len(errors)} unreadable file(s)"
            )

    # ======================================
    # UPLOAD
    # ======================================

    def upload(self):

        paths = filedialog.askopenfilenames(
            title="Select documents"
        )

        if not paths:
            return

        uploaded = 0

        for source in paths:

            source = Path(source)
            destination = DOCUMENT_DIR / source.name

            if destination.exists():

                replace = messagebox.askyesno(
                    "File already exists",
                    f"{source.name} already exists.\nReplace it?"
                )

                if not replace:
                    continue

            try:

                # Validate before replacing an existing file
                content = main.extract_text(source)

                if not content.strip():
                    raise ValueError("No readable text found")

                shutil.copy2(
                    source,
                    destination
                )

                self.documents[source.name] = content

                uploaded += 1

            except Exception as error:

                messagebox.showerror(
                    "Upload error",
                    f"{source.name}\n{error}"
                )

        self.update_count()
        self.show_all()

        self.status.set(
            f"{uploaded} file(s) uploaded"
        )

    # ======================================
    # SEARCH
    # ======================================

    def search(self):

        query = self.search_entry.get().strip()

        if not query:
            return

        if not self.documents:

            messagebox.showinfo(
                "Search",
                "Upload documents first."
            )

            return

        results = main.search(
            self.documents,
            query
        )

        self.clear_table()

        for result in results:

            self.tree.insert(
                "",
                "end",
                iid=result["filename"],
                values=(
                    result["filename"],
                    f"{result['similarity']* 100:.2f}%"
                )
            )

        self.status.set(
            f"{len(results)} matching documents"
        )

    # ======================================
    # SHOW ALL
    # ======================================

    def show_all(self):

        self.clear_table()

        for filename in self.documents:

            self.tree.insert(
                "",
                "end",
                iid=filename,
                values=(filename, "-")
            )

        self.status.set(
            f"{len(self.documents)} documents available"
        )

    # ======================================
    # OPEN DOCUMENT
    # ======================================

    def open_document(self, event=None):

        selected = self.tree.selection()

        if not selected:
            return

        filename = selected[0]

        path = DOCUMENT_DIR / filename

        if not path.exists():
            return

        try:

            if os.name == "nt":
                os.startfile(path)

            elif os.uname().sysname == "Darwin":
                os.system(
                    f'open "{path}"'
                )

            else:
                os.spawnlp(
                    os.P_NOWAIT,
                    "xdg-open",
                    "xdg-open",
                    str(path)
                )

        except Exception as error:

            messagebox.showerror(
                "Open error",
                str(error)
            )

    # ======================================
    # DELETE
    # ======================================

    def delete_selected(self):

        selected = self.tree.selection()

        if not selected:
            return

        filename = selected[0]

        confirm = messagebox.askyesno(
            "Delete document",
            f"Permanently delete {filename}?"
        )

        if not confirm:
            return

        path = DOCUMENT_DIR / filename

        try:

            path.unlink()

            self.documents.pop(
                filename,
                None
            )

            self.update_count()
            self.show_all()

        except Exception as error:

            messagebox.showerror(
                "Delete error",
                str(error)
            )

    # ======================================
    # UTILITIES
    # ======================================

    def clear_table(self):

        for item in self.tree.get_children():
            self.tree.delete(item)

    def update_count(self):

        self.count_label.config(
            text=f"{len(self.documents)} documents"
        )


# ==========================================
# ENTRY POINT
# ==========================================

if __name__ == "__main__":

    root = tk.Tk()

    app = LocalSearch(root)

    root.mainloop()

