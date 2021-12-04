from dataclasses import dataclass
from typing import List
from datetime import datetime
from nextcord.embeds import Embed
from nextcord.ext import commands
from nextcord.message import Message
from nextcord.reaction import Reaction

from bot.checks import guild_allowed, has_role
from bot.config import CONFIG
from bot.logging import get_logger
from bot.utils import cleanup

log = get_logger("kkst-bot")

# TODO: move this when we have a database set up
@dataclass
class Exam():
    name: str
    date: datetime

exams: List[Exam] = []

def create_embed_from_exam(exam: Exam) -> Embed:
    return Embed(
        title=exam.name,
        type="rich",
        timestamp=exam.date
    )


class Exams(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot

    @commands.command(name="exams.add")
    @guild_allowed()
    @has_role(CONFIG.moderator)
    async def add_exam(self, ctx: commands.Context, exam_name: str):
        log.info(f"{ctx.author} executed exams.add")

        # Store messages for deletion afterwards
        messages: List[Message] = []

        msg = await ctx.send(f"Okay, let's add {exam_name}!\nPlease send me the date of the exam in this format: 'dd-mm-yyyy'")
        messages.append(msg)

        def check(message: Message) -> bool:
            if message.author != ctx.author:
                return False
            try:
                datetime.strptime(message.content, "%d-%m-%Y")
                return True
            except ValueError:
                return False

        msg: Message = await self.bot.wait_for("message", check=check)
        messages.append(msg)
        await msg.add_reaction("\u2705")

        exam_date = datetime.strptime(msg.content, "%d-%m-%Y")
        exam = Exam(exam_name, exam_date)

        msg: Message = await ctx.send(
            content="Here is a preview of the Exam. Is everything correct?",
            embed=create_embed_from_exam(exam),
        )
        messages.append(msg)
        await msg.add_reaction("\u2705")
        await msg.add_reaction("\u274c")

        def check_reaction(reaction: Reaction, user) -> bool:
            return user == ctx.author and str(reaction.emoji) in ["\u2705", "\u274c"]

        reaction, _ = await self.bot.wait_for("reaction_add", check=check_reaction)
        if str(reaction.emoji) == "\u274c":
            msg = await ctx.send("Hmm, okay. I'll discard that")
            messages.append(msg)
            log.debug(f"discarding the exam '{exam_name}'")
            await ctx.message.add_reaction("\u274c")
            return await cleanup(messages)
            
        log.debug(f"creating the exam '{exam_name}'")
        exams.append(exam)

        exams_channel = self.bot.get_channel(CONFIG.channel_exams)
        if exams_channel is not None:
            await exams_channel.send(embed=create_embed_from_exam(exam))

        await ctx.message.add_reaction("\u2705")
        return await cleanup(messages)

    @add_exam.error
    async def handle_error(self, ctx: commands.Context, error):
        await ctx.send(error)


def setup(bot: commands.Bot):
    bot.add_cog(Exams(bot))
