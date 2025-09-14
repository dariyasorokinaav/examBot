import telebot
from telebot import types
import random
import os

bot = telebot.TeleBot("8459722040:AAEq7pPAqOx_QRQc7vxtnXW0xhg-N7GGPqA")  # вставь токен сюда

# --- словари заданий ---
tasks_oge = {1: "1. Оценка объёма памяти", 2: "2. Кодирование/декодирование кодовой последовательности",
             3: "3. Определение значения логического высказывания", 4: "4. Анализ моделей реальных объектов",
             5: "5. Анализ алгоритмов заданных исполнителей", 6: "6. Анализ программы с условным оператором",
             7: "7. Построение адреса в сети Интернет", 8: "8. Анализ результатов поиска в сети Интернет",
             9: "9. Анализ информации, представленной в виде схем", 10: "10. Работа с различными системами счисления",
             11: "11. Поиск информации в файлах и файловой системе", 12: "12. Поиск файлов с заданным условием",
             13: "13. Создание презентаций или форматирование текста", 14: "14. Анализ электронных таблиц",
             15: "15. Написание программ для заданного исполнителя",
             16: "16. Написание программы на универсальном языке"}
tasks_ege = {1: "1. Графы – матрица смежности", 2: "2. Алгебра логики – таблицы истинности",
             3: "3. Поиск информации в базе данных", 4: "4. Кодирование и декодирование – условие Фано",
             5: "5. Алгоритмы – анализ простейших алгоритмов", 6: "6. Алгоритмы – определение результата",
             7: "7. Кодирование и декодирование – передача и хранение информации", 8: "8. Комбинаторика",
             9: "9. Работа с электронными таблицами", 10: "10. Поиск информации в текстовом документе",
             11: "11. Кодирование и декодирование – вычисление количества информации",
             12: "12. Алгоритмы – анализ сложных алгоритмов", 13: "13. Организация компьютерных сетей",
             14: "14. Системы счисления", 15: "15. Алгебра логики – преобразование логических выражений",
             16: "16. Рекурсивные алгоритмы", 17: "17. Обработка числовой последовательности",
             18: "18. Работа с электронными таблицами", 19: "19. Теория игр", 20: "20. Теория игр",
             21: "21. Теория игр", 22: "22. Многопроцессорные системы", 23: "23. Оператор присваивания и ветвления",
             24: "24. Обработка символьной информации", 25: "25. Обработка целочисленной информации",
             26: "26. Обработка целочисленной информации с использованием сортировки", 27: "27. Анализ данных"}

TASKS_PER_PAGE = 5  # сколько задач на странице

# состояние для проверки ответов тренировки
# {chat_id: {"answer": str, "level": str, "task_id": str}}
active_training = {}


# ---------- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ----------
def get_tasks_dict(level: str) -> dict:
    """Вернуть словарь заданий по уровню"""
    return tasks_oge if level == "oge" else tasks_ege


def normalize(s: str) -> str:
    """Нормализуем строку"""
    return s.strip().replace(",", ".").casefold()


def answers_equal(a: str, b: str) -> bool:
    """Сравниваем ответы: как числа или как строки"""
    aa, bb = normalize(a), normalize(b)

    def to_float(x):
        try:
            return float(x)
        except:
            return None

    fa, fb = to_float(aa), to_float(bb)
    if fa is not None and fb is not None:
        return abs(fa - fb) < 1e-9
    return aa == bb


