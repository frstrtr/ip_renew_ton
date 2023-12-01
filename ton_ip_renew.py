import requests
import time
import os
import json
import socket
import struct
from datetime import datetime
from aiogram import Bot, Dispatcher, types
import asyncio


async def send_message(chat_id, message):
    await bot.send_message(chat_id, message)


@dp.message_handler(commands=['start', 'my_chat_id'])
async def send_chat_id(message: types.Message):
    chat_id = message.chat.id
    await message.reply(f"Your chat ID is: {chat_id}")



def read_bot_config(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()
        token = lines[0].strip()
        chat_id = lines[1].strip()
        return token, chat_id


def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_external_ip():
    response = requests.get("https://httpbin.org/ip")
    ip_dotted = response.json()["origin"]
    # Convert dotted IP to decimal
    ip_decimal = struct.unpack("!L", socket.inet_aton(ip_dotted))[0]
    return ip_decimal


def read_last_ip():
    try:
        with open("last_ip.txt", "r") as file:
            return int(file.read().strip())
    except FileNotFoundError:
        return None


def write_last_ip(ip):
    with open("last_ip.txt", "w") as file:
        file.write(str(ip))


def update_config_and_restart_service(new_ip):
    config_path = "/var/ton-work/db/config.json"
    with open(config_path, "r+") as file:
        config = json.load(file)

        if config["addrs"][0]["ip"] != new_ip:
            config["addrs"][0]["ip"] = new_ip

            file.seek(0)
            json.dump(config, file, indent=4)
            file.truncate()

    os.system("systemctl restart validator.service")
    os.system("systemctl restart mytoncore.service")


async def main():
    # Existing code for IP checking...

    while True:
        current_ip = get_external_ip()
        dotted_ip = socket.inet_ntoa(struct.pack("!L", current_ip))
        log_message = f"[{get_timestamp()}] Current IP (Decimal): {current_ip}, (Dotted): {dotted_ip}"
        print(log_message)
        await send_message(YOUR_CHAT_ID, log_message)

        last_ip = read_last_ip()
        if current_ip != last_ip:
            update_message = f"[{get_timestamp()}] IP changed. Updating config and restarting services."
            print(update_message)
            await send_message(YOUR_CHAT_ID, update_message)
            update_config_and_restart_service(current_ip)
            write_last_ip(current_ip)
        else:
            check_message = f"[{get_timestamp()}] No change in IP."
            print(check_message)
            await send_message(YOUR_CHAT_ID, check_message)

        await asyncio.sleep(1800)  # Wait for 30 minutes


if __name__ == "__main__":

    from aiogram import executor

    API_TOKEN, YOUR_CHAT_ID = read_bot_config('bot_config.conf')
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(bot)

    executor.start_polling(dp, skip_updates=True)

    asyncio.run(main())
