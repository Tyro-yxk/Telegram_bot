import os
import sys
import threading
from time import sleep

from Bot import TelegramBot

shutdown_event = threading.Event()


def timer_thread(duration):
    print(f"计时器已启动，将在{duration}秒后关闭程序...")
    sleep(duration)
    print("计时结束，发送关闭信号...")
    shutdown_event.set()  # 设置事件通知主线程关闭
    os._exit(0)


if __name__ == "__main__":
    time_out = 5
    bot = TelegramBot()

    timer = threading.Thread(target=timer_thread, args=(time_out,))
    # timer.daemon = True
    timer.start()

    try:
        bot.run()
    except KeyboardInterrupt:
        print("\n收到键盘中断信号，正在关闭程序...")
        shutdown_event.set()
    finally:
        # 等待所有线程结束
        timer.join(1)
        print("程序已退出")
        sys.exit(0)
