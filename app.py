#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import webbrowser
import threading
import time
import sys
import os
from dashboard import app

server = app.server

def open_browser():
    """Открывает браузер через 2 секунды после запуска сервера"""
    time.sleep(2)
    webbrowser.open('http://127.0.0.1:8050/')

def main():
    PORT = 8050
    
    print("=" * 80)
    print("🇫🇮 ДАШБОРД ВНЕШНЕЙ ТОРГОВЛИ ФИНЛЯНДИИ")
    print("=" * 80)
    print(f"📡 Запуск Dash-приложения на порту {PORT}...")
    print(f"🌐 URL: http://127.0.0.1:{PORT}/")
    print("=" * 80)
    
    # Проверяем наличие необходимых файлов
    required_files = [
        "dashboard.py",
        "trade.csv",
        "countries.csv",
        "commodities.csv"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ ОШИБКА: Отсутствуют необходимые файлы:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print("Пожалуйста, убедитесь, что все файлы созданы корректно.")
        sys.exit(1)
    
    # Запускаем браузер в отдельном потоке
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    try:
        # Импортируем и запускаем Dash приложение
        from dashboard import app
        
        print(f"✅ Dash-приложение успешно запущено!")
        print(f"📂 Рабочая директория: {os.getcwd()}")
        print(f"🔗 Откроется в браузере через 2 секунды...")
        print(f"⏹️  Для остановки нажмите Ctrl+C")
        print("=" * 80)
        
        app.run(debug=False, port=PORT, host='0.0.0.0')
        
    except ImportError as e:
        print(f"❌ ОШИБКА ИМПОРТА: {e}")
        print("Убедитесь, что установлены все зависимости:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n" + "=" * 80)
        print("🛑 Сервер остановлен пользователем")
        print("=" * 80)
    except Exception as e:
        print(f"❌ НЕОЖИДАННАЯ ОШИБКА: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