# ---------- СТАРТ ----------
@bot.message_handler(commands=['start'])
def choose_level(message):
    bot.send_message(message.chat.id, "СЕЙЧАС ДОСТУПНО: теория по заданию 6 ЕГЭ и тренировка задания 1 ОГЭ")

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("ОГЭ", callback_data="oge"))
    markup.add(types.InlineKeyboardButton("ЕГЭ", callback_data="ege"))
    bot.send_message(message.chat.id, "Выберите уровень подготовки:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "menu")
def back_to_menu(call):
    choose_level(call.message)


# ---------- ВЫБОР ДЕЙСТВИЯ ----------
@bot.callback_query_handler(func=lambda call: call.data in ["oge", "ege"])
def choose_action(call):
    level = call.data
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🧠 Объяснение теории", callback_data=f"theory_{level}_1"))
    markup.add(types.InlineKeyboardButton("🧩 Тренировка", callback_data=f"training_{level}_1"))
    bot.send_message(call.message.chat.id, f"Вы выбрали {level.upper()}. Теперь выберите действие:",
                     reply_markup=markup)


# ------ ПРАВИЛЬНАЯ разметка списка с пагинацией ------
def get_tasks_markup(list_prefix, item_prefix, level, tasks, page):
    markup = types.InlineKeyboardMarkup()
    start = (page - 1) * TASKS_PER_PAGE
    end = start + TASKS_PER_PAGE

    # кнопки задач
    for i in list(tasks.keys())[start:end]:
        markup.add(types.InlineKeyboardButton(tasks[i], callback_data=f"{item_prefix}_{level}_{i}"))

    # кнопки пагинации (ВНИМАНИЕ: используем list_prefix)
    nav = []
    if page > 1:
        nav.append(types.InlineKeyboardButton("⬅ Назад", callback_data=f"{list_prefix}_{level}_{page-1}"))
    if end < len(tasks):
        nav.append(types.InlineKeyboardButton("Вперёд ➡", callback_data=f"{list_prefix}_{level}_{page+1}"))
    if nav:
        markup.row(*nav)

    markup.add(types.InlineKeyboardButton("🏠 В меню", callback_data="menu"))
    return markup


# --- ТЕОРИЯ: показать список ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("theory_"))
def show_theory_tasks(call):
    _, level, page = call.data.split("_")
    page = int(page)
    tasks = get_tasks_dict(level)
    # было: get_tasks_markup("theoryTask", ...)
    markup = get_tasks_markup("theory", "theoryTask", level, tasks, page)
    bot.edit_message_text(f"📚 Теория по {level.upper()}. Страница {page}:",
                          chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          reply_markup=markup)



@bot.callback_query_handler(func=lambda call: call.data.startswith("theoryTask_"))
def send_theory_video(call):
    _, level, task_id = call.data.split("_")
    file_path = f"videos/{level}/{task_id}.mp4"
    try:
        with open(file_path, "rb") as video:
            bot.send_video(call.message.chat.id, video, timeout=600)
    except FileNotFoundError:
        bot.send_message(call.message.chat.id, f"⏳ Видео для {level.upper()} №{task_id} ещё в обработке.")


# --- ТРЕНИРОВКА: показать список ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("training_"))
def show_training_tasks(call):
    _, level, page = call.data.split("_")
    page = int(page)
    tasks = get_tasks_dict(level)
    markup = get_tasks_markup("training", "trainingTask", level, tasks, page)
    bot.edit_message_text(f"🧩 Тренировка по {level.upper()}. Страница {page}:",
                          chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          reply_markup=markup)



def ask_random_training_question(chat_id: int, level: str, task_id: str):
    file_path = f"training/{level}/{task_id}.txt"
    if not os.path.exists(file_path):
        bot.send_message(chat_id, f"⏳ Задание для {level.upper()} №{task_id} ещё в обработке.")
        return False

    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    data_lines = lines[1:] if len(lines) > 1 else []

    if not data_lines:
        bot.send_message(chat_id, f"⚠️ В файле {file_path} нет заданий.")
        return False

    random_line = random.choice(data_lines)
    parts = random_line.split(";", maxsplit=2)
    if len(parts) < 3:
        bot.send_message(chat_id, f"⚠️ Ошибка формата:\n{random_line}")
        return False

    _, task_text, correct_answer = parts[0], parts[1], parts[2]
    active_training[chat_id] = {
        "answer": correct_answer.strip(),
        "level": level,
        "task_id": task_id
    }
    bot.send_message(chat_id,
                     f"🧩 Задание (№{task_id}, {level.upper()}):\n{task_text}\n\n✍ Напиши свой ответ сообщением.")
    return True


@bot.callback_query_handler(func=lambda call: call.data.startswith("trainingTask_"))
def start_training_question(call):
    _, level, task_id = call.data.split("_")
    ask_random_training_question(call.message.chat.id, level, task_id)


@bot.message_handler(func=lambda msg: msg.chat.id in active_training)
def check_training_answer(message):
    info = active_training[message.chat.id]
    correct = info["answer"]
    user_ans = message.text or ""

    if answers_equal(user_ans, correct):
        verdict = "✅ Верно!"
    else:
        verdict = f"❌ Неверно. Правильный ответ: {correct}"

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🎲 Ещё задание", callback_data=f"trainingTask_{info['level']}_{info['task_id']}"))
    markup.add(types.InlineKeyboardButton("🏠 В меню", callback_data="menu"))

    bot.send_message(message.chat.id, f"{verdict}\n\nЧто дальше?", reply_markup=markup)

    del active_training[message.chat.id]


# ---------- ЗАПУСК ----------
bot.polling(none_stop=True)
