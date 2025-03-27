import json
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class PayOSController(http.Controller):

    @http.route('/payment/payos/checkout', type='http', auth='public', website=True)
    def payos_checkout(self, **kwargs):
        tx_id = kwargs.get("tx_id")
        if not tx_id:
            _logger.error("Không tìm thấy tx_id trong request checkout")
            return request.redirect('/shop/payment')
        transaction = request.env["payment.transaction"].sudo().browse(int(tx_id))
        if not transaction or not transaction.payos_payment_url:
            _logger.error("Giao dịch không tồn tại hoặc thiếu URL thanh toán")
            return request.redirect('/shop/payment')
        provider = transaction.provider_id
        base_url = provider.get_base_url() if hasattr(provider, 'get_base_url') else ''
        values = {
            "payos_url": transaction.payos_payment_url,
            "orderCode": transaction.reference,
            "amount": int(transaction.amount),
            "currency": transaction.currency_id.name,
            "return_url": base_url + "/payment/payos/return",
            "cancel_url": base_url + "/payment/payos/cancel",
            "webhook_url": base_url + "/payment/payos/webhook",
        }
        return request.render("payment_payos.payment_payos_templates", values)

    @http.route('/payment/payos/return', type='http', auth='public', methods=['GET'])
    def payos_return(self, **kwargs):
        _logger.info("PayOS Return: %s", json.dumps(kwargs))
        reference = kwargs.get("orderCode")
        if not reference:
            _logger.error("PayOS Return: orderCode không tồn tại!")
            return request.redirect('/shop/payment')
        transaction = request.env["payment.transaction"].sudo().search([("reference", "=", reference)], limit=1)
        if transaction:
            transaction._set_transaction_done()
            return request.redirect('/shop/confirmation')
        _logger.error("PayOS Return: Không tìm thấy giao dịch với reference %s", reference)
        return request.redirect('/shop/payment')

    @http.route('/payment/payos/cancel', type='http', auth='public', methods=['GET'])
    def payos_cancel(self, **kwargs):
        _logger.info("PayOS Cancel: %s", json.dumps(kwargs))
        return request.redirect('/shop/payment')

    @http.route('/payment/payos/webhook', type='json', auth='public', methods=['POST'])
    def payos_webhook(self):
        try:
            data = json.loads(request.httprequest.data)
            _logger.info("PayOS Webhook: %s", json.dumps(data))
            reference = data.get("orderCode")
            status = data.get("status")
            if not reference:
                _logger.error("PayOS Webhook: orderCode không tồn tại!")
                return "Missing orderCode", 400
            transaction = request.env["payment.transaction"].sudo().search([("reference", "=", reference)], limit=1)
            if not transaction:
                _logger.error("PayOS Webhook: Không tìm thấy giao dịch với reference %s", reference)
                return "Transaction not found", 404
            if status == "successful":
                transaction._set_transaction_done()
            else:
                transaction._set_transaction_cancel()
            return "OK"
        except Exception as e:
            _logger.exception("PayOS Webhook: Exception - %s", str(e))
            return "Error processing webhook", 500
