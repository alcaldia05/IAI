from multidict import MultiDict
from pyobigram.client import ObigramClient
from pyobigram.inline import inlineKeyboardMarkup,inlineKeyboardButton
from aiohttp import web
import threading
import asyncio
from pyngrok import ngrok
import re

PORT_ = 80

ngrok.set_auth_token("2ONUSJwFo4IOS8DGF6VjIeY6glF_5VKdcDLo36QZUQBXtfbNd")
print('Tunnel Connecting...')
tunnel = ngrok.connect(PORT_)
print('Tunnel Conected!')

BOT_TOKEN = '6205764515:AAFozZNDsK8MXe9GnDImRy3-Ntvbo__0gu0'
API_ID = '18641760'
API_HASH = 'b7b026ce9d1d36400c02dc21d8df53a3'
HOST_ = 'https://fiercely-lovely-lily-ship-dev.wayscript.cloud/'
HOST_ = tunnel.public_url + '/'


bot:ObigramClient = None

routes = web.RouteTableDef()
@routes.get('/{chatid}/{msgid}')
async def get_file(request):
    global bot
    offset = request.headers.get('Range', 0)
    if not isinstance(offset, int):
        offset = int(re.match(r'bytes=(\d+)', offset).group(1))
    chatid = request.match_info['chatid']
    msgid = request.match_info['msgid']
    if bot:
        msg = bot.mtp_gen_message(int(chatid),int(msgid))
        
        stream = await bot.async_get_info_stream(msg)
        size = stream['fsize']
        headers = MultiDict({
            'Accept-Ranges': 'bytes',
            'Content-Range': f'bytes {offset}-{size}/{size}',
            'Content-Disposition':'attachment; filename="'+stream['fname']+'"',
            'Content-Length':str(size)})
        return web.Response(status=206 if offset else 200,body=stream['body'],headers=headers)
    return web.Response(text='404 NOT FOUND')

ADMINS = ['Genoskuncyborg','obisoftt']

def onmessage(update,bot:ObigramClient):
    global ADMINS
    if update.message.chat.username not in ADMINS:return

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
        bot.send_message(message.chat.id,'''Pasos para usar:
1-Reenvia un archivo y espera unos segundos
2-Toca el boton URL File
3-Pincha Abrir y usa Navegador IDM+
4-Toca el boton Visit Site
5-Tocar boton Empezar a descargar''',reply_to_message_id=message.message_id)
    elif '/perm' in message.text:
        user = message.text.split(' ')[1]
        ADMINS.append(user)
    elif '/ban' in message.text:
        user = message.text.split(' ')[1]
        ADMINS.pop(user)
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
        site = web.TCPSite(runner,host='0.0.0.0',port=PORT_)
        bot.loop.run_until_complete(site.start())
        print(f'Server : {HOST_}')
        bot.loop.run_forever()
    threading.Thread(target=run_web).start()
    bot = ObigramClient(BOT_TOKEN,API_ID,API_HASH)
    bot.onMessage(onmessage)
    print('bot started!')
    bot.run()
