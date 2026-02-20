import os
import asyncio

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

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
        "/sua <id|pass|2fa|...>\n"
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

# /sua
async def edit_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return

    if not context.args:
        await update.message.reply_text("Vui lòng nhập:\n/sua id|pass|2fa|...")
        return

    new_data = " ".join(context.args)

    if "|" not in new_data:
        await update.message.reply_text("Sai định dạng. Phải là id|pass|2fa|...")
        return

    new_id = new_data.split("|")[0]

    updated = False
    lines = []

    # Đọc file
    with open(FILE_NAME, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Ghi đè nếu trùng id
    for i in range(len(lines)):
        if lines[i].startswith(new_id + "|"):
            lines[i] = new_data + "\n"
            updated = True
            break

    # Nếu không tìm thấy thì thêm mới
    if not updated:
        lines.append(new_data + "\n")

    # Ghi lại file
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        f.writelines(lines)

    if updated:
        await update.message.reply_text("✏️ Đã cập nhật tài khoản!")
    else:
        await update.message.reply_text("➕ ID chưa tồn tại. Đã thêm mới!")


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_account))
    app.add_handler(CommandHandler("xem", view_account))
    app.add_handler(CommandHandler("xemall", view_all))
    app.add_handler(CommandHandler("sua", edit_account))

    print("Bot đang chạy...")
    app.run_polling()


if __name__ == "__main__":
    main()
