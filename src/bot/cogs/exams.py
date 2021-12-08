from dataclasses import dataclass
from typing import List, Tuple, Union, cast
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


# TODO: create __all__

log = get_logger("kkst-bot")

# TODO: replace this with database interface later
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

        msg = await ctx.send(f"Okay, let's add {exam_name}!")
        messages.append(msg)

        utils_cog = cast(Utils, self.bot.get_cog("utils"))
        exam_date, msgs = await utils_cog.get_date(ctx, past_allowed=False)
        messages.extend(msgs)

        if exam_date is None: 
            await ctx.message.add_reaction(emote.CHECK["x"].emoji)
            return await cleanup(messages)

        exam = Exam(exam_name, exam_date, 0)

        msg: Message = await ctx.send(
            content="Here is a preview of the Exam. Is everything correct?",
            embed=create_embed_from_exam(exam),
        )
        messages.append(msg)

        utils_cog = cast(Utils, self.bot.get_cog("utils"))
        reaction, msgs = await utils_cog.get_reaction(ctx, msg, list(emote.CHECK.values()), ctx.author)
        messages.extend(msgs)

        if reaction is None:
            await ctx.message.add_reaction(emote.CHECK["x"].emoji)
            return await cleanup(messages)

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
        reaction, msgs = await utils_cog.get_reaction(ctx, msg, list(emote.CHECK.values()), ctx.author)
        messages.extend(msgs)

        if reaction is None:
            await ctx.message.add_reaction(emote.CHECK["x"].emoji)
            return await cleanup(messages)

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

        exam: Union[Exam, None] = None

        for _exam in exams:
            if _exam.name == exam_name:
                exam = _exam
                break

        if exam is None:
            msg = await ctx.send(f"I couldn't find the exam '{exam_name}'")
            messages.append(msg)
            log.error(f"Exam '{exam_name}' was not found")

            await wait_for(seconds=2)
            await ctx.message.add_reaction(emote.CHECK["x"].emoji)
            return await cleanup(messages)

        select_options = [
            emote.NUMBERS["one"],
            emote.NUMBERS["two"],
            emote.NUMBERS["three"],
        ]
        msg = await ctx.send(f"""
        Here is the exam '{exam.name}', what do you want to edit?

        {select_options[0]}: Name
        {select_options[1]}: Date
        {select_options[2]}: Topics (WIP)
        """)
        messages.append(msg)

        utils_cog = cast(Utils, self.bot.get_cog("utils"))
        reaction, msgs = await utils_cog.get_reaction(ctx, msg, select_options, ctx.author)
        messages.extend(msgs)

        if reaction is None:
            await ctx.message.add_reaction(emote.CHECK["x"].emoji)
            return await cleanup(messages)

        elif reaction == 0:
            is_error, msgs = await self._edit_exam_name(ctx, exam)
            messages.extend(msgs)
            if is_error is True:
                await ctx.message.add_reaction(emote.CHECK["white_check_mark"].emoji)
                return await cleanup(messages)

        elif reaction == 1:
            is_error, msgs = await self._edit_exam_date(ctx, exam)
            messages.extend(msgs)
            if is_error is True:
                await ctx.message.add_reaction(emote.CHECK["white_check_mark"].emoji)
                return await cleanup(messages)

        elif reaction == 2:
            msg: Message = await ctx.send("Sorry, that's still in development :/")
            messages.append(msg)

            await wait_for(seconds=4)

        await ctx.message.add_reaction(emote.CHECK["x"].emoji)
        return await cleanup(messages)

    async def _edit_exam_name(self, ctx: commands.Context, exam: Exam) -> Tuple[bool, List[Message]]:
        messages: List[Message] = []

        # TODO: use helper function to get the new name
        msg = await ctx.send("Please enter a new name")
        messages.append(msg)
        def check(message: Message) -> bool:
            return message.author == ctx.author

        name_message = await self.bot.wait_for("message", check=check)
        messages.append(name_message)

        # TODO: find a better way to do this / move this into a function
        for i, _exam in enumerate(exams):
            if _exam.message_id == exam.message_id:
                exams[i].name = name_message.content

                is_error = await self._update_exam(_exam)
                if is_error:
                    break

                return (True, messages)

        return (False, messages)

    async def _edit_exam_date(self, ctx: commands.Context, exam: Exam) -> Tuple[bool, List[Message]]:
        # TODO: implement Exams._edit_exam_name
        messages: List[Message] = []

        utils_cog = cast(Utils, self.bot.get_cog("utils"))
        date, msgs = await utils_cog.get_date(ctx, past_allowed=False)
        messages.extend(msgs)

        if date is None:
            return (False, messages)

        for i, _exam in enumerate(exams):
            if _exam.message_id == exam.message_id:
                exams[i].date = date

                is_error = await self._update_exam(_exam)
                if is_error:
                    break

                return (True, messages)

        return (False, messages)

    async def _update_exam(self, exam: Exam) -> bool:
        log.debug(f"updating the exam '{exam}'")

        exams_channel = self.bot.get_channel(CONFIG.channel_exams)
        if exams_channel is None:
            return True

        exam_message = exams_channel.get_partial_message(exam.message_id)
        exam_message = await exam_message.edit(embed=create_embed_from_exam(exam))
        if exam_message is None:
            return True

        return False

    @add_exam.error
    @remove_exam.error
    @edit_exam.error
    async def handle_error(self, ctx: commands.Context, error):
        await ctx.send(error)


def setup(bot: commands.Bot):
    bot.add_cog(Exams(bot))
