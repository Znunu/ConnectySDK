import discord
import typing
import json

class MessageLike:
    """
    Children of this class may be passed to Link.send for complete control over the message sent by the webhook
    """
    name: str
    avatar_url: str
    content: str
    tts: bool


class Link:
    hook: discord.Webhook
    channel: discord.TextChannel
    bot: discord.Client
    his: set
    handler: typing.Callable

    @classmethod
    async def new(cls, channel: discord.TextChannel, bot: discord.Client):
        self = cls()
        self.his = set()
        self.handler = None
        self.bot = bot
        self.channel = channel
        hooks = await channel.webhooks()
        name = bot.user.name
        for hook in hooks:
            if hook.name == name:
                self.hook = hook
                break
        else:
            self.hook = await channel.create_webhook(name=name)
        return self

    async def send(self, message: typing.Union[discord.Message, MessageLike, str]):
        """
        Send a message to the channel.
        If a string is passed, the bot will not use the webhook to send the message.
        If a discord message is passed, the bot will try to imitate the message and author using a webhook.
        A MessageLike can be passed for finer control.
        """

        if isinstance(message, str):
            await self.channel.send(message)
        elif isinstance(message, MessageLike):
            await self.hook.send(content=message.content, avatar_url=str(message.avatar_url), username=message.name, tts=message.tts)
        elif isinstance(message, discord.Message):
            if not self.bot.echo:
                if message.channel == self.channel:
                    return
            if not self.bot.repeat:
                if message.id in self.his:
                    return
                else:
                    self.his.add(message.id)
            await self.hook.send(content=message.content, avatar_url=str(message.author.avatar_url), username=message.author.name, tts=message.tts)

    async def check(self, message: discord.Message):
        if message.channel.id == self.channel.id:
            if self.handler:
                await self.handler(message)

    def on_message(self, func: typing.Callable):
        """
        Decorator that is called whenever this channel receives a new message.
        """
        self.handler = func


class Chain:
    links: list[Link]
    bot: discord.Client
    handler: typing.Callable

    @classmethod
    async def new(cls, channels: list[discord.TextChannel], bot: discord.Client):
        self = cls()
        self.bot = bot
        self.handler = None
        self.links = list()
        for channel in channels:
            self.links.append(await Link.new(channel, bot))
        return self

    async def check(self, message: discord.Message):
        if message.channel.id in (link.channel.id for link in self.links):
            if self.handler:
                await self.handler(message)
            for link in self.links:
                await link.check(message)

    async def send(self, message: MessageLike):
        """
        Send a message to each and every channel contained within the chain.
        If a string is passed, the bot will not use the webhook to send the message.
        If a discord message is passed, the bot will try to imitate the message and author using a webhook.
        A MessageLike can be passed for finer control.
        """
        for link in self.links:
            await link.send(message)

    def on_message(self, func: typing.Callable):
        """
        Decorator that is called whenever any channel contained within this chain receives a message.
        """
        self.handler = func


class Bot(discord.Client):

    def __init__(self):
        super().__init__()
        self.chains = []
        self.init = None
        self.echo = True
        self.repeat = True

    async def on_ready(self):
        await self.init()
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message: discord.Message):
        if message.author == self.user or (int(message.author.discriminator) == 0):
            return

        for chain in self.chains:
            await chain.check(message)

    async def register(self, channels: list[int]):
        """
        Pass a list of channel IDs.
        A newly created chain (connection) will be returned.
        """
        channels = [self.get_channel(id) for id in channels]
        chain = await Chain.new(channels, self)
        self.chains.append(chain)
        return chain



    def configure(self, func: typing.Callable):
        """
        All custom code should be placed within an async function wrapped by this decorator
        """
        self.init = func

    def no_echo(self, no_echo=True):
        """
        Guarantees that the bot will never echo a message in the same channel.
        This takes precedence over any function call that instructs the bot to send a message.
        """
        self.echo = not no_echo

    def no_repeat(self, no_repeat=True):
        """
        Guarantees that the bot will never send the same message twice in the same channel.
        This takes precedence over any function call that instructs the bot to send a message.
        """

        self.repeat = not no_repeat
