from discord import Client, Message
import os

TOKEN = os.environ.get("DISCORD_TOKEN", None)


class Bot(Client):
    async def on_ready(self):
        print(f"Logged on as {self.user}!")

    async def on_message(self, message: Message):
        if message.author == self:
            return

        await message.reply("ping!")


def main():
    client = Bot()
    client.run(TOKEN)


if __name__ == "__main__":
    main()
