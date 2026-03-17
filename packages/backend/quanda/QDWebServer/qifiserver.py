from qaenv import mongo_ip
from quanda.QDWebServer.basehandles import QDBaseHandler
from quanda.QDUtil import QA_util_to_json_from_pandas
from quanda.QIFI.QifiManager import QA_QIFIMANAGER, QA_QIFISMANAGER

class QDQIFI_Handler(QDBaseHandler):
    manager = QA_QIFISMANAGER(mongo_ip, model='BACKTEST')

    def get(self):
        action = self.get_argument('action', 'acchistory')
        acc = self.get_argument('account_cookie', 'KTKS_t01_au2012_5min')
        manage_acc = QA_QIFIMANAGER(acc, mongo_ip)

        if action == 'acchistory':
            history_assets = manage_acc.assets
            history_assets.index = history_assets.index.map(str)
            self.write({'res': history_assets.to_dict()})
        elif action == 'monthprofit':
            self.write({'res': manage_acc.month_assets_profit.to_dict()})
        elif action == 'historytrade':
            res = manage_acc.trade.loc[:, ['commission', 'direction',
                                           'instrument_id', 'offset', 'price', 'trade_date_time', 'volume']].reset_index()
            res = res.assign(datetime=res.tradetime.map(str)).loc[:, ['commission', 'direction',
                                                                      'offset', 'price', 'trade_date_time', 'volume', 'code', 'datetime']]
            self.write({'res': QA_util_to_json_from_pandas(res)})
        elif action == 'holdingpanel':
            trading_day = self.get_argument('trading_day')
            res = self.manager.get_holding_panel(acc, trading_day)
            self.write({'res': QA_util_to_json_from_pandas(res)})


class QDQIFIS_Handler(QDBaseHandler):
    manager = QA_QIFISMANAGER(mongo_ip, model='BACKTEST')

    def get(self):
        action = self.get_argument('action', 'acchistory')

        if action == 'accountlist':
            res = self.manager.get_allaccountname()
            self.write({'res': res})
        elif action == 'portfoliolist':
            res = self.manager.get_allportfolio()
            self.write({'res': res})
        elif action == 'accountinportfolio':
            portfolio = self.get_argument('portfolio', 't12')
            res = self.manager.get_portfolio_panel(portfolio)
            self.write({'res': QA_util_to_json_from_pandas(res)})

    def post(self):
        action = self.get_argument('action', 'change_name')
        if action == 'drop_account':
            account_cookie = self.get_argument('account_cookie')
            res = self.manager.drop_account(account_cookie)
            self.write({
                'res': res,
                'status': 200
            })
        elif action == 'drop_many':
            account_cookies = self.get_argument('account_cookies')
            res = self.manager.drop_many(account_cookies)
            self.write({
                'res': res,
                'status': 200
            })


class QDQIFIS_REALTIME_Handler(QDBaseHandler):
    manager = QA_QIFISMANAGER(mongo_ip, model='REALTIME')

    def get(self):
        action = self.get_argument('action', 'acchistory')

        if action == 'accountlist':
            res = self.manager.get_allaccountname()
            self.write({'res': res})
        elif action == 'portfoliolist':
            res = self.manager.get_allportfolio()
            self.write({'res': res})
        elif action == 'accountinportfolio':
            portfolio = self.get_argument('portfolio', 't12')
            res = self.manager.get_portfolio_panel(portfolio)
            self.write({'res': QA_util_to_json_from_pandas(res)})

    def post(self):
        action = self.get_argument('action', 'change_name')
        if action == 'drop_account':
            account_cookie = self.get_argument('account_cookie')
            res = self.manager.drop_account(account_cookie)
            self.write({
                'res': res,
                'status': 200
            })
        elif action == 'drop_many':
            account_cookies = self.get_argument('account_cookies')
            res = self.manager.drop_many(account_cookies)
            self.write({
                'res': res,
                'status': 200
            })
