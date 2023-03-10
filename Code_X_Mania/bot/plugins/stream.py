# (c) Jigarvarma2005 || Code-X-Mania
#edit at your own risk
import os
import asyncio
from asyncio import TimeoutError
from Code_X_Mania.bot import StreamBot
from Code_X_Mania.utils.database import Database
from Code_X_Mania.utils.human_readable import humanbytes
from Code_X_Mania.vars import Var
from pyrogram import filters, Client
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
db = Database(Var.DATABASE_URL, Var.SESSION_NAME)


MY_PASS = os.environ.get("MY_PASS",None)
pass_dict = {}
pass_db = Database(Var.DATABASE_URL, "jv_passwords")


@StreamBot.on_message((filters.regex("LOGIN") | filters.command("login")) & ~filters.edited, group=4)
async def login_handler(c: Client, m: Message):
    try:
        try:
            jv = await m.reply_text("Now send me password.\n\n If You don't know ask password in @Dcstreambot \n\n(You can use /cancel command to cancel the process)")
            _text = await c.listen(m.chat.id, filters=filters.text, timeout=90)
            if _text.text:
                textp = _text.text
                if textp=="/cancel":
                   await jv.edit("Process Cancelled Successfully")
                   return
            else:
                return
        except TimeoutError:
            await jv.edit("I can't wait more for password, try again")
            return
        if textp == MY_PASS:
            await pass_db.add_user_pass(m.chat.id, textp)
            jv_text = "yeah! you entered the password correctly"
        else:
            jv_text = "Wrong password, try again"
        await jv.edit(jv_text)
    except Exception as e:
        print(e)

@StreamBot.on_message((filters.private) & (filters.document | filters.video | filters.audio | filters.photo) & ~filters.edited, group=4)
async def private_receive_handler(c: Client, m: Message):
    check_pass = await pass_db.get_user_pass(m.chat.id)
    if check_pass== None:
        await m.reply_text("Login first using /login cmd \n don\'t know the pass? request it from @Dcstreambot")
        return
    if check_pass != MY_PASS:
        await pass_db.delete_user(m.chat.id)
        return
    if not await db.is_user_exist(m.from_user.id):
        await db.add_user(m.from_user.id)
        await c.send_message(
            Var.BIN_CHANNEL,
            f"N?????? Us????? J????????????? : \n\n N????????? : [{m.from_user.first_name}](tg://user?id={m.from_user.id}) S????????????????? Y???????? B?????? !!"
        )
    if Var.UPDATES_CHANNEL != "None":
        try:
            user = await c.get_chat_member(Var.UPDATES_CHANNEL, m.chat.id)
            if user.status == "kicked":
                await c.send_message(
                    chat_id=m.chat.id,
                    text="__S????????? S????, Y?????? ???????? B????????????? ?????? ???s??? ??????.__\n\n  **C????????????????? D?????????????????????? @dcbotsa ????? W?????? H???????? Y??????**",
                    parse_mode="markdown",
                    disable_web_page_preview=True
                )
                return 
        except UserNotParticipant:
            await c.send_message(
                chat_id=m.chat.id,
                text="""<i>???????????????? UPDATES CHANNEL ???????? ???????????? ???????? ????</i>""",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("J??????? ???????? ????", url=f"https://t.me/{Var.UPDATES_CHANNEL}")
                        ]
                    ]
                ),
                parse_mode="HTML"
            )
            return
        except Exception as e:
            await m.reply_text(e)
            await c.send_message(
                chat_id=m.chat.id,
                text="**S???????????????????? ??????????? W?????????. C????????????????? ????? ?????ss** @Dcstreambot",
                parse_mode="markdown",
                disable_web_page_preview=True)
            return
    try:
        
        file_size = None
        if m.video:
            file_size = f"{humanbytes(m.video.file_size)}"
        elif m.document:
            file_size = f"{humanbytes(m.document.file_size)}"
        elif m.audio:
            file_size = f"{humanbytes(m.audio.file_size)}"
        elif m.photo:
            file_size=f"{humanbytes(m.photo.file_size)}"

        file_name = None
        if m.video:
            file_name = f"{m.video.file_name}"
        elif m.document:
            file_name = f"{m.document.file_name}"
        elif m.audio:
            file_name = f"{m.audio.file_name}"
        """
        elif m.photo:
            file_name=f"{m.photo.file_name}"
        """
            
        log_msg = await m.forward(chat_id=Var.BIN_CHANNEL)
        stream_link = Var.URL + 'watch/' + str(log_msg.message_id) 
        
        online_link = Var.URL + 'download/'+ str(log_msg.message_id) 
       
        
        

        msg_text ="""
<i><u>Your Link is Generated!</u></i>

<b>???? F??????? ??????????? :</b> <i>{}</i>

<b>???? F??????? ??????????? :</b> <i>{}</i>

<b>???? D??????????????????? :</b> <i>{}</i>

<b> ????WATCH  :</b> <i>{}</i>

<b>???? N????????? : LINK WON'T EXPIRE TILL I DELETE</b>"""

        await log_msg.reply_text(text=f"**R???Q?????????????????? ???? :** [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n**U???????? ????? :** `{m.from_user.id}`\n**Stream ????????? :** {stream_link}", disable_web_page_preview=True, parse_mode="Markdown", quote=True)
        await m.reply_text(
            text=msg_text.format(file_name, file_size, online_link, stream_link),
            parse_mode="HTML", 
            quote=True,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("???? STREAM", url=stream_link), #Stream Link
                                                InlineKeyboardButton('D??????????????????? ????', url=online_link)]]) #Download Link
        )
    except FloodWait as e:
        print(f"Sleeping for {str(e.x)}s")
        await asyncio.sleep(e.x)
        await c.send_message(chat_id=Var.BIN_CHANNEL, text=f"G?????? F???????????W???????? ????? {str(e.x)}s from [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n\n**???????????????? ???????? :** `{str(m.from_user.id)}`", disable_web_page_preview=True, parse_mode="Markdown")


