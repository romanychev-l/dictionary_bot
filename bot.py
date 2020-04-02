import config
import telebot
import csv
import random
import time

bot = telebot.TeleBot(config.token)

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

@bot.message_handler(commands=["add"])
def add_word(message):
    text = parse_str(message.text)
    dictionary[text[0]] = text[1]
        
    save()

    bot.send_message(message.chat.id, "Word is added")

@bot.message_handler(commands=["get"])
def get_word(message):
    save()
    print(len(words))
    index = random.randint(0, len(words) - 1)
    bot.send_message(message.chat.id, words[index])
    time.sleep(3)
    bot.send_message(message.chat.id, translate[index])

@bot.message_handler(commands=["delete"])
def delete(message):
    text = parse_str(message.text)
    if(text in dictionary):
        del dictionary[text]
        save()
        bot.send_message(message.chat.id, "Word is deleted")
    else:
        bot.send_message(message.chat.id, "Word isn`t found")

@bot.message_handler(commands=["training"])
def training(message):
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
        bot.send_message(message.chat.id, words[index])
        time.sleep(3)
        bot.send_message(message.chat.id, translate[index])
        time.sleep(3)


if __name__ == '__main__':
    with open(path_in, "r") as f_obj:
        csv_reader(f_obj)
    bot.polling(none_stop=True)
