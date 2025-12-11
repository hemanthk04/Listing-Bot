# **Telegram List Manager Bot**

A simple personal Telegram bot to create, manage, edit, and delete lists using easy text commands.
Useful for Substack ideas, watchlists, notes, reminders, and anything else you want to track.

---

## 🚀 **Features**

* Create unlimited lists
* Add items easily
* Delete items using index
* Edit items using index
* Case-insensitive list handling
* JSON-based local storage (no database needed)

---

## 🛠️ **Installation (Local Machine)**

### **1. Clone this repository**

```bash
git clone https://github.com/yourusername/telegram-list-bot.git
cd telegram-list-bot
```

### **2. Install dependencies**

```bash
pip install -r requirements.txt
```

### **3. Add your Telegram Bot Token**

Create a file named **config.py** inside the project:

```python
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
```

(Do NOT commit your actual token — it’s ignored using `.gitignore`)

### **4. Run the bot**

```bash
python bot.py
```

You should see:

```
Bot is running...
```

Now open Telegram and start messaging your bot.

---

## 📌 **Commands**

### **Create a list**

```
Create list - Movie Watchlist
```

### **Add an item**

```
Movie Watchlist - Interstellar
```

### **Show all lists**

```
lists
```

### **Show a specific list**

```
Movie Watchlist
```

### **Delete an item (step 1)**

```
Delete from Movie Watchlist
```

Bot will show:

```
1. Interstellar
Reply with: delete 1
```

### **Delete an item (step 2)**

```
delete 1
```

### **Edit an item (step 1)**

```
Edit from Movie Watchlist
```

Bot will show:

```
1. Interstellar
Reply with: edit 1 -> new text
```

### **Edit an item (step 2)**

```
edit 1 -> Interstellar (2014)
```

---

## 🤝 **Contribute**

This is a simple utility bot made for personal use — but feel free to:

* Suggest new features
* Open issues
* Create pull requests

Ideas that would be awesome:

* Inline keyboard buttons
* Cloud sync (Google Drive / Firebase)
* Export list as PDF / text
* Search inside lists
* Undo last delete
* Auto-backup

If you build something cool, definitely contribute!
