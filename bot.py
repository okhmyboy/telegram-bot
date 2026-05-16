import telebot
import requests
import json
import os
from flask import Flask
from threading import Thread
from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    KeyboardButtonRequestUsers
)

BOT_TOKEN = "8797340595:AAGQ-M3Rg_VTKoFO2lEGVHbACrXelfFbTTc"

bot = telebot.TeleBot(
    BOT_TOKEN,
    parse_mode="HTML"
)

ADMIN_ID = "7503104119"
GROUP_ID = -1003638269375

API = "https://tgtonum.xclusor.workers.dev/?key=xclusor&id="

session = requests.Session()
app = Flask('')

@app.route('/')
def home():
    return "Bot Running"

def run():
    app.run(
    host='0.0.0.0',
    port=int(os.environ.get('PORT', 8080))
    )

def keep_alive():
    t = Thread(target=run)
    t.start()
DB_FILE = "database.json"

users = {}
plans = {}
creditplans = {}
waiting = {}
temp = {}

# ---------------- DATABASE ---------------- #

def load_db():

    global users, plans, creditplans

    if os.path.exists(DB_FILE):

        with open(DB_FILE, "r") as f:

            data = json.load(f)

            users = data.get("users", {})
            plans = data.get("plans", {})
            creditplans = data.get("creditplans", {})


def save_db():

    with open(DB_FILE, "w") as f:

        json.dump({
            "users": users,
            "plans": plans,
            "creditplans": creditplans
        }, f, indent=4)


load_db()

# ---------------- START ---------------- #

@bot.message_handler(commands=['start'])
def start(message):

    user_id = str(message.chat.id)

    reply_markup = ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    req = KeyboardButtonRequestUsers(
        request_id=1,
        user_is_bot=False,
        max_quantity=1
    )

    user_btn = KeyboardButton(
        text="👤 USER ID",
        request_users=req
    )

    reply_markup.add(user_btn)

    markup = InlineKeyboardMarkup()

    markup.row(
        InlineKeyboardButton(
            "🔎 ENTER USER ID",
            callback_data="enter"
        )
    )

    markup.row(
        InlineKeyboardButton(
            "👤 MY PLAN",
            callback_data="myplan"
        ),

        InlineKeyboardButton(
            "💎 VIEW PLANS",
            callback_data="plans"
        )
    )

    markup.row(
        InlineKeyboardButton(
            "📞 CONTACT OWNER",
            url="https://t.me/okhmyboy"
        )
    )

    if user_id == ADMIN_ID:

        markup.row(
            InlineKeyboardButton(
                "⚙ ADMIN PANEL",
                callback_data="admin"
            )
        )
    
    bot.send_message(
        user_id,
        f"""
🔥 PREMIUM LOOKUP BOT 🔥

⚡ Fast Fetch
✅ Premium Access
✅ Full Admin Panel

Choose Option 👇
""",
        reply_markup=reply_markup
    )

    bot.send_message(
        user_id,
        "Choose from below 👇",
        reply_markup=markup
    )

# ---------------- CALLBACKS ---------------- #

