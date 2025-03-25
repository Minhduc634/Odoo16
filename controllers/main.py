import json
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class PayOSController(http.Controller):
    @http.route('/payment/payos/redirect', type='http', auth="public", website=True)
    def payos_redirect(self, **post):
        """ Chuyển hướng người dùng đến trang thanh toán PayOS """
        order_id = request.session.get('sale_order_id')
        if not order_id:
            _logger.error("Không tìm thấy sale_order_id trong session.")
            return request.redirect('/shop')

        sale_order = request.env['sale.order'].sudo().browse(order_id)
        if not sale_order:
            _logger.error(f"Không tìm thấy đơn hàng: {order_id}")
            return request.redirect('/shop')

        payment_transaction = sale_order.transaction_ids.filtered(lambda t: t.state == 'draft')
        if not payment_transaction:
            _logger.error("Không tìm thấy transaction hợp lệ.")
            return request.redirect('/shop')

        payos_url = payment_transaction.provider_reference
        if not payos_url:
            _logger.error("Không có URL thanh toán PayOS.")
            return request.redirect('/shop')

        return request.redirect(payos_url)
