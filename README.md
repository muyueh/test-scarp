# 聯合報新聞爬蟲

這個專案提供一個簡單的 Python 指令列工具，用來抓取聯合報（UDN）的即時新聞資料。程式會透過官方的 JSON API 取得最新文章，包含標題、連結、摘要、發佈時間以及封面圖片網址，並輸出為 JSON 格式。

## 使用方式

```bash
python udn_crawler.py --pages 2 --output udn.json
```

常用參數說明：

- `--pages`：要抓取的頁數，預設為 1。
- `--delay`：每次請求之間的延遲秒數，預設為 1 秒，避免對伺服器造成壓力。
- `--category-id`、`--channel-id`、`--type`：對應聯合報 API 的參數，預設為即時新聞。
- `--output`：輸出檔案路徑；若不指定，結果會輸出到標準輸出。

## 執行結果

指令執行後會得到一個 JSON 陣列，每個元素即為一篇新聞，例如：

```json
[
  {
    "title": "宜蘭泉月樓行館超狂防水一夕爆紅 卻有違建、農地未農用遭裁罰",
    "link": "https://udn.com/news/story/7320/8663558",
    "summary": "宜蘭五結鄉泉月樓行館以「防水超強」為賣點...",
    "time": "2024-03-20 12:34",
    "image": "https://pgw.udn.com.tw/gw/photo.php?u=..."
  }
]
```

> **提示**：執行前請確認環境能夠連線到 `https://udn.com`，並且適度調整延遲時間。
