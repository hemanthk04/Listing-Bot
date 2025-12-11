"""
Telegram List Manager Bot
-------------------------
Features:
- Create lists
- Add items to lists
- Show all lists
- Show specific list
- Delete item (with index selection)
- Edit item (with index selection)
- JSON file storage (simple + persistent)

Author: YOU
"""

import json
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from config import BOT_TOKEN


DATA_FILE = "lists.json"

# -----------------------
# Load or initialize JSON
# -----------------------
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        lists = json.load(f)
else:
    lists = {}


# --------------------------------------------------
# Temporary state memory for delete/edit flows
# Example:
# pending_actions[user_id] = {
#     "type": "delete",
#     "list": "Substack Ideas"
# }
# --------------------------------------------------
pending_actions = {}


def save_data():
    """Save all lists to JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(lists, f, indent=4)


# ==================================================
# MAIN MESSAGE HANDLER
# ==================================================
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()

    # ---------------------------------------------
    # 0️⃣ If user is in a pending action (delete/edit)
    # ---------------------------------------------
    if user_id in pending_actions:
        action = pending_actions[user_id]

        # -------------------------
        # DELETE MODE (step 2)
        # User replies: "delete 2"
        # -------------------------
        if action["type"] == "delete":
            if text.lower().startswith("delete"):
                parts = text.split()
                if len(parts) != 2 or not parts[1].isdigit():
                    await update.message.reply_text("❌ Use: delete 2")
                    return

                index = int(parts[1]) - 1
                list_name = action["list"]
                items = lists[list_name]

                if index < 0 or index >= len(items):
                    await update.message.reply_text("❌ Invalid number.")
                    return

                removed_item = items.pop(index)
                save_data()
                del pending_actions[user_id]

                await update.message.reply_text(
                    f"🗑️ Deleted from *{list_name}*:\n{removed_item}",
                    parse_mode="Markdown"
                )
                return

        # -------------------------
        # EDIT MODE (step 2)
        # User replies: "edit 2 -> new text"
        # -------------------------
        if action["type"] == "edit":
            if text.lower().startswith("edit"):
                try:
                    command, rest = text.split(" ", 1)
                    index_str, new_text = rest.split("->")
                    index = int(index_str.strip()) - 1
                    new_text = new_text.strip()
                except:
                    await update.message.reply_text("❌ Use: edit 2 -> new text")
                    return

                list_name = action["list"]
                items = lists[list_name]

                if index < 0 or index >= len(items):
                    await update.message.reply_text("❌ Invalid number.")
                    return

                old_value = items[index]
                items[index] = new_text
                save_data()
                del pending_actions[user_id]

                await update.message.reply_text(
                    f"✏️ Edited in *{list_name}*:\n{old_value} → {new_text}",
                    parse_mode="Markdown"
                )
                return

    # ---------------------------------------------
    # 1️⃣ Show all lists
    # ---------------------------------------------
    if text.lower() == "lists":
        if not lists:
            await update.message.reply_text("No lists created yet.")
            return

        formatted = "\n".join([f"• {name}" for name in lists.keys()])
        await update.message.reply_text(
            f"📂 *Your Lists:*\n{formatted}",
            parse_mode="Markdown"
        )
        return

    # ---------------------------------------------
    # 2️⃣ Create List
    # ---------------------------------------------
    if text.lower().startswith("create list -"):
        list_name = text.split("-", 1)[1].strip()
        lists[list_name] = []
        save_data()

        await update.message.reply_text(
            f"✅ List created: *{list_name}*",
            parse_mode="Markdown"
        )
        return

    # ---------------------------------------------
    # 3️⃣ Delete Mode (step 1)
    # User: "Delete from Substack Ideas"
    # ---------------------------------------------
    if text.lower().startswith("delete from"):
        list_name = text.split("from", 1)[1].strip()

        if list_name not in lists:
            await update.message.reply_text("❌ List not found.")
            return

        if not lists[list_name]:
            await update.message.reply_text("❌ List is empty.")
            return

        pending_actions[user_id] = {
            "type": "delete",
            "list": list_name
        }

        items = lists[list_name]
        formatted = "\n".join([f"{i+1}. {item}" for i, item in enumerate(items)])

        await update.message.reply_text(
            f"📃 *Items in {list_name}:*\n{formatted}\n\nReply with: delete 2",
            parse_mode="Markdown"
        )
        return

    # ---------------------------------------------
    # 4️⃣ Edit Mode (step 1)
    # User: "Edit from Substack Ideas"
    # ---------------------------------------------
    if text.lower().startswith("edit from"):
        list_name = text.split("from", 1)[1].strip()

        if list_name not in lists:
            await update.message.reply_text("❌ List not found.")
            return

        if not lists[list_name]:
            await update.message.reply_text("❌ List is empty.")
            return

        pending_actions[user_id] = {
            "type": "edit",
            "list": list_name
        }

        items = lists[list_name]
        formatted = "\n".join([f"{i+1}. {item}" for i, item in enumerate(items)])

        await update.message.reply_text(
            f"✏️ *Items in {list_name}:*\n{formatted}\n\nReply with:\nedit 2 -> new text",
            parse_mode="Markdown"
        )
        return

# to add a new item in specific list
    if "-" in text:
        list_name, item = [x.strip() for x in text.split("-", 1)]

        if list_name in lists:
            lists[list_name].append(item)
            save_data()

            await update.message.reply_text(
                f"➕ Added to *{list_name}*: {item}",
                parse_mode="Markdown"
            )
            return

#show a specific list
    if text in lists:
        items = lists[text]

        if not items:
            await update.message.reply_text(f"📃 *{text}* is empty.", parse_mode="Markdown")
            return

        formatted = "\n".join([f"• {i}" for i in items])
        await update.message.reply_text(
            f"📃 *{text}*\n{formatted}",
            parse_mode="Markdown"
        )
        return

# for help command
    await update.message.reply_text(
        "Commands:\n"
        "• Create list - Name\n"
        "• Name - Item\n"
        "• lists (show all lists)\n\n"
        "Deleting:\n"
        "• Delete from Name\n"
        "• delete 2\n\n"
        "Editing:\n"
        "• Edit from Name\n"
        "• edit 2 -> new text\n\n"
        "• Name (show contents)"
    )


# ==================================================
# START BOT
# ==================================================
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print("🤖 Bot is running...\nPress CTRL + C to stop.")
    app.run_polling()
