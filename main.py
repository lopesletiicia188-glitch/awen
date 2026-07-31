import os
import psycopg2

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)


TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")


def get_db():
    return psycopg2.connect(
        DATABASE_URL
    )


def init_db():

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS numbers(
        id SERIAL PRIMARY KEY,
        number TEXT UNIQUE,
        username TEXT,
        user_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()

    cur.close()
    conn.close()



async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "📱号码查重机器人\n\n发送号码即可检测"
    )



async def check_number(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    number = update.message.text.strip()

    user = update.message.from_user

    username = (
        "@" + user.username
        if user.username
        else "无用户名"
    )

    user_id = str(user.id)


    conn = get_db()
    cur = conn.cursor()


    cur.execute(
        """
        SELECT username,user_id
        FROM numbers
        WHERE number=%s
        """,
        (number,)
    )


    result = cur.fetchone()



    if result:

        await update.message.reply_text(
            f"⚠️号码已存在\n\n"
            f"首次上传用户：{result[0]}\n"
            f"Telegram ID：{result[1]}"
        )


    else:

        cur.execute(
            """
            INSERT INTO numbers
            (
            number,
            username,
            user_id
            )
            VALUES
            (%s,%s,%s)
            """,
            (
                number,
                username,
                user_id
            )
        )


        conn.commit()


        await update.message.reply_text(
            "✅号码保存成功"
        )


    cur.close()
    conn.close()



async def count(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    conn = get_db()
    cur = conn.cursor()


    cur.execute(
        "SELECT COUNT(*) FROM numbers"
    )


    total = cur.fetchone()[0]


    await update.message.reply_text(
        f"📊当前保存号码数量：{total}"
    )


    cur.close()
    conn.close()



init_db()


app = Application.builder().token(TOKEN).build()


app.add_handler(
    CommandHandler(
        "start",
        start
    )
)


app.add_handler(
    CommandHandler(
        "count",
        count
    )
)


app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        check_number
    )
)


print("Bot running...")


app.run_polling()
