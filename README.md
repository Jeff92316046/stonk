# Stonk

## 簡介 (Introduction)
本專案利用 Prefect 建立的 Stock Data Pipeline，透過 Selenium 自動爬取台灣公開的集保戶股權分散表跟每日交易日報，並使用 Streamlit 進行資料視覺化，透過自訓練 [model](https://github.com/Jeff92316046/crnn-captcha-break) 破解 CAPTCHA。

This project leverages Prefect to build a Stock Data Pipeline, using Selenium to automatically scrape publicly available Taiwan Depository & Clearing Corporation (TDCC) shareholder distribution data and daily trading reports. It also employs Streamlit for data visualization, and utilizes a self-trained model to break CAPTCHA.

## 啟動方法 (Getting Started)
### **需求 (Prerequisites)**
- Install Docker
- Install uv

### **環境模式 (Environment Modes)**
- `MODE=dev` ：本地測試用 (Local testing mode)
- `MODE=prod` ：生產環境使用 (Production mode)

### **步驟 (Setup Steps)**
```bash
git clone https://github.com/Jeff92316046/stock-data-pipeline.git
cd stock-data-pipeline
cp .env.sample .env
```

### **啟動專案 (Start the Project)**
- 使用 docker compose 啟動專案
```bash
docker compose up -d
```

- 使用 uv 啟動專案
  - run crawler
    ```bash
    uv sync
    cp src/crawler/main.py src/main.py
    uv python src/main.py
    ```
  - run dashboard
    ```bash
    uv sync
    cp src/dashboard/main.py src/main.py
    uv python src/main.py
    ```

## 目前功能 (Current Features)
- **自動化資料抓取**：定期從 **TDCC** 跟 **TWSE** 爬取 **集保戶股權分散表** 與 **每日交易日報** 資料。
- **資料視覺化**：透過 **Streamlit** 呈現股東級距分布。
- **可視化流程監控**：使用 **Prefect UI** 監控資料抓取與處理流程。

## 未來計畫 (Roadmap)
- **基於規則篩選潛力股**（Rule-based stock selection）。
- **機器學習模型訓練**（Training models for data analysis）。
- **股票價格爬取與整合**（Stock price collection and integration）。
- **優化資料搜尋功能**（Enhancing search by stock name）。

## 專案結構 (Project Structure)
重要檔案架構說明
```
stock-data-pipeline/
├── data/                   # 資料庫的 Volume 綁定目錄
├── src/
│   ├── crawler/            # 爬取資料的模組
│   │   ├── scraping/       # 爬取資料的腳本
│   │   ├── Dockerfile      # 構建爬蟲容器的 Dockerfile
│   │   ├── main.py         # 爬蟲的入口點 (Entrypoint)
│   ├── dashboard/          # 資料視覺化儀表板
│   │   ├── service.py      # UI 與資料庫之間的邏輯層
│   │   ├── main.py         # UI 介面 (Entrypoint)
│   │   ├── Dockerfile      # 構建儀表板容器的 Dockerfile
│   ├── database/           # 資料庫相關操作
│   │   ├── migrate/        # Alembic 資料庫遷移腳本
│   │   ├── repository/     # 以 Repository Pattern 封裝的 DB 操作
│   │   ├── db_helper.py    # 資料庫相關設定
│   │   ├── model.py        # 資料表欄位定義
│   │   ├── alembic.ini     # Alembic 設定檔
├── .env.sample             # .env 設定範例
├── docker-compose.yml      # Docker Compose 設定檔
├── pyproject.toml          # Python 套件管理設定
```

## 資料來源 (Data Source)
[台灣集中保管結算所 (TDCC)](https://www.tdcc.com.tw/portal/zh)
[買賣日報表查詢系統 (TWSE)](https://bsr.twse.com.tw/bshtm/)

> ⚠ **聲明 (Disclaimer)**
> 本專案僅供學習用途，股票投資有風險，買賣需審慎評估，**本專案不對任何投資行為負責**。
> 
> This project is for educational purposes only. Stock investments involve risks. **We do not take responsibility for any investment decisions.**

