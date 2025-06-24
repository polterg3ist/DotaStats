import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram import F

# Инициализация бота с HTML-разметкой по умолчанию
bot = Bot(
    token="7824254637:AAGS3Nv6T4P0je9Ek24J_VUz2vLN9uEOG40",
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Функция для получения SteamID32


def get_steam_id32(input_str):
    if input_str.isdigit():
        return int(input_str)
    elif "steamcommunity.com" in input_str:
        parts = input_str.split('/')
        for part in parts:
            if part.startswith('7656') and len(part) == 17:
                steamid64 = int(part)
                return steamid64 - 76561197960265728
    return None


# Обработчик команды /start
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "<b>Привет!</b> Я бот для анализа статистики Dota 2.\n\n"
        "Отправь мне:\n"
        "• SteamID32 (например, <code>123456789</code>)\n"
        "• SteamID64 (например, <code>76561197960265728</code>)\n"
        "• Ссылку на профиль Steam"
    )


# Обработчик текстовых сообщений
@dp.message(F.text)
async def handle_input(message: types.Message):
    user_input = message.text.strip()
    steam_id32 = get_steam_id32(user_input)

    if steam_id32 is None:
        await message.answer("❌ Неверный формат SteamID. Попробуйте еще раз.")
        return

    try:
        player_data = requests.get(f"https://api.opendota.com/api/players/{steam_id32}").json()

        if 'profile' not in player_data:
            await message.answer("⚠️ Профиль не найден. Проверь SteamID.")
            return

        web_app_btn = InlineKeyboardButton(
            text="📊 Открыть статистику",
            web_app=WebAppInfo(url=f"https://dota-stats-pi.vercel.app/?steamid={steam_id32}")
        )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[web_app_btn]])

        await message.answer(
            f"🎮 <b>{player_data['profile']['personaname']}</b>\n"
            f"🏆 MMR: <code>{player_data.get('mmr_estimate', {}).get('estimate', 'N/A')}</code>\n\n"
            "Нажми кнопку ниже для детальной статистики:",
            reply_markup=keyboard
        )

    except Exception as e:
        await message.answer(f"🚨 Ошибка: {str(e)}")


# Запуск бота
async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())