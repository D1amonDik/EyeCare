"""
localization.py - Система локализации для Eye Care
Поддерживает: English (по умолчанию), Русский, Українська
"""

TRANSLATIONS = {
    "en": {
        # Main window
        "app_name": "Eye Care",
        "tray_breaks_today": "breaks today",
        
        # Menu
        "menu_settings": "Settings",
        "menu_break_now": "Break Now",
        "menu_reset_timer": "Reset Timer",
        "menu_exit": "Exit",
        
        # Settings window
        "settings_title": "Eye Care — Settings",
        "tab_timer": "⏱ Timer",
        "tab_appearance": "🎨 Appearance",
        "tab_behavior": "⚙ Behavior",
        "tab_stats": "📊 Statistics",
        
        # Timer tab
        "work_time": "Work Time",
        "rest_time": "Rest Time",
        "smart_pause": "Smart Pause",
        "smart_pause_desc": "Pause when user is idle",
        "threshold": "Threshold:",
        "minutes": "min",
        "seconds": "sec",
        
        # Appearance tab
        "color_scheme": "Color Scheme",
        "custom_hex": "Custom HEX:",
        "pick": "Pick",
        "opacity": "Overlay Opacity",
        "opacity_hint": "Click 'Test' → window appears → move slider to see effect",
        "test": "Test",
        "sound": "Sound",
        "sound_alert": "⚠ Alert",
        "sound_beep": "📢 Beep",
        "sound_custom": "📁 Custom File",
        "sound_none": "🔇 No Sound",
        "sound_file": "File:",
        "browse": "Browse",
        
        # Behavior tab
        "overlay_mode": "Overlay Mode",
        "fullscreen_mode": "Fullscreen Mode",
        "strict_mode": "Strict Mode (no close button)",
        "system": "System",
        "autostart": "Autostart with Windows",
        "smart_detect": "Don't interrupt fullscreen apps",
        "monitor": "Monitor",
        "all_monitors": "All Monitors",
        "language": "Language",
        
        # Statistics tab
        "today": "Today",
        "breaks": "breaks",
        "goal": "goal",
        "total_all_time": "Total all time:",
        "last_7_days": "Last 7 Days",
        "reset_stats": "Reset Statistics",
        
        # Buttons
        "save": "Save",
        "cancel": "Cancel",
        "reset": "🔄 Reset",
        "preview": "▶ Preview",
        
        # Overlay
        "eye_rest_time": "👁   Eye Rest Time",
        "seconds_remaining": "seconds remaining",
        "skip": "Skip",
        
        # Exercises
        "exercise_rotation": "👁  Rotation",
        "exercise_rotation_desc": "Slowly rotate your eyes clockwise 10 times,\nthen counterclockwise 10 times.",
        "exercise_distance": "🎯  Focus Far",
        "exercise_distance_desc": "Find an object 20 feet (6 meters) away\nand look at it for the entire break.",
        "exercise_blinking": "🌟  Blinking",
        "exercise_blinking_desc": "Blink rapidly and consciously 20 times in a row.\nThis moisturizes the cornea and relieves tension.",
        "exercise_horizontal": "↔  Horizontal",
        "exercise_horizontal_desc": "Without moving your head, look as far left as possible,\nthen right. Repeat 10 times.",
        "exercise_vertical": "↕  Vertical",
        "exercise_vertical_desc": "Look as far up as possible,\nthen down, without turning your head. 10 times.",
        "exercise_eight": "🌀  Figure Eight",
        "exercise_eight_desc": "Imagine a horizontal figure eight in front of you\nand slowly trace it with your eyes 5 times.",
        "exercise_palming": "🖐  Palming",
        "exercise_palming_desc": "Close your eyes and cover them with warm palms.\nRelax completely in the darkness.",
        "exercise_near_far": "🔭  Near-Far",
        "exercise_near_far_desc": "Look at your fingertip for 5 seconds,\nthen look into the distance. Repeat 5 times.",
        
        # Messages
        "saved": "✓ Settings Saved",
        "reset_confirm": "Reset Settings",
        "reset_message": "Reset all settings to default values?\n\nThis will reset:\n- Work and rest time\n- Color scheme\n- Sounds\n- Break window position\n- All other parameters\n\nSettings window size will be preserved.",
        "reset_stats_confirm": "Reset all statistics?",
        "stats_reset": "Statistics reset.",
        "error": "Error",
        "sound_error": "For MP3/OGG playback, pygame is required.\nInstall: pip install pygame",
        "file_not_found": "File not found!",
        "sound_play_error": "Could not play:",
    },
    
    "ru": {
        # Main window
        "app_name": "Eye Care",
        "tray_breaks_today": "перерывов сегодня",
        
        # Menu
        "menu_settings": "Настройки",
        "menu_break_now": "Перерыв сейчас",
        "menu_reset_timer": "Сбросить таймер",
        "menu_exit": "Выход",
        
        # Settings window
        "settings_title": "Eye Care — Настройки",
        "tab_timer": "⏱ Таймер",
        "tab_appearance": "🎨 Внешний вид",
        "tab_behavior": "⚙ Поведение",
        "tab_stats": "📊 Статистика",
        
        # Timer tab
        "work_time": "Время работы",
        "rest_time": "Время отдыха",
        "smart_pause": "Умная пауза",
        "smart_pause_desc": "Пауза при бездействии пользователя",
        "threshold": "Порог:",
        "minutes": "мин",
        "seconds": "сек",
        
        # Appearance tab
        "color_scheme": "Цветовая схема",
        "custom_hex": "Custom HEX:",
        "pick": "Выбрать",
        "opacity": "Прозрачность overlay",
        "opacity_hint": "Нажми «Тест» → появится окошко → двигай ползунок чтобы видеть эффект",
        "test": "Тест",
        "sound": "Звук",
        "sound_alert": "⚠ Внимание",
        "sound_beep": "📢 Beep",
        "sound_custom": "📁 Свой файл",
        "sound_none": "🔇 Без звука",
        "sound_file": "Файл:",
        "browse": "Обзор",
        
        # Behavior tab
        "overlay_mode": "Режим overlay",
        "fullscreen_mode": "Полноэкранный режим",
        "strict_mode": "Strict Mode (нет кнопки закрытия)",
        "system": "Система",
        "autostart": "Автозагрузка при старте Windows",
        "smart_detect": "Не прерывать полноэкранные приложения",
        "monitor": "Монитор",
        "all_monitors": "Все мониторы",
        "language": "Язык",
        
        # Statistics tab
        "today": "Сегодня",
        "breaks": "перерывов",
        "goal": "цель",
        "total_all_time": "Всего за всё время:",
        "last_7_days": "За 7 дней",
        "reset_stats": "Сбросить статистику",
        
        # Buttons
        "save": "Сохранить",
        "cancel": "Отмена",
        "reset": "🔄 Сброс",
        "preview": "▶ Предпросмотр",
        
        # Overlay
        "eye_rest_time": "👁   Время отдыха для глаз",
        "seconds_remaining": "секунд до конца перерыва",
        "skip": "Пропустить",
        
        # Exercises
        "exercise_rotation": "👁  Вращение",
        "exercise_rotation_desc": "Медленно вращайте глазами по часовой стрелке 10 раз,\nзатем столько же против часовой.",
        "exercise_distance": "🎯  Фокусировка вдаль",
        "exercise_distance_desc": "Найдите объект на расстоянии 6 метров\nи смотрите на него всё время перерыва.",
        "exercise_blinking": "🌟  Моргание",
        "exercise_blinking_desc": "Быстро и осознанно моргните 20 раз подряд.\nЭто увлажняет роговицу и снимает напряжение.",
        "exercise_horizontal": "↔  По горизонтали",
        "exercise_horizontal_desc": "Не двигая головой, переведите взгляд максимально\nвлево, затем вправо. Повторите 10 раз.",
        "exercise_vertical": "↕  По вертикали",
        "exercise_vertical_desc": "Переведите взгляд максимально вверх,\nзатем вниз, не поворачивая голову. 10 раз.",
        "exercise_eight": "🌀  Восьмёрка",
        "exercise_eight_desc": "Представьте перед собой горизонтальную восьмёрку\nи медленно обводите её взглядом 5 раз.",
        "exercise_palming": "🖐  Пальминг",
        "exercise_palming_desc": "Закройте глаза и прикройте их тёплыми ладонями.\nРасслабьтесь полностью в темноте.",
        "exercise_near_far": "🔭  Ближе–дальше",
        "exercise_near_far_desc": "Смотрите на кончик пальца 5 секунд,\nзатем переводите взгляд вдаль. Повторите 5 раз.",
        
        # Messages
        "saved": "✓ Настройки сохранены",
        "reset_confirm": "Сброс настроек",
        "reset_message": "Вернуть все настройки к значениям по умолчанию?\n\nЭто сбросит:\n- Время работы и отдыха\n- Цветовую схему\n- Звуки\n- Позицию окна перерыва\n- Все остальные параметры\n\nРазмер окна настроек сохранится.",
        "reset_stats_confirm": "Сбросить всю статистику?",
        "stats_reset": "Статистика сброшена.",
        "error": "Ошибка",
        "sound_error": "Для воспроизведения MP3/OGG нужен pygame.\nУстановите: pip install pygame",
        "file_not_found": "Файл не найден!",
        "sound_play_error": "Не удалось воспроизвести:",
    },
    
    "ua": {
        # Main window
        "app_name": "Eye Care",
        "tray_breaks_today": "перерв сьогодні",
        
        # Menu
        "menu_settings": "Налаштування",
        "menu_break_now": "Перерва зараз",
        "menu_reset_timer": "Скинути таймер",
        "menu_exit": "Вихід",
        
        # Settings window
        "settings_title": "Eye Care — Налаштування",
        "tab_timer": "⏱ Таймер",
        "tab_appearance": "🎨 Зовнішній вигляд",
        "tab_behavior": "⚙ Поведінка",
        "tab_stats": "📊 Статистика",
        
        # Timer tab
        "work_time": "Час роботи",
        "rest_time": "Час відпочинку",
        "smart_pause": "Розумна пауза",
        "smart_pause_desc": "Пауза при бездіяльності користувача",
        "threshold": "Поріг:",
        "minutes": "хв",
        "seconds": "сек",
        
        # Appearance tab
        "color_scheme": "Колірна схема",
        "custom_hex": "Custom HEX:",
        "pick": "Вибрати",
        "opacity": "Прозорість overlay",
        "opacity_hint": "Натисни «Тест» → з'явиться вікно → рухай повзунок щоб побачити ефект",
        "test": "Тест",
        "sound": "Звук",
        "sound_alert": "⚠ Увага",
        "sound_beep": "📢 Beep",
        "sound_custom": "📁 Свій файл",
        "sound_none": "🔇 Без звуку",
        "sound_file": "Файл:",
        "browse": "Огляд",
        
        # Behavior tab
        "overlay_mode": "Режим overlay",
        "fullscreen_mode": "Повноекранний режим",
        "strict_mode": "Strict Mode (немає кнопки закриття)",
        "system": "Система",
        "autostart": "Автозавантаження при старті Windows",
        "smart_detect": "Не переривати повноекранні додатки",
        "monitor": "Монітор",
        "all_monitors": "Всі монітори",
        "language": "Мова",
        
        # Statistics tab
        "today": "Сьогодні",
        "breaks": "перерв",
        "goal": "ціль",
        "total_all_time": "Всього за весь час:",
        "last_7_days": "За 7 днів",
        "reset_stats": "Скинути статистику",
        
        # Buttons
        "save": "Зберегти",
        "cancel": "Скасувати",
        "reset": "🔄 Скинути",
        "preview": "▶ Попередній перегляд",
        
        # Overlay
        "eye_rest_time": "👁   Час відпочинку для очей",
        "seconds_remaining": "секунд до кінця перерви",
        "skip": "Пропустити",
        
        # Exercises
        "exercise_rotation": "👁  Обертання",
        "exercise_rotation_desc": "Повільно обертайте очима за годинниковою стрілкою 10 разів,\nпотім стільки ж проти годинникової.",
        "exercise_distance": "🎯  Фокусування вдалину",
        "exercise_distance_desc": "Знайдіть об'єкт на відстані 6 метрів\nі дивіться на нього весь час перерви.",
        "exercise_blinking": "🌟  Моргання",
        "exercise_blinking_desc": "Швидко і свідомо моргніть 20 разів підряд.\nЦе зволожує рогівку і знімає напругу.",
        "exercise_horizontal": "↔  По горизонталі",
        "exercise_horizontal_desc": "Не рухаючи головою, переведіть погляд максимально\nвліво, потім вправо. Повторіть 10 разів.",
        "exercise_vertical": "↕  По вертикалі",
        "exercise_vertical_desc": "Переведіть погляд максимально вгору,\nпотім вниз, не повертаючи голову. 10 разів.",
        "exercise_eight": "🌀  Вісімка",
        "exercise_eight_desc": "Уявіть перед собою горизонтальну вісімку\nі повільно обводьте її поглядом 5 разів.",
        "exercise_palming": "🖐  Пальмінг",
        "exercise_palming_desc": "Закрийте очі і прикрийте їх теплими долонями.\nРозслабтеся повністю в темряві.",
        "exercise_near_far": "🔭  Ближче–далі",
        "exercise_near_far_desc": "Дивіться на кінчик пальця 5 секунд,\nпотім переводьте погляд вдалину. Повторіть 5 разів.",
        
        # Messages
        "saved": "✓ Налаштування збережено",
        "reset_confirm": "Скидання налаштувань",
        "reset_message": "Повернути всі налаштування до значень за замовчуванням?\n\nЦе скине:\n- Час роботи і відпочинку\n- Колірну схему\n- Звуки\n- Позицію вікна перерви\n- Всі інші параметри\n\nРозмір вікна налаштувань збережеться.",
        "reset_stats_confirm": "Скинути всю статистику?",
        "stats_reset": "Статистику скинуто.",
        "error": "Помилка",
        "sound_error": "Для відтворення MP3/OGG потрібен pygame.\nВстановіть: pip install pygame",
        "file_not_found": "Файл не знайдено!",
        "sound_play_error": "Не вдалося відтворити:",
    }
}


def get_text(key: str, lang: str = "en") -> str:
    """Получает переведенный текст по ключу."""
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)


def get_language_name(lang_code: str) -> str:
    """Возвращает название языка."""
    names = {
        "en": "English",
        "ru": "Русский",
        "ua": "Українська"
    }
    return names.get(lang_code, "English")
