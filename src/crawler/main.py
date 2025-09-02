from crawler.scraping.get_stock_share_distribution import get_all_stocksd_data
from crawler.scraping.get_broker_trade_daily import (
    get_stock_broker_trade_daily_in_watchlist,
)
from crawler.scraping.update_stock_list import update_stock_list
from prefect import flow, serve


@flow
def main():
    update_stock_list()
    get_all_stocksd_data()


@flow
def broker_trade_daily():
    get_stock_broker_trade_daily_in_watchlist()


if __name__ == "__main__":
    serve(
        main.to_deployment(name="stock_crawler", cron="0 0 * * 7"),
        broker_trade_daily.to_deployment(name="broker_trade_daily", cron="30 9 * * 1-5"),
    )
