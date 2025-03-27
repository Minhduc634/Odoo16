from odoo import models, fields

class PaymentProviderPayOS(models.Model):
    _inherit = "payment.provider"

    code = fields.Selection(selection_add=[("payos", "PayOS")], ondelete={"payos": "set default"})
    payos_api_key = fields.Char("PayOS API Key")
    payos_secret_key = fields.Char("PayOS Secret Key")
    payos_client_id = fields.Char("PayOS Client ID")
