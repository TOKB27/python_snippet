import schedule
import time

def job():
    print("タスクが実行されました")

# 毎日21時にタスクを実行
schedule.every().day.at("21:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