@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    try:
        bot.answer_callback_query(call.id)
    except:
        pass

    user_id = str(call.message.chat.id)

    # ENTER
    if call.data == "enter":

        if user_id not in users:

            bot.send_message(
                user_id,
                "❌ No Active Plan"
            )
            return

        if users[user_id]["credits"] != "Unlimited":

            if int(users[user_id]["credits"]) <= 0:

                bot.send_message(
                    user_id,
                    "❌ No Credits Left"
                )
                return

        waiting[user_id] = "lookup"

        bot.send_message(
            user_id,
            "📥 Send User ID"
        )

    # MY PLAN
    elif call.data == "myplan":

        if user_id not in users:

            bot.send_message(
                user_id,
                "❌ No Active Plan"
            )
            return

        u = users[user_id]

        bot.send_message(
            user_id,
            f"""
👤 YOUR PLAN

📦 Plan: {u['plan']}
📅 Days: {u['days']}
💎 Credits: {u['credits']}
⚡ Per Day: {u['perday']}
"""
        )

    # VIEW PLANS
    elif call.data == "plans":

        text = "📦 SUBSCRIPTION PLANS\n\n"

        if len(plans) == 0:
            text += "❌ No Plans\n\n"

        for p in plans:

            x = plans[p]

            text += f"""
📦 {p}

📅 Days: {x['days']}
💎 Credits: {x['credits']}
⚡ Per Day: {x['perday']}
💰 Price: {x['price']}

"""

        text += "\n🎟 CREDIT PLANS\n\n"

        if len(creditplans) == 0:
            text += "❌ No Credit Plans"

        for p in creditplans:

            x = creditplans[p]

            text += f"""
🎟 {p}
💎 Credits: {x['credits']}
💰 Price: {x['price']}

"""

        bot.send_message(user_id, text)

    # ADMIN PANEL
    elif call.data == "admin":

        if user_id != ADMIN_ID:
            return

        markup = InlineKeyboardMarkup(row_width=2)

        buttons = [

            InlineKeyboardButton(
                "➕ ADD PLAN",
                callback_data="addplan"
            ),

            InlineKeyboardButton(
                "➖ REMOVE PLAN",
                callback_data="removeplan"
            ),

            InlineKeyboardButton(
                "🎟 ADD CREDIT PLAN",
                callback_data="creditplan"
            ),

            InlineKeyboardButton(
                "❌ REMOVE CREDIT PLAN",
                callback_data="removecreditplan"
            ),

            InlineKeyboardButton(
                "👤 ADD USER",
                callback_data="adduser"
            ),

            InlineKeyboardButton(
                "❌ REMOVE USER",
                callback_data="removeuser"
            ),

            InlineKeyboardButton(
                "💎 ADD CREDITS",
                callback_data="addcredits"
            ),

            InlineKeyboardButton(
                "➖ REMOVE CREDITS",
                callback_data="removecredits"
            ),

            InlineKeyboardButton(
                "📋 USER INFO",
                callback_data="userinfo"
            ),

            InlineKeyboardButton(
                "📊 TOTAL USERS",
                callback_data="stats"
            ),

            InlineKeyboardButton(
                "📢 BROADCAST",
                callback_data="broadcast"
            )
        ]

        markup.add(*buttons)

        bot.send_message(
            user_id,
            "⚙ ADMIN PANEL",
            reply_markup=markup
        )

    # ADD PLAN
    elif call.data == "addplan":

        waiting[user_id] = "plan_name"

        bot.send_message(
            user_id,
            "📦 Send Plan Name"
        )

    # REMOVE PLAN
    elif call.data == "removeplan":

        if len(plans) == 0:

            bot.send_message(
                user_id,
                "❌ No Plans"
            )
            return

        markup = InlineKeyboardMarkup()

        for p in plans:

            markup.row(
                InlineKeyboardButton(
                    p,
                    callback_data=f"deleteplan_{p}"
                )
            )

        bot.send_message(
            user_id,
            "Select Plan To Remove",
            reply_markup=markup
        )

    elif call.data.startswith("deleteplan_"):

        p = call.data.replace("deleteplan_", "")

        if p in plans:

            del plans[p]

            save_db()

            bot.edit_message_text(
                "✅ Plan Removed",
                call.message.chat.id,
                call.message.message_id
            )

    # CREDIT PLAN
    elif call.data == "creditplan":

        waiting[user_id] = "creditplan"

        bot.send_message(
            user_id,
            "Send Like:\n10 Credits ₹20"
        )

    # REMOVE CREDIT PLAN
    elif call.data == "removecreditplan":

        if len(creditplans) == 0:

            bot.send_message(
                user_id,
                "❌ No Credit Plans"
            )
            return

        markup = InlineKeyboardMarkup()

        for p in creditplans:

            markup.row(
                InlineKeyboardButton(
                    p,
                    callback_data=f"deletecredit_{p}"
                )
            )

        bot.send_message(
            user_id,
            "Select Credit Plan",
            reply_markup=markup
        )

    elif call.data.startswith("deletecredit_"):

        p = call.data.replace("deletecredit_", "")

        if p in creditplans:

            del creditplans[p]

            save_db()

            bot.edit_message_text(
                "✅ Credit Plan Removed",
                call.message.chat.id,
                call.message.message_id
            )

    # ADD USER
    elif call.data == "adduser":

        waiting[user_id] = "adduser"

        bot.send_message(
            user_id,
            "Send User ID"
        )

    elif call.data.startswith("setplan_"):

        data = call.data.split("_")

        uid = data[1]
        plan = data[2]

        x = plans[plan]

        users[uid] = {
            "plan": plan,
            "days": x["days"],
            "credits": x["credits"],
            "perday": x["perday"]
        }

        save_db()

        try:

            bot.send_message(
                uid,
                f"""
🎉 PLAN ACTIVATED

📦 Plan: {plan}
📅 Days: {x['days']}
💎 Credits: {x['credits']}
⚡ Per Day: {x['perday']}
"""
            )

        except:
            pass

        bot.edit_message_text(
            "✅ User Added",
            call.message.chat.id,
            call.message.message_id
        )

    # REMOVE USER
    elif call.data == "removeuser":

        waiting[user_id] = "removeuser"

        bot.send_message(
            user_id,
            "Send User ID"
        )

    # ADD CREDITS
    elif call.data == "addcredits":

        waiting[user_id] = "addcredits_user"

        bot.send_message(
            user_id,
            "Send User ID"
        )

    elif call.data.startswith("creditselect_"):

        plan = call.data.replace("creditselect_", "")

        uid = temp[user_id]["uid"]

        x = creditplans[plan]

        credits = x["credits"]

        if uid not in users:

            users[uid] = {
                "plan": "Credits Only",
                "days": "0",
                "credits": credits,
                "perday": "0"
            }

        else:

            if users[uid]["credits"] != "Unlimited":

                users[uid]["credits"] = str(
                    int(users[uid]["credits"]) + int(credits)
                )

        save_db()

        try:

            bot.send_message(
                uid,
                f"""
🎉 CREDITS ADDED

🎟 Plan: {plan}
💎 Credits: {credits}
"""
            )

        except:
            pass

        bot.edit_message_text(
            "✅ Credits Added",
            call.message.chat.id,
            call.message.message_id
        )

    # REMOVE CREDITS
    elif call.data == "removecredits":

        waiting[user_id] = "removecredits"

        bot.send_message(
            user_id,
            "Send:\nUserID Credits"
        )

    # USER INFO
    elif call.data == "userinfo":

        text = "📋 ACTIVE USERS\n\n"

        if len(users) == 0:
            text += "❌ No Users"

        for uid in users:

            u = users[uid]

            text += f"""
🆔 {uid}
📦 {u['plan']}
💎 {u['credits']}

"""

        bot.send_message(user_id, text)

    # STATS
    elif call.data == "stats":

        bot.send_message(
            user_id,
            f"📊 Total Active Users: {len(users)}"
        )

    # BROADCAST
    elif call.data == "broadcast":

        waiting[user_id] = "broadcast"

        bot.send_message(
            user_id,
            "Send Broadcast Message"
        )

