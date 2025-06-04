import json
import os

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, ApplicationBuilder, Application

from update import renew_subscription
from notify import pushme


class TelegramBot:
    def __init__(self, config_name='config.json'):
        self.user_number = 0
        self.bot_token = ""
        self.user_json = {}
        self.app: Application = None
        self._config_name = config_name
        self.load_config()

    def load_config(self):
        self.bot_token = os.environ.get("BOT_TOKEN")
        user_info = os.environ.get("USER_INFO")

        if not self.bot_token or not user_info:
            with open(self._config_name, "r") as f:
                config = json.load(f)
                self.bot_token = config.get("BOT_TOKEN", self.bot_token)
                user_info = config.get("USER_INFO", user_info)
        self.user_json = json.loads(user_info) if isinstance(user_info, str) else user_info
        self.user_number = self.user_json

    async def handle_coupon(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = update.message
        try:
            if len(context.args) > 0:
                coupon_code = "".join(context.args)
            else:
                await msg.reply_text("请直接发送您的优惠码")
                return
            print("优惠码: ", coupon_code)
            for user in self.user_json:
                data = renew_subscription(coupon_code, user)
                success = True
                result_message = ""

                for index, value in enumerate(data.get("code", [])):
                    if value != 200:
                        success = False
                        result_message += data.get("value", [""])[index]
                        break
                if success:
                    reply = f"✅ {user.get('email')} 续订成功！\n{result_message}"
                    await msg.reply_text(reply)
                    pushme.send('鸡场签到', reply)
                    print(reply)
                else:
                    reply = f"❌ {user.get('email')} 续订失败\n原因: {result_message}"
                    await msg.reply_text(reply)
                    pushme.send('鸡场签到', reply)
                    print(reply)
            # self.shutdown()
        except Exception as e:
            error_msg = f"⚠️ 处理优惠码时出错: {str(e)}"
            await msg.reply_text(error_msg)
            pushme.send('鸡场签到', error_msg)
            print(error_msg)

    def setup_handlers(self) -> None:
        """Set up all command handlers"""
        self.app.add_handler(CommandHandler(["update"], self.handle_coupon))

    def run(self):
        if not self.bot_token:
            raise ValueError("Bot token not configured")
            # Create and configure application
        self.app = ApplicationBuilder().token(self.bot_token).build()

        # Set up handlers
        self.setup_handlers()

        # Start the bot
        print("Bot is running...")
        self.app.run_polling(stop_signals=None)

    def shutdown(self):
        self.app.stop()
        self.app.shutdown()
        print("Bot is shutting down...")
