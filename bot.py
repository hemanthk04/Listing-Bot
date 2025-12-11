import json
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from config import BOT_TOKEN

DATA_FILE = "lists.json"

# load storage
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        lists = json.load(f)
else:
    lists = {}

pending_actions = {}  # temporary delete/edit mode

def save():
    with open(DATA_FILE, "w") as f:
        json.dump(lists, f, indent=4)

# convert name to a key
def normalize(name):
    return name.strip().lower()

# find actual list name (case-preserved)
def find_list(name):
    key = normalize(name)
    for real in lists.keys():
        if normalize(real) == key:
            return real
    return None


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()

    # handle pending delete/edit
    if user_id in pending_actions:
        action = pending_actions[user_id]

        # delete item
        if action["type"] == "delete":
            if text.lower().startswith("delete"):
                parts = text.split()
                if len(parts) != 2 or not parts[1].isdigit():
                    await update.message.reply_text("Use: delete 2")
                    return

                index = int(parts[1]) - 1
                list_name = action["list"]
                items = lists[list_name]

                if index < 0 or index >= len(items):
                    await update.message.reply_text("Invalid number")
                    return

                removed = items.pop(index)
                save()
                del pending_actions[user_id]

                await update.message.reply_text(
                    f"Deleted from *{list_name}*:\n{removed}",
                    parse_mode="Markdown"
                )
                return

        # edit item
        if action["type"] == "edit":
            if text.lower().startswith("edit"):
                try:
                    _, rest = text.split(" ", 1)
                    index_str, new_text = rest.split("->")
                    index = int(index_str.strip()) - 1
                    new_text = new_text.strip()
                except:
                    await update.message.reply_text("Use: edit 2 -> new text")
                    return

                list_name = action["list"]
                items = lists[list_name]

                if index < 0 or index >= len(items):
                    await update.message.reply_text("Invalid number")
                    return

                old = items[index]
                items[index] = new_text
                save()
                del pending_actions[user_id]

                await update.message.reply_text(
                    f"Updated in *{list_name}*:\n{old} → {new_text}",
                    parse_mode="Markdown"
                )
                return

    # show all lists
    if text.lower() == "lists":
        if not lists:
            await update.message.reply_text("No lists available")
            return
        await update.message.reply_text(
            "\n".join([f"• {name}" for name in lists]),
            parse_mode="Markdown"
        )
        return

    # create list
    if text.lower().startswith("create list -"):
        list_name = text.split("-", 1)[1].strip()

        # check if exists ignoring case
        existing = find_list(list_name)
        if existing:
            await update.message.reply_text("List already exists")
            return

        lists[list_name] = []
        save()
        await update.message.reply_text(f"Created: *{list_name}*", parse_mode="Markdown")
        return

    # delete mode start
    if text.lower().startswith("delete from"):
        raw_name = text.split("from", 1)[1].strip()
        list_name = find_list(raw_name)

        if not list_name:
            await update.message.reply_text("List not found")
            return
        if not lists[list_name]:
            await update.message.reply_text("List is empty")
            return

        pending_actions[user_id] = {"type": "delete", "list": list_name}

        items = lists[list_name]
        formatted = "\n".join([f"{i+1}. {v}" for i, v in enumerate(items)])

        await update.message.reply_text(
            f"{formatted}\n\nReply: delete 2",
            parse_mode="Markdown"
        )
        return

    # edit mode start
    if text.lower().startswith("edit from"):
        raw_name = text.split("from", 1)[1].strip()
        list_name = find_list(raw_name)

        if not list_name:
            await update.message.reply_text("List not found")
            return
        if not lists[list_name]:
            await update.message.reply_text("List is empty")
            return

        pending_actions[user_id] = {"type": "edit", "list": list_name}

        items = lists[list_name]
        formatted = "\n".join([f"{i+1}. {v}" for i, v in enumerate(items)])

        await update.message.reply_text(
            f"{formatted}\n\nReply: edit 2 -> new text",
            parse_mode="Markdown"
        )
        return

    # add item
    if "-" in text:
        name_part, item = [x.strip() for x in text.split("-", 1)]
        list_name = find_list(name_part)

        if list_name:
            lists[list_name].append(item)
            save()
            await update.message.reply_text(
                f"Added to *{list_name}*: {item}",
                parse_mode="Markdown"
            )
            return

    # show a list
    list_name = find_list(text)
    if list_name:
        items = lists[list_name]
        if not items:
            await update.message.reply_text(f"{list_name} is empty")
            return

        formatted = "\n".join([f"• {i}" for i in items])
        await update.message.reply_text(
            f"{list_name}\n{formatted}",
            parse_mode="Markdown"
        )
        return

    # help text
    await update.message.reply_text(
        "Commands:\n"
        "Create list - Name\n"
        "Name - Item\n"
        "lists\n"
        "Delete from Name\n"
        "delete 2\n"
        "Edit from Name\n"
        "edit 2 -> text\n"
        "Name"
    )


if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    print("Bot running...")
    app.run_polling()