# ---------------- MESSAGE HANDLER ---------------- #

@bot.message_handler(
    func=lambda message:
    str(message.chat.id) in waiting
)
def messages(message):

    user_id = str(message.chat.id)

    action = waiting[user_id]

    # ADD PLAN NAME
    if action == "plan_name":

        temp[user_id] = {
            "name": message.text
        }

        waiting[user_id] = "plan_days"

        bot.send_message(
            user_id,
            "📅 Send Days"
        )

    # PLAN DAYS
    elif action == "plan_days":

        temp[user_id]["days"] = message.text

        waiting[user_id] = "plan_credits"

        bot.send_message(
            user_id,
            "💎 Send Credits\n(Or Unlimited)"
        )

    # PLAN CREDITS
    elif action == "plan_credits":

        temp[user_id]["credits"] = message.text

        waiting[user_id] = "plan_perday"

        bot.send_message(
            user_id,
            "⚡ Send Per Day Limit"
        )

    # PLAN PERDAY
    elif action == "plan_perday":

        temp[user_id]["perday"] = message.text

        waiting[user_id] = "plan_price"

        bot.send_message(
            user_id,
            "💰 Send Price"
        )

    # PLAN PRICE
    elif action == "plan_price":

        temp[user_id]["price"] = message.text

        x = temp[user_id]

        plans[x["name"]] = {
            "days": x["days"],
            "credits": x["credits"],
            "perday": x["perday"],
            "price": x["price"]
        }

        save_db()

        bot.send_message(
            user_id,
            "✅ Plan Added"
        )

        waiting.pop(user_id)

    # CREDIT PLAN
    elif action == "creditplan":

        try:

            text = message.text.strip()

            parts = text.split()

            credits = parts[0]
            price = parts[-1]

            plan_name = f"{credits} Credits"

            creditplans[plan_name] = {
                "credits": credits,
                "price": price
            }

            save_db()

            bot.send_message(
                user_id,
                "✅ Credit Plan Added"
            )

        except:

            bot.send_message(
                user_id,
                "❌ Invalid Format"
            )

        waiting.pop(user_id)

    # ADD USER
    elif action == "adduser":

        uid = message.text

        temp[user_id] = {
            "uid": uid
        }

        markup = InlineKeyboardMarkup()

        for p in plans:

            markup.row(
                InlineKeyboardButton(
                    p,
                    callback_data=f"setplan_{uid}_{p}"
                )
            )

        bot.send_message(
            user_id,
            "Select Plan",
            reply_markup=markup
        )

        waiting.pop(user_id)

    # REMOVE USER
    elif action == "removeuser":

        uid = message.text

        if uid in users:

            try:

                bot.send_message(
                    uid,
                    "❌ Your Plan Removed"
                )

            except:
                pass

            del users[uid]

            save_db()

            bot.send_message(
                user_id,
                "✅ User Removed"
            )

        else:

            bot.send_message(
                user_id,
                "❌ User Not Found"
            )

        waiting.pop(user_id)

    # ADD CREDITS USER
    elif action == "addcredits_user":

        temp[user_id] = {
            "uid": message.text
        }

        markup = InlineKeyboardMarkup()

        for p in creditplans:

            markup.row(
                InlineKeyboardButton(
                    p,
                    callback_data=f"creditselect_{p}"
                )
            )

        bot.send_message(
            user_id,
            "🎟 Select Credit Plan",
            reply_markup=markup
        )

        waiting.pop(user_id)

    # REMOVE CREDITS
    elif action == "removecredits":

        try:

            uid, credits = message.text.split()

            if uid in users:

                if users[uid]["credits"] != "Unlimited":

                    current = int(users[uid]["credits"])

                    new = current - int(credits)

                    if new < 0:
                        new = 0

                    users[uid]["credits"] = str(new)

                    save_db()

                try:

                    bot.send_message(
                        uid,
                        f"❌ {credits} Credits Removed"
                    )

                except:
                    pass

                bot.send_message(
                    user_id,
                    "✅ Credits Removed"
                )

        except:

            bot.send_message(
                user_id,
                "❌ Invalid Format"
            )

        waiting.pop(user_id)

    # BROADCAST
    elif action == "broadcast":

        total = 0

        for uid in users:

            try:

                bot.send_message(uid, message.text)

                total += 1

            except:
                pass

        bot.send_message(
            user_id,
            f"✅ Broadcast Sent To {total} Users"
        )

        waiting.pop(user_id)

    # LOOKUP
    elif action == "lookup":

        try:

            fetching = bot.send_message(
                user_id,
                "⚡ Fetching..."
            )

            response = session.get(
                API + message.text.strip(),
                timeout=5
            )

            found = None

            try:

                data = response.json()

                if isinstance(data, dict):

                    for key in [
                        "number",
                        "phone",
                        "mobile",
                        "result",
                        "data"
                    ]:

                        if key in data:

                            value = str(data[key]).strip()

                            if len(value) >= 8:

                                found = value
                                break

                elif isinstance(data, str):

                    value = data.strip()

                    if len(value) >= 8:

                        found = value

            except:

                text = response.text.strip()

                if text and len(text) >= 8:

                    found = text

            # SUCCESS
            if found:
               try:

                    log_text = f"""
🔍 NEW CHECK

Checked ID: {user_id}
👤 Username: @{message.from_user.username if message.from_user.username else "No Username"}
Target ID: {message.text.strip()}

📱 Number: {found}
✅ Number Found
"""

                        bot.send_message(
                            GROUP_ID,
                            log_text
                        )

                    except:
                        pass
                bot.edit_message_text(
                    f"""
✅ Number Fetched

📞 {found}
""",
                    chat_id=user_id,
                    message_id=fetching.message_id
                )

                # REMOVE CREDIT ONLY SUCCESS
                if users[user_id]["credits"] != "Unlimited":

                    current = int(users[user_id]["credits"])

                    if current > 0:

                        users[user_id]["credits"] = str(current - 1)

                        save_db()

            # FAIL
            else:
          try:

                    log_text = f"""
🔍 NEW CHECK

Checked ID: {user_id}
👤 Username: @{message.from_user.username if message.from_user.username else "No Username"}
Target ID: {message.text.strip()}

❌ Number Not Found
"""

                    bot.send_message(
                        GROUP_ID,
                        log_text
                    )

                except:
                    pass
                bot.edit_message_text(
                    """
❌ Number Not Found

💎 Credits Saved
""",
                    chat_id=user_id,
                    message_id=fetching.message_id
                )

        except:

            bot.send_message(
                user_id,
                "⚠ Server Busy"
            )

        waiting.pop(user_id)

print("⚡ BOT STARTED")
# ---------------- USER ID GETTER ---------------- #

@bot.message_handler(content_types=['users_shared'])
def shared(message):

    try:

        user_id = message.users_shared.users[0].user_id

        bot.send_message(
            message.chat.id,
            f"""
✅ USER SELECTED

🆔 User ID: <code>{user_id}</code>
""",
            parse_mode="HTML"
        )

    except Exception as e:

        bot.send_message(
            message.chat.id,
            str(e)
    )
keep_alive()
bot.infinity_polling(
    skip_pending=True,
    timeout=10,
    long_polling_timeout=5
)
