import json
import os
import threading
import time
import sys
from typing import List, Dict
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, Application

from update import renew_subscription

# 使用Event来通知线程关闭
shutdown_event = threading.Event()


# 初始化配置
def load_config():
    _token = os.environ.get('BOT_TOKEN')
    user_info = os.environ.get('USER_INFO')

    if not _token or not user_info:
        with open('config.json', 'r') as f:
            config = json.load(f)
            _token = config.get('BOT_TOKEN', _token)
            user_info = config.get('USER_INFO', user_info)

    return _token, json.loads(user_info) if isinstance(user_info, str) else user_info


bot_token, user_json = load_config()


async def handle_coupon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = ""
    try:
        msg = update.message
        if len(context.args) > 0:
            coupon_code = ''.join(context.args)
        else:
            await msg.reply_text("请直接发送您的优惠码")
            return

        print("优惠码: ", coupon_code)

        for user in user_json:
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
                print(reply)
            else:
                reply = f"❌ {user.get('email')} 续订失败\n原因: {result_message}"
                await msg.reply_text(reply)
                print(reply)

    except Exception as e:
        error_msg = f"⚠️ 处理优惠码时出错: {str(e)}"
        await msg.reply_text(error_msg)
        print(error_msg)


class BotRunner:
    def __init__(self):
        self.application: Application = None

    async def shutdown(self):
        if self.application:
            await self.application.stop()
            await self.application.shutdown()

    def run(self):
        self.application = ApplicationBuilder().token(bot_token).build()
        self.application.add_handler(CommandHandler(["update"], handle_coupon))
        print("机器人开始运行...")

        # 添加检查shutdown_event的循环
        self.application.run_polling(stop_signals=None)  # 禁用默认的信号处理

        # 等待关闭事件
        while not shutdown_event.is_set():
            time.sleep(1)

        # 收到关闭事件后执行清理
        print("收到关闭信号，正在停止机器人...")
        self.application.loop.run_until_complete(self.shutdown())


def timer_thread(duration):
    print(f"计时器已启动，将在{duration}秒后关闭程序...")
    time.sleep(duration)
    print("计时结束，发送关闭信号...")
    shutdown_event.set()  # 设置事件通知主线程关闭
    os._exit(0)


if __name__ == "__main__":
    # 设置计时时长（秒），例如3600秒=1小时
    timer_duration = 5

    # 创建并启动计时器线程
    timer = threading.Thread(target=timer_thread, args=(timer_duration,))
    timer.daemon = True
    timer.start()

    # 创建并运行机器人
    bot_runner = BotRunner()

    try:
        bot_runner.run()
    except KeyboardInterrupt:
        print("\n收到键盘中断信号，正在关闭程序...")
        shutdown_event.set()
    finally:
        # 等待所有线程结束
        timer.join(timeout=1)
        print("程序已退出")
        sys.exit(0)
