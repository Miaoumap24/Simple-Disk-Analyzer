# Copyright (C) 2026 Lixiod Technologies

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from collections import defaultdict
import threading

def format_size(size_bytes):
    if size_bytes == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    while size >= 1024 and i < len(units) - 1:
        size /= 1024
        i += 1
    return f"{size:.2f} {units[i]}"

class DiskAnalyzer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simple Disk Analyzer")
        self.geometry("1000x650")

        self.scanning = False
        self.total_size = 0
        self.ext_stats = defaultdict(lambda: {"size": 0, "count": 0})

        self._build_ui()

    def _build_ui(self):
        # Top selection bar
        top_frame = ttk.Frame(self, padding=10)
        top_frame.pack(fill=tk.X)

        ttk.Label(top_frame, text="Target Directory:").pack(side=tk.LEFT, padx=(0, 5))
        self.path_entry = ttk.Entry(top_frame)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.path_entry.insert(0, os.path.abspath(os.sep))

        self.browse_btn = ttk.Button(top_frame, text="Browse", command=self._browse_directory)
        self.browse_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.scan_btn = ttk.Button(top_frame, text="Scan", command=self._start_scan)
        self.scan_btn.pack(side=tk.LEFT)

        # Status & Progress bar
        status_frame = ttk.Frame(self, padding=(10, 0, 10, 5))
        status_frame.pack(fill=tk.X)

        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.pack(side=tk.LEFT)

        self.progress_bar = ttk.Progressbar(status_frame, mode="indeterminate")
        self.progress_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))

        # Main Tabbed view
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1: Directory Tree View
        self.tree_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.tree_tab, text="Directory Structure")

        self.file_tree = ttk.Treeview(self.tree_tab, columns=("size", "percent"), show="tree headings")
        self.file_tree.heading("#0", text="Folder / File", anchor=tk.W)
        self.file_tree.heading("size", text="Size", anchor=tk.E)
        self.file_tree.heading("percent", text="% of Total", anchor=tk.E)

        self.file_tree.column("#0", stretch=True, width=500)
        self.file_tree.column("size", stretch=False, width=120, anchor=tk.E)
        self.file_tree.column("percent", stretch=False, width=100, anchor=tk.E)

        tree_scroll = ttk.Scrollbar(self.tree_tab, orient=tk.VERTICAL, command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=tree_scroll.set)

        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Tab 2: File Extensions Stats
        self.ext_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.ext_tab, text="Extension Stats")

        self.ext_tree = ttk.Treeview(self.ext_tab, columns=("ext", "size", "count", "percent"), show="headings")
        self.ext_tree.heading("ext", text="Extension", anchor=tk.W)
        self.ext_tree.heading("size", text="Total Size", anchor=tk.E)
        self.ext_tree.heading("count", text="File Count", anchor=tk.E)
        self.ext_tree.heading("percent", text="% of Total", anchor=tk.E)

        self.ext_tree.column("ext", stretch=True, width=200)
        self.ext_tree.column("size", stretch=False, width=120, anchor=tk.E)
        self.ext_tree.column("count", stretch=False, width=100, anchor=tk.E)
        self.ext_tree.column("percent", stretch=False, width=100, anchor=tk.E)

        ext_scroll = ttk.Scrollbar(self.ext_tab, orient=tk.VERTICAL, command=self.ext_tree.yview)
        self.ext_tree.configure(yscrollcommand=ext_scroll.set)

        self.ext_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ext_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def _browse_directory(self):
        selected = filedialog.askdirectory()
        if selected:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, selected)

    def _start_scan(self):
        if self.scanning:
            return

        target_path = self.path_entry.get()
        if not os.path.exists(target_path):
            messagebox.showerror("Error", "Selected path does not exist.")
            return

        self.scanning = True
        self.scan_btn.config(state=tk.DISABLED)
        self.browse_btn.config(state=tk.DISABLED)
        self.progress_bar.start(10)
        self.status_label.config(text="Scanning files...")

        self.file_tree.delete(*self.file_tree.get_children())
        self.ext_tree.delete(*self.ext_tree.get_children())
        self.ext_stats.clear()

        threading.Thread(target=self._scan_worker, args=(target_path,), daemon=True).start()

    def _scan_worker(self, path):
        def scan_dir(dir_path):
            dir_size = 0
            children_data = []

            try:
                with os.scandir(dir_path) as entries:
                    for entry in entries:
                        try:
                            if entry.is_file(follow_symlinks=False):
                                stat = entry.stat(follow_symlinks=False)
                                size = stat.st_size
                                dir_size += size
                                children_data.append((entry.name, size, True, []))

                                ext = os.path.splitext(entry.name)[1].lower() or "No Extension"
                                self.ext_stats[ext]["size"] += size
                                self.ext_stats[ext]["count"] += 1

                            elif entry.is_dir(follow_symlinks=False):
                                sub_size, sub_children = scan_dir(entry.path)
                                dir_size += sub_size
                                children_data.append((entry.name, sub_size, False, sub_children))

                        except PermissionError:
                            continue
            except PermissionError:
                pass

            children_data.sort(key=lambda item: item[1], reverse=True)
            return dir_size, children_data

        self.total_size, tree_structure = scan_dir(path)
        self.after(0, self._populate_ui, path, tree_structure)

    def _populate_ui(self, root_path, tree_structure):
        root_node = self.file_tree.insert(
            "", tk.END, text=root_path,
            values=(format_size(self.total_size), "100.00%")
        )

        def insert_nodes(parent, items):
            for name, size, is_file, children in items:
                pct = (size / self.total_size * 100) if self.total_size > 0 else 0
                node = self.file_tree.insert(
                    parent, tk.END, text=name,
                    values=(format_size(size), f"{pct:.2f}%")
                )
                if not is_file and children:
                    insert_nodes(node, children)

        insert_nodes(root_node, tree_structure)
        self.file_tree.item(root_node, open=True)

        sorted_exts = sorted(self.ext_stats.items(), key=lambda x: x[1]["size"], reverse=True)
        for ext, data in sorted_exts:
            pct = (data["size"] / self.total_size * 100) if self.total_size > 0 else 0
            self.ext_tree.insert(
                "", tk.END,
                values=(ext, format_size(data["size"]), data["count"], f"{pct:.2f}%")
            )

        self.progress_bar.stop()
        self.status_label.config(text=f"Scan complete. Total size: {format_size(self.total_size)}")
        self.scan_btn.config(state=tk.NORMAL)
        self.browse_btn.config(state=tk.NORMAL)
        self.scanning = False

if __name__ == "__main__":
    app = DiskAnalyzer()
    app.mainloop()
