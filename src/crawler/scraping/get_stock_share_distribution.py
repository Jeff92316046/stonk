import time
from database.repository.stock_list_repository import (
    get_all_stock,
    upsert_stock_date_by_symbol,
    Stocks,
)
from database.repository.stock_share_distribution_repository import (
    upsert_stock_share_distributions,
    stockSD,
)
from crawler.utils.selenuim_helper import TAG_NAME, XPATH, get_driver
from selenium.webdriver.remote.webelement import WebElement
from datetime import datetime
from prefect import task
from prefect.logging import get_run_logger
from prefect.cache_policies import NO_CACHE

MAX_CONCURRENT_TASKS = 1
STOCK_SHARE_DISTRIBUTION_URL = "https://www.tdcc.com.tw/portal/zh/smWeb/qryStock"


def parse_stocksd_data(table: WebElement, stock_symbol: str, date: str) -> int:
    rows = table.find_elements(TAG_NAME, "tr")
    if len(rows) == 1:  # 處理沒資料的情形
        upsert_stock_date_by_symbol(stock_symbol, datetime.strptime(date, "%Y%m%d").date())
        return 0
    if len(rows) == 17:  # 處理有補差額的情形
        rows[15], rows[16] = rows[16], rows[15]
    stocksds: list[stockSD] = []
    for row in rows:
        columns = row.find_elements(TAG_NAME, "td")
        stocksds.append(
            stockSD(
                stock_symbol=stock_symbol,
                date_time=datetime.strptime(date, "%Y%m%d").date(),
                holding_order=int(columns[0].text.strip()),
                number_of_holder=(
                    int(columns[2].text.strip().replace(",", ""))
                    if columns[2].text.strip() != ""
                    else None
                ),
                shares=int(columns[3].text.strip().replace(",", "")),
                created_at=datetime.today().date(),
            )
        )
    if len(rows) == 17:
        stocksds[15].holding_order, stocksds[16].holding_order = (
            stocksds[16].holding_order,
            stocksds[15].holding_order,
        )
    result = upsert_stock_share_distributions(stocksds)
    upsert_stock_date_by_symbol(stock_symbol, datetime.strptime(date, "%Y%m%d").date())
    return result


@task(cache_policy=NO_CACHE, retries=3)
def fetch_stocksd_data_by_symbol(stock: Stocks):
    with get_driver() as driver:
        try:
            driver.get(STOCK_SHARE_DISTRIBUTION_URL)
            select = driver.find_element(XPATH, "//*[@id='scaDate']")  # 確保 ID 正確
            options = select.find_elements(TAG_NAME, "option")
            last_updated_at = (
                stock.last_updated_at.strftime("%Y%m%d")
                if stock.last_updated_at
                else ""
            )
            newer_dates = [
                option.get_attribute("value")
                for option in options
                if option.get_attribute("value") > last_updated_at
            ][::-1]
            if len(newer_dates) == 0:
                return
            time.sleep(0.5)
            driver.find_element(
                XPATH,
                "//*[@id='StockNo']",
            ).send_keys(stock.stock_symbol)
            time.sleep(0.3)
            for date in newer_dates:
                select = driver.find_element(XPATH, "//*[@id='scaDate']")
                select.find_element(XPATH, f".//option[@value='{date}']").click()
                time.sleep(0.3)
                driver.find_element(
                    XPATH, "//*[@id='form1']/table/tbody/tr[4]/td/input"
                ).click()
                table = driver.find_element(
                    XPATH, "//*[@id='body']/div/main/div[6]/div/table/tbody"
                )
                result = parse_stocksd_data(table, stock.stock_symbol, date)
                if result == 0:
                    get_run_logger().warning(
                        f"stock {stock.stock_symbol} date {date} is already exists"
                    )
                else:
                    get_run_logger().info(
                        f"stock {stock.stock_symbol} date {date} inserted"
                    )
                time.sleep(0.3)
            return True
        except Exception as e:
            get_run_logger().error(f"Error in {stock.stock_symbol} : {e}")


@task
def get_all_stocksd_data():
    latest_date = ""
    with get_driver() as driver:
        driver.get(STOCK_SHARE_DISTRIBUTION_URL)
        select = driver.find_element(XPATH, "//*[@id='scaDate']")
        option = select.find_elements(TAG_NAME, "option")[0]
        latest_date = option.get_attribute("value")
    stock_list = get_all_stock()
    for stock in stock_list:
        last_updated_at = (
            stock.last_updated_at.strftime("%Y%m%d") if stock.last_updated_at else ""
        )
        if last_updated_at == latest_date:
            continue
        fetch_stocksd_data_by_symbol.with_options(
            name=f"fetch_stocksd_data_{stock.stock_symbol}"
        )(stock)


# TODO check last date to filter stock
