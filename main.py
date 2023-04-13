from multidict import MultiDict
from pyobigram.client import ObigramClient
from pyobigram.inline import inlineKeyboardMarkup,inlineKeyboardButton
from aiohttp import web
import threading
import asyncio

BOT_TOKEN = ''
API_ID = ''
API_HASH = ''
HOST_ = 'http://pyobigram.file2link.ydns.eu/'

bot:ObigramClient = None

routes = web.RouteTableDef()
@routes.get('/{chatid}/{msgid}')
async def get_file(request):
    global bot
    chatid = request.match_info['chatid']
    msgid = request.match_info['msgid']
    if bot:
        msg = bot.mtp_gen_message(int(chatid),int(msgid))
        stream = await bot.async_get_info_stream(msg)
        headers = MultiDict({'Content-Disposition':'attachment; filename="'+stream['fname']+'"','Content-Length':str(stream['fsize'])})
        return web.Response(body=stream['body'],headers=headers)
    return web.Response(text='404 NOT FOUND')

def onmessage(update,bot:ObigramClient):
    message = update.message
    if bot.contain_file(message):
        filename = message.file.file_id
        try:
            filename += message.file.mime_type.split('/')[-1]
        except:pass
        try:
            filename = message.file.file_name
        except:pass
        msg = bot.send_message(message.chat.id,'⏳Generando Enlace🔗...',reply_to_message_id=message.message_id)
        url = f'{HOST_}{message.chat.id}/{message.message_id}'
        reply_markup = inlineKeyboardMarkup(r1=[
            inlineKeyboardButton('🌀Url File🌀', url=url)
        ])
        resp_text = f'{filename} ✅'
        bot.edit_message(msg,resp_text,reply_markup=reply_markup)
    elif '/start' in message.text:
        reply_markup = inlineKeyboardMarkup(r1=[
            inlineKeyboardButton('🪤Academia Obisoft🪤',url='https://t.me/obisoft_academy')
        ])
        bot.send_message(message.chat.id,'Bienvenido @{} a nuestro File2Link, Unete al nuestra academia donde estaremos compartiendo contenido para el desarrollo de software. !Aprenda a Desarrollar!'.format(message.chat.username),reply_markup=reply_markup,reply_to_message_id=message.message_id)
    pass

if __name__ =='__main__':
    def run_web():
        global bot
        while not bot:pass
        while not bot.loop:pass
        app = web.Application()
        app.add_routes(routes)
        runner = web.AppRunner(app)
        bot.loop.run_until_complete(runner.setup())
        site = web.TCPSite(runner,host='0.0.0.0',port=80)
        bot.loop.run_until_complete(site.start())
        print('Server File Runing!')
        bot.loop.run_forever()
    threading.Thread(target=run_web).start()
    bot = ObigramClient(BOT_TOKEN,API_ID,API_HASH)
    bot.onMessage(onmessage)
    print('bot started!')
    bot.run()
