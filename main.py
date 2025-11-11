from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
import asyncio
import datetime
import os
import shutil
import glob
import json

SETTINGS_FILE = 'checker_settings.json'
API_FILE = 'api_config.json'

DEFAULT_SETTINGS = {
    'check_speed': 1,
    'color_primary': '91',
    'color_text': '97'
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return DEFAULT_SETTINGS.copy()
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

def load_api_config():
    if os.path.exists(API_FILE):
        try:
            with open(API_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if 'api_id' in config and 'api_hash' in config:
                    return config['api_id'], config['api_hash']
        except:
            pass
    return None, None

def save_api_config(api_id, api_hash):
    config = {
        'api_id': api_id,
        'api_hash': api_hash
    }
    with open(API_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

settings = load_settings()
api_id, api_hash = load_api_config()

def get_center_position(text):
    terminal_size = shutil.get_terminal_size()
    return (terminal_size.columns - len(text)) // 2

def print_centered(text, color_code=None):
    if color_code is None:
        color_code = settings['color_text']
    centered_text = " " * get_center_position(text) + text
    print(f"\033[{color_code}m{centered_text}\033[0m")

def print_centered_multiline(lines, color_code=None):
    if color_code is None:
        color_code = settings['color_text']
    max_length = max(len(line) for line in lines)
    center_pos = (shutil.get_terminal_size().columns - max_length) // 2
    
    for line in lines:
        centered_line = " " * center_pos + line
        print(f"\033[{color_code}m{centered_line}\033[0m")

def print_centered_line(length=50):
    terminal_size = shutil.get_terminal_size()
    line = "=" * length
    center_pos = (terminal_size.columns - length) // 2
    centered_line = " " * center_pos + line
    print(f"\033[{settings['color_primary']}m{centered_line}\033[0m")

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    banner_lines = [
        "░█████╗░██╗░░██╗███████╗██╗░░██╗███████╗██████╗░",
        "██╔══██╗██║░░██║██╔════╝██║░██╔╝██╔════╝██╔══██╗",
        "██║░░╚═╝███████║█████╗░░█████═╝░█████╗░░██████╔╝",
        "██║░░██╗██╔══██║██╔══╝░░██╔═██╗░██╔══╝░░██╔══██╗",
        "╚█████╔╝██║░░██║███████╗██║░╚██╗███████╗██║░░██║",
        "░╚════╝░╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝"
    ]
    
    for line in banner_lines:
        print_centered(line, settings['color_primary'])

def print_menu_option(number, text):
    menu_text = f"\033[{settings['color_primary']}m[\033[{settings['color_text']}m{number}\033[{settings['color_primary']}m]\033[{settings['color_text']}m {text}"
    print_centered(menu_text)

def setup_api_config():
    global api_id, api_hash
    
    clear_console()
    print_banner()
    print_centered_line(50)
    print_centered("⚙️ НАСТРОЙКА API ДАННЫХ")
    print_centered_line(50)
    print()
    print_centered("Для работы программы необходимы API данные")
    print_centered("Получите их на https://my.telegram.org")
    print()
    print_centered_line(50)
    print()
    
    try:
        api_id_input = input(" " * get_center_position("Введите API ID: ") + "\033[97mВведите API ID: \033[0m").strip()
        api_hash_input = input(" " * get_center_position("Введите API Hash: ") + "\033[97mВведите API Hash: \033[0m").strip()
        
        api_id = int(api_id_input)
        api_hash = api_hash_input
        
        save_api_config(api_id, api_hash)
        
        print()
        print_centered("✓ API данные успешно сохранены!", settings['color_primary'])
        print_centered("Теперь можно использовать программу", settings['color_text'])
        print()
        print_centered_line(50)
        
        input("\n" + " " * get_center_position("Нажмите Enter для продолжения...") + "\033[97mНажмите Enter для продолжения...\033[0m")
        return True
        
    except ValueError:
        print()
        print_centered("✗ Ошибка: API ID должен быть числом!", settings['color_primary'])
        input("\n" + " " * get_center_position("Нажмите Enter для повторной попытки...") + "\033[97mНажмите Enter для повторной попытки...\033[0m")
        return False
    except Exception as e:
        print()
        print_centered(f"✗ Ошибка: {e}", settings['color_primary'])
        input("\n" + " " * get_center_position("Нажмите Enter для повторной попытки...") + "\033[97mНажмите Enter для повторной попытки...\033[0m")
        return False

async def check_username(client, username):
    try:
        await client.get_entity(username)
        return False, "занят"
    except ValueError:
        return True, "свободен"
    except Exception as e:
        return False, "на продаже"

def get_display_name(filename):
    base_name = filename.replace('.txt', '')
    parts = base_name.split('_')
    
    if len(parts) >= 3:
        username = parts[0]
        start = parts[1]
        end = parts[2]
        return f"{username} {start}-{end}"
    else:
        return base_name

def show_settings():
    while True:
        clear_console()
        print_banner()
        print_centered_line(50)
        print_centered("⚙️ НАСТРОЙКИ")
        print_centered_line(50)
        print()
        
        print_centered(f"Скорость проверки: \033[{settings['color_primary']}m{settings['check_speed']}s\033[{settings['color_text']}m")
        print_centered(f"Основной цвет: \033[{settings['color_primary']}m{settings['color_primary']}\033[{settings['color_text']}m")
        print()
        
        menu_lines = [
            f"\033[{settings['color_primary']}m[\033[{settings['color_text']}m1\033[{settings['color_primary']}m]\033[{settings['color_text']}m Изменить скорость проверки",
            f"\033[{settings['color_primary']}m[\033[{settings['color_text']}m2\033[{settings['color_primary']}m]\033[{settings['color_text']}m Изменить цвет",
            f"\033[{settings['color_primary']}m[\033[{settings['color_text']}m3\033[{settings['color_primary']}m]\033[{settings['color_text']}m Назад"
        ]
        
        print_centered_multiline(menu_lines)
        print()
        print_centered_line(50)
        
        choice = input(" " * get_center_position("Выберите действие [1-3]: ") + f"\033[97mВыберите действие [1-3]: \033[0m").strip()
        
        if choice == '1':
            clear_console()
            print_banner()
            print_centered_line(50)
            print_centered("ИЗМЕНЕНИЕ СКОРОСТИ ПРОВЕРКИ")
            print_centered_line(50)
            print()
            
            try:
                speed = float(input(" " * get_center_position("Введите скорость проверки (секунды): ") + "\033[97mВведите скорость проверки (секунды): \033[0m").strip())
                if 0.1 <= speed <= 10:
                    settings['check_speed'] = speed
                    save_settings(settings)
                    print_centered("✓ Скорость изменена!", settings['color_primary'])
                else:
                    print_centered("✗ Скорость должна быть от 0.1 до 10 секунд")
            except ValueError:
                print_centered("✗ Введите корректное число")
            
            input("\n" + " " * get_center_position("Нажмите Enter для продолжения...") + "\033[97mНажмите Enter для продолжения...\033[0m")
            
        elif choice == '2':
            clear_console()
            print_banner()
            print_centered_line(50)
            print_centered("ИЗМЕНЕНИЕ ЦВЕТА")
            print_centered_line(50)
            print()
            print_centered("91: Красный | 92: Зеленый | 93: Желтый")
            print_centered("94: Синий | 95: Пурпурный | 96: Голубой | 97: Белый")
            print()
            
            color = input(" " * get_center_position("Введите цветовой код (91-97): ") + "\033[97mВведите цветовой код (91-97): \033[0m").strip()
            
            if color in ['91', '92', '93', '94', '95', '96', '97']:
                settings['color_primary'] = color
                save_settings(settings)
                print_centered("✓ Цвет изменен!", settings['color_primary'])
            else:
                print_centered("✗ Неверный цветовой код")
            
            input("\n" + " " * get_center_position("Нажмите Enter для продолжения...") + "\033[97mНажмите Enter для продолжения...\033[0m")
            
        elif choice == '3':
            break
        else:
            print_centered("✗ Неверный выбор! Попробуйте снова.")
            input("\n" + " " * get_center_position("Нажмите Enter для продолжения...") + "\033[97mНажмите Enter для продолжения...\033[0m")

def show_history():
    clear_console()
    print_banner()
    print_centered_line(50)
    print_centered("📜 ИСТОРИЯ ПРОВЕРОК")
    print_centered_line(50)
    print()
    
    history_files = glob.glob("*.txt")
    
    if not history_files:
        print_centered("😞 История пуста")
        print_centered("Сначала выполните проверку юзернеймов")
        return
    
    print_centered("Доступные проверки:")
    print()
    
    menu_lines = []
    for i, filename in enumerate(history_files, 1):
        display_name = get_display_name(filename)
        menu_line = f"\033[{settings['color_primary']}m[\033[{settings['color_text']}m{i}\033[{settings['color_primary']}m]\033[{settings['color_text']}m {display_name}"
        menu_lines.append(menu_line)
    
    print_centered_multiline(menu_lines)
    print()
    print_centered_line(50)
    
    try:
        choice = input(" " * get_center_position(f"Выберите проверку [1-{len(history_files)}]: ") + f"\033[97mВыберите проверку [1-{len(history_files)}]: \033[0m").strip()
        
        file_index = int(choice) - 1
        
        if 0 <= file_index < len(history_files):
            selected_file = history_files[file_index]
            display_name = get_display_name(selected_file)
            
            clear_console()
            print_banner()
            print_centered_line(50)
            print_centered(f"📄 {display_name}")
            print_centered_line(50)
            print()
            
            try:
                with open(selected_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    for line in lines:
                        if line.strip():
                            if '=' in line:
                                line = "=" * 50
                                centered_line = " " * get_center_position(line) + line
                                print(f"\033[{settings['color_primary']}m{centered_line}\033[0m")
                            else:
                                print_centered(line)
            except Exception as e:
                print_centered(f"✗ Ошибка чтения файла: {e}")
        else:
            print_centered("✗ Неверный выбор!")
    
    except ValueError:
        print_centered("✗ Введите корректный номер!")
    except Exception as e:
        print_centered(f"✗ Ошибка: {e}")

async def username_checker():
    if api_id is None or api_hash is None:
        print_centered("✗ API данные не настроены!")
        print_centered("Запустите настройку API данных из меню")
        return
    
    client = TelegramClient('session_name', api_id, api_hash)
    
    try:
        await client.connect()
        
        if not await client.is_user_authorized():
            clear_console()
            print_banner()
            print_centered_line(50)
            print_centered("🔐 АВТОРИЗАЦИЯ В TELEGRAM")
            print_centered_line(50)
            print()
            
            phone = input(" " * get_center_position("Введите ваш номер телефона: ") + "\033[97mВведите ваш номер телефона: \033[0m").strip()
            
            try:
                await client.send_code_request(phone)
                print_centered("✓ Код отправлен!", settings['color_primary'])
            except Exception as e:
                print_centered(f"✗ Ошибка отправки кода: {e}")
                return
            
            code = input(" " * get_center_position("Введите код из Telegram: ") + "\033[97mВведите код из Telegram: \033[0m").strip()
            
            try:
                await client.sign_in(phone, code)
                print_centered("✓ Успешная авторизация!", settings['color_primary'])
                
            except SessionPasswordNeededError:
                print_centered("🔒 Требуется пароль двухфакторной аутентификации")
                password = input(" " * get_center_position("Введите пароль 2FA: ") + "\033[97mВведите пароль 2FA: \033[0m")
                try:
                    await client.sign_in(password=password)
                    print_centered("✓ Успешная авторизация с 2FA!", settings['color_primary'])
                except Exception as e:
                    print_centered(f"✗ Ошибка входа с паролем: {e}")
                    return
                    
            except PhoneCodeInvalidError:
                print_centered("✗ Неверный код! Попробуйте снова.")
                return
            except Exception as e:
                print_centered(f"✗ Ошибка авторизации: {e}")
                return
        
        clear_console()
        print_banner()
        print_centered_line(50)
        print_centered("🔍 ПРОВЕРКА ЮЗЕРНЕЙМОВ")
        print_centered_line(50)
        print()
        
        base_username = input(" " * get_center_position("Введите базовый юзернейм: ") + "\033[97mВведите базовый юзернейм: \033[0m").strip()
        
        try:
            start_num = int(input(" " * get_center_position("Начальная цифра: ") + "\033[97mНачальная цифра: \033[0m"))
            end_num = int(input(" " * get_center_position("Конечная цифра: ") + "\033[97mКонечная цифра: \033[0m"))
        except ValueError:
            print_centered("✗ Ошибка: введите корректные числа!")
            return
        
        print()
        print_centered(f"🔍 Проверяю юзернеймы: {base_username}[{start_num}-{end_num}]")
        print_centered_line(50)
        
        available_usernames = []
        total_checked = 0
        
        if start_num == 0:
            username_without_number = base_username
            total_checked += 1
            
            is_available, status = await check_username(client, username_without_number)
            
            if is_available:
                print_centered(f"✅ {username_without_number} - СВОБОДЕН")
                available_usernames.append(username_without_number)
            else:
                print_centered(f"❌ {username_without_number} - {status}")
            
            await asyncio.sleep(settings['check_speed'])
        
        for num in range(start_num, end_num + 1):
            username = f"{base_username}{num}"
            total_checked += 1
            
            is_available, status = await check_username(client, username)
            
            if is_available:
                print_centered(f"✅ {username} - СВОБОДЕН")
                available_usernames.append(username)
            else:
                print_centered(f"❌ {username} - {status}")
            
            await asyncio.sleep(settings['check_speed'])
        
        print_centered_line(50)
        print_centered("📊 РЕЗУЛЬТАТЫ ПРОВЕРКИ:")
        print_centered_line(50)
        print_centered(f"Всего проверено: \033[{settings['color_primary']}m{total_checked}\033[{settings['color_text']}m")
        print_centered(f"Свободных: \033[{settings['color_primary']}m{len(available_usernames)}\033[{settings['color_text']}m")
        print_centered(f"Занятых: \033[{settings['color_primary']}m{total_checked - len(available_usernames)}\033[{settings['color_text']}m")
        
        if available_usernames:
            filename = f"{base_username}_{start_num}_{end_num}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Свободные юзернеймы: {base_username}[{start_num}-{end_num}]\n")
                f.write("=" * 50 + "\n")
                for username in available_usernames:
                    f.write(f"{username}\n")
            
            print_centered(f"💾 Результаты сохранены в файл: \033[{settings['color_primary']}m{filename}\033[{settings['color_text']}m")
            print()
            print_centered("📋 Свободные юзернеймы:")
            for username in available_usernames:
                print_centered(f"   • \033[{settings['color_primary']}m{username}\033[{settings['color_text']}m")
        
        else:
            print_centered("😞 Свободных юзернеймов не найдено")
            
    except Exception as e:
        print_centered(f"✗ Произошла ошибка: {e}")
    finally:
        await client.disconnect()

def about_program():
    clear_console()
    print_banner()
    print_centered_line(50)
    print_centered("📝 О ПРОГРАММЕ")
    print_centered_line(50)
    print()
    print_centered(f"Создатель: \033[{settings['color_primary']}mFunPayBad\033[{settings['color_text']}m")
    print_centered(f"Канал: \033[{settings['color_primary']}m@FunPayBad\033[{settings['color_text']}m")
    print_centered(f"Версия: \033[{settings['color_primary']}m1.1\033[{settings['color_text']}m")
    print_centered(f"Тип программы: \033[{settings['color_primary']}mбесплатная\033[{settings['color_text']}m")
    print_centered(f"Тех поддержка: \033[{settings['color_primary']}m@woriot\033[{settings['color_text']}m")
    print_centered(f"Дешевый магазин: \033[{settings['color_primary']}m@FreeShopGo\033[{settings['color_text']}m")
    print_centered_line(50)

async def main():
    if api_id is None or api_hash is None:
        while not setup_api_config():
            pass
    
    while True:
        clear_console()
        print_banner()
        print_centered_line(50)
        print_centered("🎮 ГЛАВНОЕ МЕНЮ")
        print_centered_line(50)
        print()
        
        menu_lines = [
            f"\033[{settings['color_primary']}m[\033[{settings['color_text']}m1\033[{settings['color_primary']}m]\033[{settings['color_text']}m 🔍 Чекер юзернеймов",
            f"\033[{settings['color_primary']}m[\033[{settings['color_text']}m2\033[{settings['color_primary']}m]\033[{settings['color_text']}m 📜 История",
            f"\033[{settings['color_primary']}m[\033[{settings['color_text']}m3\033[{settings['color_primary']}m]\033[{settings['color_text']}m ⚙️ Настройки",
            f"\033[{settings['color_primary']}m[\033[{settings['color_text']}m4\033[{settings['color_primary']}m]\033[{settings['color_text']}m 📝 О программе",
            f"\033[{settings['color_primary']}m[\033[{settings['color_text']}m5\033[{settings['color_primary']}m]\033[{settings['color_text']}m 🚪 Выход"
        ]
        
        print_centered_multiline(menu_lines)
        print()
        print_centered_line(50)
        
        choice = input(" " * get_center_position("Выберите действие [1-5]: ") + f"\033[97mВыберите действие [1-5]: \033[0m").strip()
        
        if choice == '1':
            await username_checker()
        elif choice == '2':
            show_history()
        elif choice == '3':
            show_settings()
        elif choice == '4':
            about_program()
        elif choice == '5':
            clear_console()
            print_banner()
            print_centered_line(50)
            print_centered("👋 До свидания!")
            print_centered_line(50)
            break
        else:
            print_centered("✗ Неверный выбор! Попробуйте снова.")
        
        if choice != '5':
            input("\n" + " " * get_center_position("Нажмите Enter для продолжения...") + "\033[97mНажмите Enter для продолжения...\033[0m")

if __name__ == '__main__':
    clear_console()
    print_centered("Запуск Checker...")
    asyncio.run(main())