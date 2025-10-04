Darktide Mod Handler

Простий застосунок із графічним інтерфейсом для керування модами у грі Warhammer 40,000: Darktide.

📦 Можливості
Автоматичне встановлення модів із архівів .zip та .rar
Додавання існуючих модів із папки mods
Увімкнення / вимкнення модів (рядки у mod_load_order.txt)
Повне видалення модів (папка + запис у списку)
Перевірка наявності файлу .mod у архіві чи папці (щоб уникнути «лівих» архівів)
Інтеграція з Darktide Mod Loader
Кнопка Активувати/Деактивувати моди через toggle_darktide_mods.bat
Зручне відображення стану модів: активні / вимкнені (червоним)
Посилання на Nexus Mods
Можливість запуску гри прямо з програми

🚀 Як встановити
Завантаж DarktideModHandler.zip і розпакуй у зручну теку.
Усередині повинні бути:
DTMH.exe
ico.ico
tools/UnRAR.exe
utils/
Переконайся, що у тебе встановлений Darktide Mod Loader.
Якщо його немає → завантаж із Nexus Mods

Перший запуск програми попросить вказати шлях до toggle_darktide_mods.bat.
При першому запуску програма попросить вказати шлях до Steam (туди, де лежить гра).
Наприклад:
C:\Program Files (x86)\Steam

🛠 Використання
Додати мод (архів)
Натисни «Додати мод» → вибери .zip або .rar.
Програма автоматично розпакує його у Darktide/mods/ та додасть у mod_load_order.txt.
Якщо архів не містить .mod — встановлення скасується.
Додати існуючі моди
Якщо у папці mods/ є моди, але вони ще не у mod_load_order.txt, натисни «Додати існуючі моди» та вибери зі списку.
Увімкнути / Виключити мод
Виділи мод у списку та натисни відповідну кнопку.
Увімкнений мод відображається чорним.
Виключений (рядок із -- у mod_load_order.txt) — червоним.
Видалити мод
Повністю прибирає теку моду та його запис у списку.
Активувати/Деактивувати моди
Викликає toggle_darktide_mods.bat із Darktide Mod Loader.
У спливаючому повідомленні показується стан (моди активні/деактивовані).

Запустити гру
Запускає Darktide напряму.

Відвідати Nexus Mods
Відкриває сторінку модів у браузері.

⚠️ Важливі моменти
Для роботи з архівами .rar потрібен UnRAR.exe.
Він уже в комплекті у папці tools/.
Якщо при запуску exe з’являється помилка про відсутні бібліотеки — переконайся, що в архіві є всі додаткові файли (ico.ico, utils/, tools/UnRAR.exe).
Якщо Windows SmartScreen блокує запуск — натисни «Докладніше» → «Запустити все одно».
📌 Приклад структури після встановлення
DarktideModHandler/
├─ DTMH.exe
├─ ico.ico
├─ tools/
│  └─ UnRAR.exe
├─ utils/
│  └─ ExistingModsDialog.py


🚀 Darktide Mod Handler v1.0
First public release of a lightweight GUI tool for managing mods in Warhammer 40,000: Darktide.

✨ Features
Install mods directly from .zip and .rar archives
Automatic validation — detects .mod files to avoid invalid archives
Add existing mods from your /mods folder
Multi-selection support for adding several mods at once
Enable / disable mods (commenting lines in mod_load_order.txt)
Remove mods completely (both folder and file entry)
Integration with Darktide Mod Loader
One-click Activate / Deactivate Mods button (toggle_darktide_mods.bat)
Displays current mod state (enabled / disabled)
Launch the game directly from the tool
Quick access button to Nexus Mods

🧭 Installation
Download and extract the DarktideModHandler.zip archive.
The folder should contain:
DTMH.exe
ico.ico
tools/UnRAR.exe
utils/
On first launch:
Select your Steam directory (e.g. C:\Program Files (x86)\Steam).
Select your toggle_darktide_mods.bat file from Darktide Mod Loader.
Once configured, the tool will automatically detect and manage your mods.

⚠️ Notes
.rar archives require UnRAR.exe (already included in the /tools folder).
Disabled mods appear in red and are prefixed with -- inside mod_load_order.txt.
If SmartScreen blocks the app, click More info → Run anyway.
