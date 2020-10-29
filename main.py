import config
import csv
import random
import time
import asyncio

from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.executor import start_webhook


WEBHOOK_HOST = 'https://romanychev.online'
WEBHOOK_PATH = '/dictionary/'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

WEBAPP_HOST = '127.0.0.1'
WEBAPP_PORT = 7772

bot = Bot(token=config.token)
dp = Dispatcher(bot)

dictionary = {}
fieldnames = ['words', 'abbreviations', 'translate']
words = []
translate = []

path_out = "dict_out.csv"
path_in = "dict_in.csv"


def csv_reader(file_obj):
    reader = csv.reader(file_obj)

    for row in reader:
        if(row[0] != 'words'):
            dictionary[row[0]] = row[2]


def csv_dict_writer(data):
    with open(path_in, "w", newline='') as out_file:
        writer = csv.DictWriter(out_file, delimiter=',', fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def save():
    global dictionary
    dictionary = {k: v for k, v in sorted(dictionary.items(), key=lambda item: item[0])}

    global words
    global translate
    words = list(dictionary.keys())
    translate = list(dictionary.values())
    n = len(words)

    data = []
    for i in range(n):
        inner_dict = dict(zip(fieldnames, [words[i], '', translate[i]]))
        data.append(inner_dict)

    csv_dict_writer(data)


def parse_str(s):
    i = 0
    n = len(s)
    while(i < n and s[i] != ' ' and s[i] != '\n'):
        i += 1
    i += 1
    l = i
    while(i < n and s[i] != ' ' and s[i] != '\n'):
        i += 1
    if(i < n):
        t = [s[l:i], s[i+1:]]
    else:
        t = s[l:i]
    return t


@dp.message_handler(commands=["add"])
async def add_word(message):
    text = parse_str(message.text)
    dictionary[text[0]] = text[1]

    save()

    await bot.send_message(message.chat.id, "Word is added")

@dp.message_handler(commands=["get"])
async def get_word(message):
    save()
    print(len(words))
    index = random.randint(0, len(words) - 1)
    await bot.send_message(message.chat.id, words[index])
    await asyncio.sleep(3)
    await bot.send_message(message.chat.id, translate[index])

@dp.message_handler(commands=["delete"])
async def delete(message):
    text = parse_str(message.text)
    if(text in dictionary):
        del dictionary[text]
        save()
        await bot.send_message(message.chat.id, "Word is deleted")
    else:
        await bot.send_message(message.chat.id, "Word isn`t found")


@dp.message_handler(commands=["training"])
async def training(message):
    kol = 0
    n = len(dictionary)
    used = [0] * n

    save()
    while(kol < n):
        index = random.randint(0, n)
        while(used[index] == 1):
            index = random.randint(0, n)
        used[index] = 1
        kol += 1
        await bot.send_message(message.chat.id, words[index])
        await asyncio.sleep(3)
        await bot.send_message(message.chat.id, translate[index])
        await asyncio.sleep(3)


def main():
    with open(path_in, "r") as f_obj:
        csv_reader(f_obj)

    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )


if __name__ == '__main__':
    main()
