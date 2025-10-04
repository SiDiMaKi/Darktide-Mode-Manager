import sys
import os
import subprocess
import zipfile
import rarfile
import webbrowser

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QInputDialog, QDialog,
    QListWidget, QPushButton, QFileDialog, QMessageBox, QMenuBar, QMenu, QListWidgetItem
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QColor, QIcon

from utils.ExistingModsDialog import ExistingModsDialog

# одразу вказуємо шлях до UnRAR.exe
rarfile.UNRAR_TOOL = os.path.join(os.getcwd(), "tools", "UnRAR.exe")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Darktide Mod Handler")
        self.resize(900, 600)

        # --- Налаштування ---
        self.settings = QSettings("DarktideTools", "ModHandler")
        self.steam_path = self.settings.value("steam_path", "")
        self.toggle_path = self.settings.value("toggle_path", "")
        self.mods_enabled = self.settings.value("mods_enabled", False, type=bool)

        # Питаємо Steam шлях
        if not self.steam_path or not os.path.exists(self.steam_path):
            self.ask_for_steam_path()

        # Питаємо toggle_darktide_mods.bat
        if not self.toggle_path or not os.path.exists(self.toggle_path):
            self.ask_for_toggle_path()

        # Папка модів
        self.mods_dir = os.path.join(
            self.steam_path,
            "steamapps",
            "common",
            "Warhammer 40,000 DARKTIDE",
            "mods"
        )
        os.makedirs(self.mods_dir, exist_ok=True)
        self.load_order_file = os.path.join(self.mods_dir, "mod_load_order.txt")

        self.mods = []   # список модів
        self.current_mod = None

        # --- Меню ---
        menu_bar = QMenuBar()
        file_menu = QMenu("Файл", self)
        menu_bar.addMenu(file_menu)

        # --- Меню ---
        menu_bar = QMenuBar()

        file_menu = QMenu("Файл", self)
        menu_bar.addMenu(file_menu)

        mods_menu = QMenu("Моди", self)
        menu_bar.addMenu(mods_menu)

        # пункт меню для Nexus Mods
        visit_nexus_action = mods_menu.addAction("Відвідати Nexus Mods")
        visit_nexus_action.triggered.connect(
            lambda: webbrowser.open("https://www.nexusmods.com/games/warhammer40kdarktide/mods")
        )

        self.setMenuBar(menu_bar)

        add_mod_action = file_menu.addAction("Додати мод (.rar, .zip, .7z)")
        add_mod_action.triggered.connect(self.add_mod)

        remove_mod_action = file_menu.addAction("Видалити мод")
        remove_mod_action.triggered.connect(self.remove_mod)

        set_steam_action = file_menu.addAction("Змінити шлях до Steam")
        set_steam_action.triggered.connect(self.ask_for_steam_path)

        set_toggle_action = file_menu.addAction("Змінити шлях до toggle_darktide_mods.bat")
        set_toggle_action.triggered.connect(self.ask_for_toggle_path)

        exit_action = file_menu.addAction("Вийти")
        exit_action.triggered.connect(self.close)

        self.setMenuBar(menu_bar)

        # --- Ліва панель: список з mod_load_order.txt ---
        self.mod_list = QListWidget()
        self.mod_list.itemClicked.connect(self.select_mod)

        # --- Права панель: кнопки ---
        self.add_button = QPushButton("Додати мод")
        self.add_button.clicked.connect(self.add_mod)

        self.toggle_button = QPushButton()
        self.mods_enabled = self.check_mods_status()
        self.update_toggle_button()
        self.toggle_button.clicked.connect(self.toggle_mods)

        self.enable_button = QPushButton("Увімкнути мод")
        self.enable_button.clicked.connect(lambda: self.toggle_mod_state(True))

        self.disable_button = QPushButton("Виключити мод")
        self.disable_button.clicked.connect(lambda: self.toggle_mod_state(False))

        self.add_existing_button = QPushButton("Додати існуючі моди")
        self.add_existing_button.clicked.connect(self.add_existing_mods_multi)

        self.run_button = QPushButton("Запустити гру")
        self.run_button.clicked.connect(self.run_game)

        self.exit_button = QPushButton("Вийти")
        self.exit_button.clicked.connect(self.close)

        # --- Layout ---
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.mod_list)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.add_button)
        right_layout.addWidget(self.toggle_button)
        right_layout.addWidget(self.enable_button)
        right_layout.addWidget(self.disable_button)
        right_layout.addWidget(self.add_existing_button)
        right_layout.addStretch(1)
        right_layout.addWidget(self.run_button)
        right_layout.addWidget(self.exit_button)

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout, 2)
        main_layout.addLayout(right_layout, 1)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # --- завантажуємо моди при старті ---
        self.scan_mods()

    # --- Вибір шляху Steam ---
    def ask_for_steam_path(self):
        QMessageBox.information(
            self,
            "Вкажіть шлях до Steam",
            "Будь ласка, вкажіть папку, де встановлений Steam.\n"
            "Наприклад: C:\\Program Files (x86)\\Steam"
        )

        while True:
            path = QFileDialog.getExistingDirectory(self, "Виберіть папку Steam")
            if not path:
                QMessageBox.critical(self, "Помилка", "Не вказано шлях до Steam")
                sys.exit(1)

            # перевіряємо наявність Darktide
            game_path = os.path.join(path, "steamapps", "common", "Warhammer 40,000 DARKTIDE")
            if not os.path.exists(game_path):
                QMessageBox.warning(
                    self,
                    "Не знайдено Darktide",
                    "У вибраній директорії не знайдено Darktide.\n"
                    "Виберіть іншу папку, де встановлена гра."
                )
                continue

            self.steam_path = path
            self.settings.setValue("steam_path", self.steam_path)
            break


    # --- Вибір toggle_darktide_mods.bat ---
    def ask_for_toggle_path(self):
        QMessageBox.information(
            self,
            "Вкажіть toggle_darktide_mods.bat",
            "Будь ласка, вкажіть файл toggle_darktide_mods.bat з Darktide Mod Loader.\n\n"
            "Зазвичай він знаходиться у теці гри поряд із 'bundle_database.data'."
        )

        file_name, _ = QFileDialog.getOpenFileName(
            self, "Виберіть toggle_darktide_mods.bat", "", "Batch Files (*.bat)"
        )
        if file_name:
            self.toggle_path = file_name
            self.settings.setValue("toggle_path", self.toggle_path)
        else:
            QMessageBox.critical(self, "Помилка", "Не вказано шлях до toggle_darktide_mods.bat")
            sys.exit(1)

    # --- Читання mod_load_order.txt ---
    def scan_mods(self):
        self.mod_list.clear()
        self.mods.clear()
        if os.path.exists(self.load_order_file):
            with open(self.load_order_file, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
            self.mods = lines
            for mod in lines:
                item = QListWidgetItem(mod.lstrip("-"))
                if mod.startswith("--"):
                    item.setForeground(QColor("red"))
                self.mod_list.addItem(item)

    # --- Додавання моду (.zip) ---
    def add_mod(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Вибрати мод", "", "Archives (*.zip *.rar)"
        )
        if not file_name:
            return

        import shutil, zipfile, rarfile
        mod_name = os.path.splitext(os.path.basename(file_name))[0]
        target_path = os.path.join(self.mods_dir, mod_name)

        # Якщо така папка є – прибираємо (оновлення моду)
        if os.path.exists(target_path):
            shutil.rmtree(target_path)

        os.makedirs(target_path, exist_ok=True)

        try:
            # --- Розпаковка
            if file_name.endswith(".zip"):
                with zipfile.ZipFile(file_name, 'r') as zip_ref:
                    zip_ref.extractall(target_path)
            elif file_name.endswith(".rar"):
                import rarfile
                rarfile.UNRAR_TOOL = os.path.join(os.getcwd(), "tools", "UnRAR.exe")
                with rarfile.RarFile(file_name, 'r') as rar_ref:
                    rar_ref.extractall(target_path)
            else:
                QMessageBox.warning(self, "Помилка", "Формат архіву не підтримується")
                shutil.rmtree(target_path)
                return

            # --- Виправлення подвійної вкладеності
            subdirs = [d for d in os.listdir(target_path) if os.path.isdir(os.path.join(target_path, d))]
            if len(subdirs) == 1 and subdirs[0].lower() == mod_name.lower():
                inner_path = os.path.join(target_path, subdirs[0])
                for item in os.listdir(inner_path):
                    src = os.path.join(inner_path, item)
                    dst = os.path.join(target_path, item)
                    if os.path.exists(dst):
                        shutil.rmtree(dst) if os.path.isdir(dst) else os.remove(dst)
                    shutil.move(src, dst)
                shutil.rmtree(inner_path)

            # --- Перевірка чи це дійсно мод (шукаємо .mod файл)
            has_mod_file = False
            for root, dirs, files in os.walk(target_path):
                for f in files:
                    if f.endswith(".mod"):
                        has_mod_file = True
                        break
                if has_mod_file:
                    break

            if not has_mod_file:
                shutil.rmtree(target_path)  # видаляємо некоректний мод
                QMessageBox.critical(self, "Помилка", "У архіві немає .mod файлу — це не мод для Darktide")
                return

            # --- Якщо все добре → додаємо до load_order
            already_in_file = False
            if os.path.exists(self.load_order_file):
                with open(self.load_order_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip().lstrip("-") == mod_name:
                            already_in_file = True
                            break

            if not already_in_file:
                with open(self.load_order_file, "a", encoding="utf-8") as f:
                    # перевірка щоб не злипались рядки
                    if os.path.getsize(self.load_order_file) > 0:
                        f.write("\n")
                    f.write(mod_name)

            QMessageBox.information(self, "Успіх", f"Мод {mod_name} встановлено")
            self.scan_mods()

        except Exception as e:
            shutil.rmtree(target_path, ignore_errors=True)
            QMessageBox.critical(self, "Помилка", f"Не вдалося встановити мод:\n{e}")



    def append_mod_to_load_order(self, mod_name):
        with open(self.load_order_file, "a+", encoding="utf-8") as f:
            f.seek(0, os.SEEK_END)  # на кінець файлу
            if f.tell() > 0:  # якщо файл не пустий
                f.seek(f.tell() - 1)  # дивимося останній символ
                last_char = f.read(1)
                if last_char != "\n":
                    f.write("\n")  # додаємо перенос
            f.write(mod_name + "\n")

    # --- Видалення моду ---
    def remove_mod(self):
        current_item = self.mod_list.currentItem()
        if not current_item:
            return
        mod_name = current_item.text().lstrip("-")

        mod_path = os.path.join(self.mods_dir, mod_name)
        import shutil
        if os.path.exists(mod_path):
            shutil.rmtree(mod_path, ignore_errors=True)

        # Видаляємо рядок з mod_load_order.txt
        if os.path.exists(self.load_order_file):
            with open(self.load_order_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            with open(self.load_order_file, "w", encoding="utf-8") as f:
                for line in lines:
                    if line.strip().lstrip("-") != mod_name:
                        f.write(line)

        QMessageBox.information(self, "Видалено", f"Мод {mod_name} видалено повністю")
        self.scan_mods()


    # --- Збереження mod_load_order.txt ---
    def save_load_order(self):
        with open(self.load_order_file, "w", encoding="utf-8") as f:
            for mod in self.mods:
                f.write(mod + "\n")

    def select_mod(self, item):
        self.current_mod = item.text()

    # --- Кнопка toggle ---
    def toggle_mods(self):
        if not self.toggle_path or not os.path.exists(self.toggle_path):
            QMessageBox.critical(self, "Помилка", "Не знайдено toggle_darktide_mods.bat")
            return

        try:
            result = subprocess.run(
                [self.toggle_path],
                shell=True,
                capture_output=True,
                text=True
            )
            output = (result.stdout + result.stderr).lower()

            if "unpatched" in output:
                self.mods_enabled = False
                QMessageBox.information(self, "Стан модів", "❌ Моди деактивовані")
            elif "patched" in output:
                self.mods_enabled = True
                QMessageBox.information(self, "Стан модів", "✅ Моди активовані")
            else:
                QMessageBox.information(self, "Стан модів", "ℹ️ Моди залишилися без змін")

            self.update_toggle_button()

        except Exception as e:
            QMessageBox.critical(self, "Помилка", str(e))

    def check_mods_status(self):
        """Перевіряє чи активовані моди при старті"""
        try:
            result = subprocess.run(
                [os.path.join(os.path.dirname(self.toggle_path), "tools", "dtkit-patch"), "--status", "./bundle"],
                cwd=os.path.dirname(self.toggle_path),
                shell=True,
                capture_output=True,
                text=True
            )
            output = (result.stdout + result.stderr).lower()
            if "patched" in output:
                return True
            else:
                return False
        except Exception:
            return False



    def update_toggle_button(self):
        if self.mods_enabled:
            self.toggle_button.setText("Деактивувати моди")
        else:
            self.toggle_button.setText("Активувати моди")


    # --- Запуск гри ---
    def run_game(self):
        steam_exe = os.path.join(self.steam_path, "steam.exe")
        appid = "1361210"  # Darktide

        if os.path.exists(steam_exe):
            try:
                subprocess.Popen([steam_exe, "-applaunch", appid])
                self.statusBar().showMessage("Запускаю Darktide через Steam...")
            except Exception as e:
                self.statusBar().showMessage(f"Помилка запуску: {e}")
        else:
            QMessageBox.critical(self, "Помилка", "Не знайдено steam.exe")

    def toggle_mod_state(self, enable=True):
        current_item = self.mod_list.currentItem()
        if not current_item:
            return
        mod_name = current_item.text().lstrip("-")  # знімаємо можливі --
        changed = False

        with open(self.load_order_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        with open(self.load_order_file, "w", encoding="utf-8") as f:
            for line in lines:
                clean = line.strip().lstrip("-")
                if clean == mod_name:
                    if enable:  # увімкнути
                        new_line = clean + "\n"
                        f.write(new_line)
                        changed = True
                    else:  # вимкнути
                        if not line.strip().startswith("--"):
                            new_line = "--" + clean + "\n"
                            f.write(new_line)
                            changed = True
                        else:
                            f.write(line)  # вже вимкнений
                    continue
                f.write(line)

        if changed:
            if enable:
                QMessageBox.information(self, "Увімкнено", f"Мод {mod_name} увімкнено")
            else:
                QMessageBox.information(self, "Вимкнено", f"Мод {mod_name} виключено")

        self.scan_mods()
    
    def add_existing_mods_multi(self):
        if not os.path.exists(self.mods_dir):
            QMessageBox.warning(self, "Помилка", "Тека з модами не знайдена")
            return

        # усі підтеки в mods/
        all_dirs = [d for d in os.listdir(self.mods_dir)
                    if os.path.isdir(os.path.join(self.mods_dir, d))]

        already = self._names_in_load_order()

        candidates = []
        for d in all_dirs:
            if d.lower() == "dmf":
                continue
            full = os.path.join(self.mods_dir, d)
            has_mod = False
            for root, _, files in os.walk(full):
                if any(f.lower().endswith(".mod") for f in files):
                    has_mod = True
                    break
            if has_mod and d not in already:
                candidates.append(d)

        if not candidates:
            QMessageBox.information(self, "Готово", "Немає нових модів для додавання.")
            return

        dlg = ExistingModsDialog(candidates, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            selected = dlg.selected_names()
            if not selected:
                return
            added = self.append_mods_to_load_order(selected)
            QMessageBox.information(self, "Додано", f"Додано {added} нових мод(ів)")
            self.scan_mods()


    def _names_in_load_order(self) -> set:
        names = set()
        if os.path.exists(self.load_order_file):
            with open(self.load_order_file, "r", encoding="utf-8") as f:
                for line in f:
                    s = line.strip()
                    if not s:
                        continue
                    names.add(s.lstrip("-"))  # ігноруємо коментарі `--`
        return names

    def _ensure_trailing_newline(self, path: str):
        """Фікс: гарантує, що останній рядок закінчується \n (виправляє баг 'slidebase')."""
        if not os.path.exists(path):
            open(path, "w", encoding="utf-8").close()
            return
        with open(path, "rb") as fb:
            fb.seek(0, os.SEEK_END)
            size = fb.tell()
            if size == 0:
                return
            fb.seek(-1, os.SEEK_END)
            last = fb.read(1)
        if last != b"\n":
            with open(path, "ab") as fa:
                fa.write(b"\n")

    def append_mods_to_load_order(self, mod_names: list[str]) -> int:
        existing = self._names_in_load_order()
        to_add = [m for m in mod_names if m not in existing]
        if not to_add:
            return 0
        self._ensure_trailing_newline(self.load_order_file)
        with open(self.load_order_file, "a", encoding="utf-8") as f:
            for m in to_add:
                f.write(m + "\n")
        return len(to_add)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowIcon(QIcon("ico.ico"))
    window.show()
    sys.exit(app.exec())
