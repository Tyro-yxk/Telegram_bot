# update.py
import re
import requests


def login(user):
    url = "https://xn--yet.xn--766a.top/api/v1/passport/auth/login"
    result = requests.post(url, data=user)
    if result.status_code == 200:
        return 200, result.json()
    return -1, "登录失败"


def get_subscription(_header):
    url = "https://xn--yet.xn--766a.top/api/v1/user/plan/fetch"
    result = requests.get(url, headers=_header)
    if result.status_code == 200:
        data = result.json()
        for i in data.get("data"):
            if bool(re.search("免费套餐", i["name"])):
                return 200, i["id"]
        return -2, "找不到免费套餐"
    return -3, "列表获取失败"


def check(coupon_code, _plan_id, _header):
    url = "https://xn--yet.xn--766a.top/api/v1/user/coupon/check"
    data = {
        "code": coupon_code,
        "plan_id": _plan_id
    }
    result = requests.post(url, data=data, headers=_header)
    if result.status_code == 200:
        data = result.json()
        return 200, data
    return -4, "优惠码验证失败"


def save(_plan_id, _period, _coupon_code, _header):
    url = "https://xn--yet.xn--766a.top/api/v1/user/order/save"
    data = {
        "plan_id": _plan_id,
        "period": _period,
        "coupon_code": _coupon_code
    }
    result = requests.post(url, data=data, headers=_header)
    if result.status_code == 200:
        data = result.json()
        return 200, data
    return -6, "订单保存失败"


def checkout(_trade_no, _method, _header):
    url = "https://xn--yet.xn--766a.top/api/v1/user/order/checkout"
    data = {
        "trade_no": _trade_no,
        "method": _method
    }
    result = requests.post(url, headers=_header, data=data)
    if result.status_code == 200:
        return result.status_code, result.json()
    return -8, "支付失败"


def subscription(coupon_id, user):
    subscription_code = 0
    plan_id = 0
    check_id = 0
    check_data = {}
    period = ""
    save_id = 0
    save_value = ""
    detail_id = 0
    detail_data = ""
    checkout_id = 0
    checkout_data = ""
    token = ""
    header = {}

    login_id, auth = login(user)
    if login_id == 200:
        token = auth.get("data").get("token")
        header = {
            "authorization": auth.get("data").get("auth_data")
        }
        subscription_code, plan_id = get_subscription(header)
    if subscription_code == 200:
        # subscribe(plan_id, header)
        check_id, check_data = check(coupon_id, plan_id, header)
    if check_id == 200:
        period = check_data.get("data").get("limit_period")[0]
        save_id, save_data = save(plan_id, period, coupon_id, header)
        save_value = save_data.get("data")
    if save_id == 200:
        checkout_id, checkout_data = checkout(_trade_no=save_value, _method=1, _header=header)
    return {
        "code": [login_id, subscription_code, check_id, save_id, checkout_id],
        "value": [auth, plan_id, check_data, save_value, checkout_data]
    }


def renew_subscription(coupon_id, user):
    return subscription(coupon_id, user)
