from telebot import *
from web_scraper import *

API_TOKEN = '' #insert your TOKEN

bot = telebot.TeleBot(API_TOKEN)

# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, """\
🤖 Hi there, I am a Vinted Bot 🤖

I am here to advertise you about profitable ads. 🤑

Insert the product to track:  \
""")

@bot.message_handler(commands=['stop'])
def stop_bot(message):
    Run = False
    try:
        products = main(message.text, Run)
    except:
        print('')
    scraper_reset()
    bot.reply_to(message, """\
🤖 Great, the bot is stopped 🤖

Insert the new product:\
""")

# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def start_bot(message):
    bot.reply_to(message, """\
🤖 Great, the bot is started 🤖

⏸ Wait some minutes... ⏸

🛑🛑🛑 
Write /stop for interrupt the bot and search a new product 
🛑🛑🛑	\
    """)
    print(f'Recived message:{message.text}')
    Run = True
    #init function
    try:
        init(message.text)
    except:
        bot.reply_to(message, 'INIT FAILURE')

    #start main task
    #SCRAP GOOD PRODUCTS
    try:
        while Run:

            products = main(message.text, Run)

            try:
                print('Bot reply')
                for i in range(len(products)):
                    product = products[i]
                    print(product[3])
                    bot.reply_to(message, '💣💣💣💣 NEW ADS 💣💣💣💣 \n' f'Name:{product[0]} \n' f'Price:{product[1]} 🤑🤑🤑 \n' f'Market Price:{product[3]} \n' f'Link:{product[2]}')
                    #bot.send_photo(message,product[2])
            except:
                print('Error')

    except:
        print('Error')

    #GENERATE RETURN MESSAGE

bot.polling()