import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import platform
import shutil

class SiteBlockerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Блокировщик сайтов")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        self.os_type = platform.system()
        if self.os_type == "Windows":
            self.hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
        else:
            self.hosts_path = "/etc/hosts"
        self.redirect_ip = "127.0.0.1"
        self.blocked_sites = self.load_blocked_sites()
        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        title_label = ttk.Label(main_frame, text="Блокировщик сайтов", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 15))
        info_text = f"Система: {self.os_type} | Файл hosts: {self.hosts_path}"
        ttk.Label(main_frame, text=info_text).grid(row=1, column=0, columnspan=3, pady=(0, 10))
        ttk.Label(main_frame, text="Сайт для блокировки:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.site_entry = ttk.Entry(main_frame, width=40)
        self.site_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 5))
        ttk.Label(main_frame, text="Например: example.com (без http://)", foreground="gray").grid(row=3, column=1, sticky=tk.W, padx=(5, 0))
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=4, column=0, columnspan=3, pady=15)
        self.block_button = ttk.Button(buttons_frame, text="Заблокировать сайт", command=self.block_site)
        self.block_button.pack(side=tk.LEFT, padx=5)
        self.unblock_button = ttk.Button(buttons_frame, text="Разблокировать сайт", command=self.unblock_site)
        self.unblock_button.pack(side=tk.LEFT, padx=5)
        self.unblock_all_button = ttk.Button(buttons_frame, text="Разблокировать все", command=self.unblock_all)
        self.unblock_all_button.pack(side=tk.LEFT, padx=5)
        ttk.Label(main_frame, text="Заблокированные сайты:", font=("Arial", 10, "bold")).grid(row=5, column=0, sticky=tk.W, pady=(20, 5))
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        columns = ("site", "status")
        self.sites_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        self.sites_tree.heading("site", text="Заблокированный сайт")
        self.sites_tree.heading("status", text="Статус")
        self.sites_tree.column("site", width=350)
        self.sites_tree.column("status", width=150)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.sites_tree.yview)
        self.sites_tree.configure(yscrollcommand=scrollbar.set)
        self.sites_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        self.status_var = tk.StringVar(value="Готово")
        ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN).grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        self.update_sites_list()
        self.sites_tree.bind("<<TreeviewSelect>>", self.on_site_select)

    def load_blocked_sites(self):
        blocked = []
        try:
            with open(self.hosts_path, 'r') as file:
                for line in file.readlines():
                    line = line.strip()
                    if line.startswith(self.redirect_ip):
                        parts = line.split()
                        if len(parts) >= 2:
                            for site in parts[1:]:
                                if site and not site.startswith('#'):
                                    blocked.append(site)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать файл hosts:\n{str(e)}")
        return blocked

    def update_sites_list(self):
        for item in self.sites_tree.get_children():
            self.sites_tree.delete(item)
        for site in self.blocked_sites:
            status = "Заблокирован" if self.is_site_blocked(site) else "Не заблокирован"
            self.sites_tree.insert("", tk.END, values=(site, status))

    def is_site_blocked(self, site):
        try:
            with open(self.hosts_path, 'r') as file:
                content = file.read()
                return f"{self.redirect_ip} {site}" in content or f"{self.redirect_ip}\t{site}" in content
        except Exception:
            return False

    def block_site(self):
        site = self.site_entry.get().strip()
        if not site:
            messagebox.showwarning("Предупреждение", "Введите адрес сайта для блокировки")
            return
        site = site.replace("http://", "").replace("https://", "").replace("www.", "")
        if self.is_site_blocked(site):
            messagebox.showinfo("Информация", "Сайт уже заблокирован")
            return
        try:
            with open(self.hosts_path, 'a') as file:
                file.write(f"\n{self.redirect_ip} {site}")
            self.blocked_sites.append(site)
            self.update_sites_list()
            self.site_entry.delete(0, tk.END)
            self.status_var.set(f"Заблокирован: {site}")
        except PermissionError:
            messagebox.showerror("Ошибка", "Недостаточно прав. Запустите программу от имени администратора.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось заблокировать сайт:\n{str(e)}")

    def unblock_site(self):
        selected = self.sites_tree.selection()
        site = self.site_entry.get().strip()
        if selected:
            site = self.sites_tree.item(selected[0])['values'][0]
        if not site:
            messagebox.showwarning("Предупреждение", "Выберите сайт или введите его адрес")
            return
        try:
            with open(self.hosts_path, 'r') as file:
                lines = file.readlines()
            with open(self.hosts_path, 'w') as file:
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 2 and parts[0] == self.redirect_ip and site in parts[1:]:
                        continue
                    file.write(line)
            if site in self.blocked_sites:
                self.blocked_sites.remove(site)
            self.update_sites_list()
            self.site_entry.delete(0, tk.END)
            self.status_var.set(f"Разблокирован: {site}")
        except PermissionError:
            messagebox.showerror("Ошибка", "Недостаточно прав. Запустите программу от имени администратора.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось разблокировать сайт:\n{str(e)}")

    def unblock_all(self):
        if not self.blocked_sites:
            messagebox.showinfo("Информация", "Нет заблокированных сайтов")
            return
        if not messagebox.askyesno("Подтверждение", "Разблокировать все сайты?"):
            return
        try:
            with open(self.hosts_path, 'r') as file:
                lines = file.readlines()
            blocked_set = set(self.blocked_sites)
            with open(self.hosts_path, 'w') as file:
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 2 and parts[0] == self.redirect_ip and blocked_set.intersection(parts[1:]):
                        continue
                    file.write(line)
            self.blocked_sites.clear()
            self.update_sites_list()
            self.status_var.set("Все сайты разблокированы")
        except PermissionError:
            messagebox.showerror("Ошибка", "Недостаточно прав. Запустите программу от имени администратора.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось разблокировать сайты:\n{str(e)}")

    def on_site_select(self, event):
        selected = self.sites_tree.selection()
        if selected:
            self.site_entry.delete(0, tk.END)
            self.site_entry.insert(0, self.sites_tree.item(selected[0])['values'][0])

if __name__ == "__main__":
    root = tk.Tk()
    app = SiteBlockerApp(root)
    root.mainloop()
