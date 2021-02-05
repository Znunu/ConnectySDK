# ConnectySDK


## Basic Example
```python
from connecty import Bot
bot = Bot()

@bot.configure
async def config():

    bot.no_echo()
    connection = await bot.register([YOUR CHANNEL IDs HERE])
    
    @connection.on_message
    async def on_msg(message):
        await connection.send(message)
        
bot.run(YOUR TOKEN HERE)
```

## Advanced Example
```python
@bot.configure
async def config():

    bot.no_echo()
    connection = await bot.register([YOUR CHANNEL IDs HERE])

    @connection.on_message
    async def on_msg(message):
        await connection.send(message)

    @connection.links[0].on_message
    async def on_msg(message):
        await connection.links[2].send("Message sent from 0")

    @connection.links[1].on_message
    async def on_msg(message):
        await connection.links[2].send("Message sent from 1")
```
