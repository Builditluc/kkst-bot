from nextcord.embeds import Embed
from nextcord.ext import commands
from nextcord.message import Message
from bot.checks import guild_allowed, in_channel, has_role
from bot.cogs.cog import Cog
from bot.cogs.utils import Utils
from bot.helpers import cleanup, error, ok, wait_for
from db.exam import Exam, ExamTopic
from db import EXAMS_DATABASE
from emote import EMOTES
from log import init_logger, LogLevel
from typing import cast, List, Tuple
from config import CONFIG

__all__ = ["Exams"]

log = init_logger(__name__, LogLevel.DEBUG)


class Exams(Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__("exams", bot)
        log.info("Created an instance of the Exams cog")

    @commands.command(name="exams.create")
    @guild_allowed()
    @in_channel(CONFIG.staff_channel)
    @has_role(CONFIG.moderator)
    async def createExam(self, ctx: commands.Context, name: str):
        log.info(f"{ctx.author} executed Exams.create")

        messages: List[Message] = []

        msg = await ctx.send(f"Okay, let's add {name}!")
        messages.append(msg)

        utils = cast(Utils, self.bot.get_cog("utils"))
        date, msgs = await utils.getDate(ctx, past_allowed=False)
        messages.extend(msgs)

        if date is None:
            await error(log, ctx.message)
            return await cleanup(log, messages)

        exam = Exam(name=name, topics=[], date=date, messageId=0)

        msg = await ctx.send(
            content="Here is a preview of the Exam. Is everything correct?",
            embed=exam.toEmbed(),
        )
        messages.append(msg)

        reaction, msgs = await utils.getReaction(
            ctx, msg, [EMOTES["white_check_mark"], EMOTES["x"]], ctx.author
        )
        messages.extend(msgs)

        if reaction is None:
            await error(log, ctx.message)
            return await cleanup(log, messages)

        if reaction > 0:
            msg = await ctx.send("Hmm, okay. I'll discard that")
            messages.append(msg)
            log.debug(f"Discarding the exam {name=}")
            log.info(f"Aborting the command Exam.create")

            await error(log, ctx.message)
            return await cleanup(log, messages)

        log.debug(f"Creating the exam {name=}")

        log.debug(f"Trying to send the exam message in the exams channel")
        exam_channel = self.bot.get_channel(CONFIG.exams_channel)
        if exam_channel is not None:
            msg = await exam_channel.send(embed=exam.toEmbed())
            exam.messageId = msg.id

        log.debug(f"Adding the exam '{name}' to the database")
        EXAMS_DATABASE.createExam(exam)

        log.info(f"Successfully finished Exams.create")
        await ok(log, ctx.message)
        return await cleanup(log, messages)

    @commands.command(name="exams.remove")
    @guild_allowed()
    @in_channel(CONFIG.staff_channel)
    async def removeExam(self, ctx: commands.Context, name: str):
        log.info(f"{ctx.author} executed Exams.remove")
        exam = EXAMS_DATABASE.getExam(name)
        if exam is None:
            log.info(f"Aborting Exams.remove because the exam could not be found")
            return await error(log, ctx.message)

        EXAMS_DATABASE.removeExam(name)

        exam_channel = self.bot.get_channel(CONFIG.exams_channel)
        if exam_channel is None:
            log.info(
                "Aborting Exams.remove because the exams channel could not be found"
            )
            await error(log, ctx.message)

        message = exam_channel.get_partial_message(exam.messageId)
        await message.delete()

        log.info(f"Successfully finished Exams.remove")
        await ok(log, ctx.message)

    @commands.command(name="exams.update")
    @guild_allowed()
    @in_channel(CONFIG.staff_channel)
    async def updateExam(self, ctx: commands.Context, name: str):
        log.info(f"{ctx.author} executed Exams.update")
        messages: List[Message] = []

        exam = EXAMS_DATABASE.getExam(name)
        if exam is None:
            msg = await ctx.send(f"I couldn't find the exam '{name}'")
            messages.append(msg)
            log.info(
                f"Aborting Exams.update because the exam '{name}' could not be found"
            )

            await wait_for(log, seconds=2)
            await error(log, ctx.message)
            return await cleanup(log, messages)

        msg = await ctx.send(
            f"""Here is the exam '{exam.name}', what do you want to update?
{EMOTES["one"]}: Name
{EMOTES["two"]}: Date
{EMOTES["three"]}: Topics
        """
        )
        messages.append(msg)

        utils = cast(Utils, self.bot.get_cog("utils"))
        reaction, msgs = await utils.getReaction(
            ctx, msg, [EMOTES["one"], EMOTES["two"], EMOTES["three"]], ctx.author
        )
        messages.extend(msgs)

        if reaction is None:
            log.info(f"Aborting Exams.update")
            await error(log, ctx.message)
            return await cleanup(log, messages)

        elif reaction == 0:
            log.info(f"Changing the name of the exam")
            is_error, msgs = await self._updateExamName(ctx, exam)
            messages.extend(msgs)
            if is_error is False:
                await ok(log, ctx.message)
                log.info(f"Successfully finished Exams.update")
                return await cleanup(log, messages)

        elif reaction == 1:
            log.info(f"Changing the date of the exam")
            is_error, msgs = await self._updateExamDate(ctx, exam)
            messages.extend(msgs)
            if is_error is False:
                await ok(log, ctx.message)
                log.info(f"Successfully finished Exams.update")
                return await cleanup(log, messages)

        elif reaction == 2:
            log.info(f"Changing the topics of the exam")
            is_error, msgs = await self._updateExamTopics(ctx, exam)
            messages.extend(msgs)
            if is_error is False:
                await ok(log, ctx.message)
                log.info(f"Successfully finished Exams.update")
                return await cleanup(log, messages)

        await error(log, ctx.message)
        log.info(f"Aborting Exams.update")
        return await cleanup(log, messages)

    @commands.command(name="exams.list")
    @guild_allowed()
    @in_channel(CONFIG.staff_channel)
    async def listExams(self, ctx: commands.Context):
        log.info(f"{ctx.author} executed Exams.list")
        messages: List[Message] = []

        exams = EXAMS_DATABASE.getAllExams()
        if len(exams) == 0:
            msg = await ctx.send("I couldn't find any exams in the database!")
            messages.append(msg)

            await wait_for(log, seconds=2)
            await error(log, ctx.message)
            return await cleanup(log, messages)

        list_embed = Embed(
            title="Saved Exams:",
            type="rich",
            description="\n".join(
                f"{x.date.strftime('%d-%m-%Y')}:\t{x.name}" for x in exams
            ),
        )
        msg = await ctx.send(embed=list_embed)
        messages.append(msg)

        log.info("Successfully finished Exams.list")
        await wait_for(log, seconds=30)
        await ok(log, ctx.message)
        return await cleanup(log, messages)

    async def _updateExam(self, exam: Exam) -> bool:
        log.debug(f"Updating the exam '{exam}'")

        exam_channel = self.bot.get_channel(CONFIG.exams_channel)
        if exam_channel is None:
            return True

        exam_message = exam_channel.get_partial_message(exam.messageId)
        exam_message = await exam_message.edit(embed=exam.toEmbed())
        if exam_message is None:
            return True

        return False

    async def _updateExamName(
        self, ctx: commands.Context, exam: Exam
    ) -> Tuple[bool, List[Message]]:
        messages: List[Message] = []

        utils = cast(Utils, self.bot.get_cog("utils"))
        name, msgs = await utils.getInput(ctx, "Please enter a new name:")
        messages.extend(msgs)

        if name is None:
            return (True, messages)

        # HACK: We need to add an update function to the Database Interface
        EXAMS_DATABASE.removeExam(exam.name)
        exam.name = name
        EXAMS_DATABASE.createExam(exam)

        await self._updateExam(exam)
        return (False, messages)

    async def _updateExamDate(
        self, ctx: commands.Context, exam: Exam
    ) -> Tuple[bool, List[Message]]:
        messages: List[Message] = []

        utils = cast(Utils, self.bot.get_cog("utils"))
        date, msgs = await utils.getDate(ctx, past_allowed=False)
        messages.extend(msgs)

        if date is None:
            return (True, messages)

        # HACK: We need to add an update function to the Database Interface
        EXAMS_DATABASE.removeExam(exam.name)
        exam.date = date
        EXAMS_DATABASE.createExam(exam)

        await self._updateExam(exam)
        return (False, messages)

    async def _updateExamTopics(
        self, ctx: commands.Context, exam: Exam
    ) -> Tuple[bool, List[Message]]:
        messages: List[Message] = []

        utils = cast(Utils, self.bot.get_cog("utils"))
        topics_string, msgs = await utils.getInput(
            ctx, "Please enter the topics in the correct format down below"
        )
        messages.extend(msgs)

        if topics_string is None:
            return (True, messages)

        exam.topics = ExamTopic.fromString(topics_string)
        exam_preview = await ctx.send(
            content="Here is a preview of the Exam. Is everything correct?",
            embed=exam.toEmbed(),
        )
        messages.append(exam_preview)

        reaction, msgs = await utils.getReaction(
            ctx, exam_preview, [EMOTES["white_check_mark"], EMOTES["x"]], ctx.author
        )
        messages.extend(msgs)

        if reaction is None or reaction == 1:
            return (True, messages)

        # HACK: We need to add an update function to the Database Interface
        EXAMS_DATABASE.removeExam(exam.name)
        EXAMS_DATABASE.createExam(exam)

        await self._updateExam(exam)
        return (False, messages)
