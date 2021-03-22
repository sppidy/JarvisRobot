from jarvis.modules.disable import DisableAbleCommandHandler
from jarvis import dispatcher, SUDO_USERS
from jarvis.modules.helper_funcs.extraction import extract_user
from telegram.ext import run_async, CallbackQueryHandler
import jarvis.modules.sql.approve_sql as sql
from jarvis.modules.helper_funcs.chat_status import (bot_admin, user_admin, promote_permission)
from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram import Update, Bot, Message, Chat, User
from typing import Optional, List


@user_admin
@promote_permission
@run_async
def approve(bot: Bot, update: Update, args: List[str]) -> str:
	 message = update.effective_message
	 chat_title = message.chat.title
	 chat = update.effective_chat
	
	 user_id = extract_user(message, args)
	 if not user_id:
	     message.reply_text("I don't know who you're talking about, you're going to need to specify a user!")
	     return ""
	 member = chat.get_member(int(user_id))
	 if member.status == "administrator" or member.status == "creator":
	     message.reply_text(f"User is already admin - locks, blocklists, and antiflood already don't apply to them.")
	     return
	 if sql.is_approved(message.chat_id, user_id):
	     message.reply_text(f"[{member.user['first_name']}](tg://user?id={member.user['id']}) is already approved in {chat_title}", parse_mode=ParseMode.MARKDOWN)
	     return
	 sql.approve(message.chat_id, user_id)
	 message.reply_text(f"[{member.user['first_name']}](tg://user?id={member.user['id']}) has been approved in {chat_title}! They will now be ignored by automated admin actions like locks, blocklists, and antiflood.", parse_mode=ParseMode.MARKDOWN)
     
@user_admin
@promote_permission
@run_async
def disapprove(bot: Bot, update: Update, args: List[str]) -> str:
	 message = update.effective_message
	 chat_title = message.chat.title
	 chat = update.effective_chat
	 
	 user_id = extract_user(message, args)
	 if not user_id:
	     message.reply_text("I don't know who you're talking about, you're going to need to specify a user!")
	     return ""
	 member = chat.get_member(int(user_id))
	 if member.status == "administrator" or member.status == "creator":
	     message.reply_text("This user is an admin, they can't be unapproved.")
	     return
	 if not sql.is_approved(message.chat_id, user_id):
	     message.reply_text(f"{member.user['first_name']} isn't approved yet!")
	     return
	 sql.disapprove(message.chat_id, user_id)
	 message.reply_text(f"{member.user['first_name']} is no longer approved in {chat_title}.")
     
@user_admin
@run_async
def approved(bot: Bot, update: Update, args: List[str]) -> str:
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    no_users = False
    msg = "The following users are approved.\n"
    x = sql.list_approved(message.chat_id)
    for i in x:
        try:
            member = chat.get_member(int(i.user_id))
        except:
            pass
        msg += f"- `{i.user_id}`: {member.user['first_name']}\n"
    if msg.endswith("approved.\n"):
      message.reply_text(f"No users are approved in {chat_title}.")
      return
    else:
      message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

@user_admin
@run_async
def approval(bot: Bot, update: Update, args: List[str]) -> str:
	 message = update.effective_message
	 chat = update.effective_chat
	 
	 user_id = extract_user(message, args)
	 member = chat.get_member(int(user_id))
	 if not user_id:
	     message.reply_text("I don't know who you're talking about, you're going to need to specify a user!")
	     return ""
	 if sql.is_approved(message.chat_id, user_id):
	     message.reply_text(f"{member.user['first_name']} is an approved user. Locks, antiflood, and blocklists won't apply to them.")
	 else:
	     message.reply_text(f"{member.user['first_name']} is not an approved user. They are affected by normal commands.")


