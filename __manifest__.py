{
    'name': "PayOS Payment",
    'version': '1.0',
    'depends': ['payment'],
    'category': 'Accounting/Payment Providers',
    'description': """
        Tích hợp cổng thanh toán PayOS vào Odoo 16.
    """,
    'data': [
        'views/payment_payos_templates.xml', 
        'views/payment_provider_views.xml', 
        'data/payment_provider_data.xml',
    ],
    
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False, 
}