@StreamBot.on_message(filters.channel & ~filters.group & (filters.document | filters.video | filters.photo) & ~filters.edited & ~filters.forwarded, group=-1)
async def channel_receive_handler(bot, broadcast):
    check_pass = await pass_db.get_user_pass(broadcast.chat.id)
    if check_pass == None:
        await broadcast.reply_text("Login first using /login cmd \n don\'t know the pass? request it from @adarshgoelz")
        return
    if check_pass != MY_PASS:
        await broadcast.reply_text("Wrong password, login again")
        await pass_db.delete_user(broadcast.chat.id)
        return
    if int(broadcast.chat.id) in Var.BANNED_CHANNELS:
        await bot.leave_chat(broadcast.chat.id)
        return
    try:
        log_msg = await broadcast.forward(chat_id=Var.BIN_CHANNEL)
        stream_link = Var.URL + 'watch/' + str(log_msg.message_id) 
        online_link = Var.URL + 'download/' + str(log_msg.message_id) 
        await log_msg.reply_text(
            text=f"**C?????????????? N?????????:** `{broadcast.chat.title}`\n**C?????????????? ID:** `{broadcast.chat.id}`\n**R???????????s??? ???????:** {stream_link}",
            quote=True,
            parse_mode="Markdown"
        )
        await bot.edit_message_reply_markup(
            chat_id=broadcast.chat.id,
            message_id=broadcast.message_id,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("???? STREAM ", url=stream_link),
                     InlineKeyboardButton('D??????????????????? ????', url=online_link)] 
                ]
            )
        )
    except FloodWait as w:
        print(f"Sleeping for {str(w.x)}s")
        await asyncio.sleep(w.x)
        await bot.send_message(chat_id=Var.BIN_CHANNEL,
                             text=f"G?????? F???????????W???????? ????? {str(w.x)}s from {broadcast.chat.title}\n\n**C?????????????? ID:** `{str(broadcast.chat.id)}`",
                             disable_web_page_preview=True, parse_mode="Markdown")
    except Exception as e:
        await bot.send_message(chat_id=Var.BIN_CHANNEL, text=f"**#????????????_?????????????????????????:** `{e}`", disable_web_page_preview=True, parse_mode="Markdown")
        print(f"C?????'??? E???????? B?????????????????s??? M???ss????????!\nE?????????:  **Give me edit permission in updates and bin Chanell{e}**")