@run_async
def unapproveall(bot: Bot, update: Update):
    chat = update.effective_chat
    user = update.effective_user
    member = chat.get_member(user.id)


    if chat.type == "private":
        update.effective_message.reply_text("This command is not specified to be used in my PM.")
        return


    if member.status != "creator" and user.id not in SUDO_USERS:
        update.effective_message.reply_text(
            "Only the chat owner can unapprove all users at once."
        )
    else:
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Unapprove all users", callback_data="unapproveall_user"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Cancel", callback_data="unapproveall_cancel"
                    )
                ],
            ]
        )
        update.effective_message.reply_text(
            f"Are you sure you would like to unapprove ALL users in {chat.title}? This action cannot be undone.",
            reply_markup=buttons,
            parse_mode=ParseMode.MARKDOWN,
        )


@run_async
def unapproveall_btn(bot: Bot, update: Update):
    query = update.callback_query
    chat = update.effective_chat
    message = update.effective_message
    member = chat.get_member(query.from_user.id)
    if query.data == "unapproveall_user":
        if member.status == "creator" or query.from_user.id in SUDO_USERS:
            users = []
            approved_users = sql.list_approved(chat.id)
            for i in approved_users:
                users.append(int(i.user_id))
            for user_id in users:
                sql.disapprove(chat.id, user_id)
            message.edit_text("Unapproved all users in chat. All users will now be affected by locks, blocklists, and antiflood.")
            return ""
        if member.status == "administrator":
            query.answer("Only owner of the chat can do this.")

        if member.status == "member":
            query.answer("You need to be admin to do this.")
    elif query.data == "unapproveall_cancel":
        if member.status == "creator" or query.from_user.id in SUDO_USERS:
            message.edit_text("Removing of all approved users has been cancelled.")
            return ""
        if member.status == "administrator":
            query.answer("Only owner of the chat can do this.")
        if member.status == "member":
            query.answer("You need to be admin to do this.")
				
def __stats__():
    return "{} approved users, across {} chats.".format(sql.num_approved(),
                                                            sql.num_approved_chats())

__help__  = """
*Admin commands:*
- /approval: Check a user's approval status in this chat.
*Admin commands:*
- /approve: Approve of a user. Locks, blacklists, and antiflood won't apply to them anymore.
- /unapprove: Unapprove of a user. They will now be subject to locks, blacklists, and antiflood again.
- /approved: List all approved users.
*Owner command:*
- /unapproveall: To unapprove all users in a chat.

*Approval Examples*
 
Here are some examples for Approval module commands.
 
• To approve a user:
‣ `/approve @user`
 
• To unapprove a user:
‣ `/unapprove @user`
• To check all approved users in a chat:
‣ `/approved`
• To unapprove all users at once:
‣ `/unapproveall`

"""



APPROVE = DisableAbleCommandHandler("approve", approve, pass_args=True)
DISAPPROVE = DisableAbleCommandHandler("unapprove", disapprove, pass_args=True)
DISAPPROVE2 = DisableAbleCommandHandler("disapprove", disapprove, pass_args=True)
LIST_APPROVED = DisableAbleCommandHandler("approved", approved, pass_args=True)
APPROVAL = DisableAbleCommandHandler("approval", approval, pass_args=True)
UNAPPROVEALL = DisableAbleCommandHandler("unapproveall", unapproveall)
UNAPPROVEALL_BTN = CallbackQueryHandler(unapproveall_btn, pattern=r"unapproveall_.*")
				
dispatcher.add_handler(APPROVE)
dispatcher.add_handler(DISAPPROVE)
dispatcher.add_handler(DISAPPROVE2)
dispatcher.add_handler(LIST_APPROVED)
dispatcher.add_handler(APPROVAL)
dispatcher.add_handler(UNAPPROVEALL)
dispatcher.add_handler(UNAPPROVEALL_BTN)


__mod_name__ = "Approval"
__command_list__ = ["approve", "unapprove", "approved", "approval"]
__handlers__ = [APPROVE, DISAPPROVE,LIST_APPROVED, APPROVAL]
