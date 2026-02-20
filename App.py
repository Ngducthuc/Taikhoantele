import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN chưa được thiết lập trong Environment Variables")

FILE_NAME = "taikhoan.txt"
ALLOWED_USERNAME = "savic888"

# Đảm bảo file tồn tại
if not os.path.exists(FILE_NAME):
    open(FILE_NAME, "a").close()


# 🔐 Kiểm tra quyền
def is_authorized(update: Update):
    user = update.effective_user
    return user and user.username == ALLOWED_USERNAME


# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return

    await update.message.reply_text(
        "Bot quản lý tài khoản\n\n"
        "/add <id|pass|2fa|...>\n"
        "/xem <id>\n"
        "/xemall"
    )


# /add
async def add_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return

    if not context.args:
        await update.message.reply_text("Vui lòng nhập:\n/add id|pass|2fa|...")
        return

    account_data = " ".join(context.args)

    with open(FILE_NAME, "a", encoding="utf-8") as f:
        f.write(account_data + "\n")

    await update.message.reply_text("✅ Đã lưu tài khoản!")


# /xem
async def view_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return

    if not context.args:
        await update.message.reply_text("Vui lòng nhập id:\n/xem id")
        return

    search_id = context.args[0]
    found = False

    with open(FILE_NAME, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith(search_id + "|"):
                await update.message.reply_text(f"🔎 Tìm thấy:\n{line.strip()}")
                found = True
                break

    if not found:
        await update.message.reply_text("❌ Không tìm thấy id này.")


# /xemall
async def view_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return

    with open(FILE_NAME, "r", encoding="utf-8") as f:
        data = f.read()

    if not data.strip():
        await update.message.reply_text("File trống.")
        return

    if len(data) > 4000:
        for i in range(0, len(data), 4000):
            await update.message.reply_text(data[i:i+4000])
    else:
        await update.message.reply_text(data)


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_account))
    app.add_handler(CommandHandler("xem", view_account))
    app.add_handler(CommandHandler("xemall", view_all))

    print("Bot đang chạy...")
    app.run_polling()


if __name__ == "__main__":
    main()
