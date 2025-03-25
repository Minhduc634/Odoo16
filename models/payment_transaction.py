import requests
import json
from odoo import models, fields, api
from odoo.tools import float_round

PAYOS_API_URL = "https://api.payos.vn/v2/payment-requests"

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    payos_payment_url = fields.Char(string="PayOS Payment URL")

    def _get_payos_payment_url(self, amount, currency, reference):
        provider = self.provider_id
        headers = {
            "x-api-key": provider.payos_api_key,
            "Content-Type": "application/json",
        }
        data = {
            "clientId": provider.payos_client_id,  # Thêm clientId vào request
            "orderCode": reference,
            "amount": int(amount),  # PayOS yêu cầu số nguyên
            "description": f"Thanh toán đơn hàng {reference}",
            "returnUrl": "/payment/payos/return",
            "cancelUrl": "/payment/payos/cancel",
            "webhookUrl": "/payment/payos/webhook"
        }
        response = requests.post(PAYOS_API_URL, headers=headers, json=data)
        if response.status_code == 200:
            return response.json().get("checkoutUrl")
        return False
