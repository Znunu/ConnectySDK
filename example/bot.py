from connecty import Bot
import config
bot = Bot()

@bot.configure
async def config():

    bot.no_echo()
    connection = await bot.register(config.channels)
    
    @connection.on_message
    async def on_msg(message):
        await connection.send(message)
        
bot.run(config.token)
