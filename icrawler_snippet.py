### 画像をウェブから効率的にダウンロードする ###

from icrawler.builtin import GoogleImageCrawler

# GoogleImageCrawlerのインスタンスを作成
crawler = GoogleImageCrawler(storage={'root_dir': 'dog_images'})

# 画像を取得するための設定
crawler.crawl(keyword='dog', max_num=5)
