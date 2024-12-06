from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Вопросы и ответы для бота
FAQ = {
    "Посетители": [
        {"question": "Можно ли приглашать гостей?", "answer": """Проход гостей осуществляется:
Для студента Политеха -  по студенческому билету. 
Для прямых родственников - по паспорту. 
Для иных гостей - по заявлению на пропуск гостя, подписанному у Специалиста по работе с молодежью.
Ответственность за приглашенного гостя возглагается на проживающего.
Гости должны покинуть общежитие до 23.00."""},
        {"question": "В какое время разрешён проход гостей в общежитие?", "answer": "Посещение гостями проживающих в студгородке разрешено с 10:00 до 23:00."},
        {"question": "На сколько дней разрешено пребывание прямых родственников в студгородке?", "answer": "Пребывание прямых родственников в студгородке допускается до 3-х суток один раз в месяц по заявлению, одобренному администрацией студгородка. "},
        {"question": "Сколько гостей можно приглашать одновременно?", "answer": "Не более двух человек."}

    ],
    "Внутренний распорядок": [
        {"question": "Как организована уборка в общежитии? Кто за это отвечает?", "answer": "Все проживающие студгородка обязаны соблюдать чистоту и порядок в жилых помещениях и местах общего"},
        {"question": "Можно ли привозить своих животных в общежитие?", "answer": "Содержать на территории студгородка любых животных категорически завершено"},
        {"question": "Можно ли хранить велосипеды или другие крупные предметы в общежитии?", "answer": "Да, только в специально отведенных местах."}
    ],
"Стоимость": [
        {"question": "Сколько стоит проживание в общежитии?", "answer": "Стоимость зависит от того на бюджетной или платной основе обучается студент, а также от местоположения общежития. Для студентов по программам бакалавриата, специалитета, магистратуры, слушатели подготовительного отделения цена варьируется от 1001 до 1314 рублей. Для студентов по программам подготовки научно-педагогических кадров от 1900 до 2800. Для студентов, обучающихся на платной договорной основе по очной форме, стоимость будет ваирьироваться от 2700 до 5500 рублей. Для слушателей ФПК, ДОП - от 1000 до 1600 рублей. ."}
    ]
}

# Генерация клавиатуры для выбора темы
def generate_topics_keyboard():
    topics = list(FAQ.keys())
    keyboard = [[InlineKeyboardButton(topic, callback_data=f"topic_{topic}")] for topic in topics]
    return InlineKeyboardMarkup(keyboard)

# Генерация клавиатуры для переключения вопросов
def generate_questions_keyboard(page, topic):
    keyboard = []
    if page > 0:
        keyboard.append(InlineKeyboardButton("Назад", callback_data=f"page_{topic}_{page - 1}"))
    if (page + 1) * 3 < len(FAQ[topic]):
        keyboard.append(InlineKeyboardButton("Далее", callback_data=f"page_{topic}_{page + 1}"))
    keyboard.append(InlineKeyboardButton("К выбору темы", callback_data="back_to_topics"))
    return InlineKeyboardMarkup([keyboard])

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Это бот FAQ по общежитию. Выберите тему:",
        reply_markup=generate_topics_keyboard()
    )

# Обработка выбора темы
async def choose_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    topic = query.data.split("_")[1]
    context.user_data["current_topic"] = topic
    await send_questions_page(update, context, topic, 0)

# Отправка страницы с вопросами
async def send_questions_page(update: Update, context: ContextTypes.DEFAULT_TYPE, topic, page):
    query = update.callback_query
    questions = FAQ[topic]
    start_idx = page * 3
    end_idx = min(start_idx + 3, len(questions))
    text = f"Тема: {topic}\n\n" + "\n\n".join(
        [f"{i + 1}. {questions[i]['question']}\nОтвет: {questions[i]['answer']}" for i in range(start_idx, end_idx)]
    )
    keyboard = generate_questions_keyboard(page, topic)
    if query:
        await query.edit_message_text(text, reply_markup=keyboard)
    else:
        await update.message.reply_text(text, reply_markup=keyboard)

# Обработка переключения страниц
async def handle_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, topic, page = query.data.split("_")
    await send_questions_page(update, context, topic, int(page))

# Возврат к выбору темы
async def back_to_topics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Выберите тему:", reply_markup=generate_topics_keyboard())

# Основная функция
def main():
    application = Application.builder().token("СЮДА НУЖНО ВСТАВИТЬ ТОКЕН").build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(choose_topic, pattern=r"^topic_"))
    application.add_handler(CallbackQueryHandler(handle_page, pattern=r"^page_"))
    application.add_handler(CallbackQueryHandler(back_to_topics, pattern=r"^back_to_topics$"))

    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
