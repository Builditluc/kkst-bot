from dataclasses import dataclass
from typing import List, cast
from datetime import datetime
from nextcord.channel import TextChannel
from nextcord.embeds import Embed
from nextcord.ext import commands
from nextcord.message import Message

from bot.checks import guild_allowed, has_role, in_channel
from bot.config import CONFIG
from bot.logging import get_logger
from bot.utils import cleanup, wait_for
from bot.cogs.utils import Utils

import emote

log = get_logger("kkst-bot")

# TODO: move this when we have a database set up
@dataclass
class Exam():
    name: str
    date: datetime
    message_id: int

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
    @in_channel(CONFIG.channel_staff)
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
        await msg.add_reaction(emote.CHECK["white_check_mark"].emoji)

        exam_date = datetime.strptime(msg.content, "%d-%m-%Y")
        exam = Exam(exam_name, exam_date, 0)

        msg: Message = await ctx.send(
            content="Here is a preview of the Exam. Is everything correct?",
            embed=create_embed_from_exam(exam),
        )
        messages.append(msg)

        utils_cog = cast(Utils, self.bot.get_cog("utils"))
        reaction = await utils_cog.get_reaction(msg, list(emote.CHECK.values()), ctx.author)

        if reaction == 1:
            msg = await ctx.send("Hmm, okay. I'll discard that")
            messages.append(msg)
            log.debug(f"discarding the exam '{exam_name}'")
            await ctx.message.add_reaction(emote.CHECK["x"].emoji)
            return await cleanup(messages)
            
        log.debug(f"creating the exam '{exam_name}'")

        exams_channel = self.bot.get_channel(CONFIG.channel_exams)
        if exams_channel is not None:
            msg = await exams_channel.send(embed=create_embed_from_exam(exam))
            exam.message_id = msg.id
        exams.append(exam)

        await ctx.message.add_reaction(emote.CHECK["white_check_mark"].emoji)
        return await cleanup(messages)
    
    @commands.command(name="exams.del")
    @in_channel(CONFIG.channel_staff)
    @has_role(CONFIG.moderator)
    async def remove_exam(self, ctx: commands.Context, exam_name: str):
        log.info(f"{ctx.author} executed exams.del")

        messages = []
        msg = await ctx.send(f"Are you sure that you want to delete the exam '{exam_name}'?")
        messages.append(msg)

        utils_cog = cast(Utils, self.bot.get_cog("utils"))
        reaction = await utils_cog.get_reaction(msg, list(emote.CHECK.values()), ctx.author)

        if reaction == 1:
            await ctx.message.add_reaction(emote.CHECK["x"].emoji)
            return await cleanup(messages)

        log.debug(f"removing the exam '{exam_name}'")
        for exam in exams:
            if exam.name == exam_name:
                exams_channel = self.bot.get_channel(CONFIG.channel_exams)
                if exams_channel is not None:
                    msg = await cast(TextChannel, exams_channel).fetch_message(exam.message_id)
                    messages.append(msg)
                break

        await ctx.message.add_reaction(emote.CHECK["white_check_mark"].emoji)
        return await cleanup(messages)

    @commands.command(name="exams.edit")
    @in_channel(CONFIG.channel_staff)
    @has_role(CONFIG.moderator)
    async def edit_exam(self, ctx: commands.Context, exam_name: str):
        log.info(f"{ctx.author} executed exams.edit")

        messages = []
        select_options = [
            emote.NUMBERS["one"],
            emote.NUMBERS["two"],
            emote.NUMBERS["three"],
        ]
        msg = await ctx.send(f"""
        Here is the exam '{exam_name}', what do you want to edit?

        {select_options[0]}: Name
        {select_options[1]}: Date
        {select_options[2]}: Topics (WIP)
        """)
        messages.append(msg)

        utils_cog = cast(Utils, self.bot.get_cog("utils"))
        await utils_cog.get_reaction(msg, select_options, ctx.author)

        msg: Message = await ctx.send("Sorry, that's still in development :/")
        messages.append(msg)

        await wait_for(seconds=4)

        await ctx.message.add_reaction(emote.CHECK["x"].emoji)
        return await cleanup(messages)

    @add_exam.error
    @remove_exam.error
    @edit_exam.error
    async def handle_error(self, ctx: commands.Context, error):
        await ctx.send(error)


def setup(bot: commands.Bot):
    bot.add_cog(Exams(bot))
