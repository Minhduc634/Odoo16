from odoo import models, fields, api
import requests
import json
import logging
from odoo.http import request

_logger = logging.getLogger(__name__)

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
            "clientId": provider.payos_client_id,
            "orderCode": reference,
            "amount": int(amount),
            "description": f"Thanh toán đơn hàng {reference}",
            "returnUrl": "/payment/payos/return",
            "cancelUrl": "/payment/payos/cancel",
            "webhookUrl": "/payment/payos/webhook"
        }
        response = requests.post(PAYOS_API_URL, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            checkout_url = result.get("checkoutUrl")
            # Nếu URL không phải là tuyệt đối, thêm domain nếu cần
            if checkout_url and not checkout_url.startswith("http"):
                checkout_url = "https://payos.vn" + checkout_url
            return checkout_url
        _logger.error("API PayOS error: %s", response.text)
        return False

    def _processRedirectPayment(self, data):
        _logger.info("Bắt đầu _processRedirectPayment với data: %s", json.dumps(data, indent=2))
        print("đã vào đây")
        payment_url = self._get_payos_payment_url(data.get("amount"), data.get("currency"), self.reference)
        if not payment_url:
            _logger.error("Không tạo được link thanh toán từ PayOS")
            return super()._processRedirectPayment(data)
        self.write({'payos_payment_url': payment_url})
        # Tạo các giá trị cần truyền vào template
        values = {
            'payos_url': payment_url,
            'orderCode': self.reference,
            'amount': int(data.get("amount")),
            'currency': data.get("currency"),
            'return_url': "/payment/payos/return",
            'cancel_url': "/payment/payos/cancel",
            'webhook_url': "/payment/payos/webhook",
        }
        # Trả về giao diện được render từ template "payment_payos.checkout"
        return request.render("payment_payos.checkout", values)
