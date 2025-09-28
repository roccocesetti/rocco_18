{
    'name': 'Odoo Marketplace and E-commerce Connector',
    'version': '18.0.0.0.0',
    'category': 'Ecommerce',
    'summary': 'Connect & Sell on 200+ marketplaces like Noon, Mirakl, Amazon, Temu, Shein, Kogan, Whatnot, Discogs, Flipkart, Iconic, The Range, Backmarket, Bandcamp, B&Q, Galaxus / Digitec, Wayfair, OnBuy, Farfetch, eBay, TikTok Shop, Reverb, Not On The High Street (NOTHs), CDiscount, Fruugo, Abebooks, Emag, Faire, Vivino, Walmart, Refurbed, Gunbroker, Groupon, Target Plus, Poshmark, Zalora, Jumia Vendor, Trademe, CDON, Miravia, Lazada, Vinted, Etsy, and more. Along with leading E-commerce platforms like Prestashop, ECWID, Shopify, WIX, BigCommerce, Woocommerce, Magento 2, Lightspeed, Commerce7. Retailer Networks such as CommerceHub / Rithum / Dsco, Rithum / OrderStream, Lowes, Home Depot. As well as Accounting & Shipping tools including QuickBooks Online, Shipstation, Royal Mail, Flexport, Amazon MCF, and Shiphero. All using just one connector. Why pay for multiple connectors when you can manage everything with Commercium?',
    'description': 'Commercium is a powerful integration platform that seamlessly connects your Odoo ERP with leading eCommerce marketplaces (Temu, eBay, Etsy, Amazon), shipping solutions, and other business systems. Automates order management, tracking, inventory sync, and product listing.',
    'depends': ['base', 'web', 'sale_management', 'stock', 'product', 'account', 'contacts'],
    'data': [
        'views/menu.xml',
        'views/settings_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'odoo_marketplace_and_e_commerce_connector/static/src/css/style.css',
            'odoo_marketplace_and_e_commerce_connector/static/src/css/custom_styles.css',
            'https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css',
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css',
            # 'odoo_marketplace_and_e_commerce_connector/static/description/static/slick/slick.min.js',
        ],
    },
    'author': "ConstaCloud Private Limited",
    'website': 'https://constacloud.com/commercium/oms/odoo-integration.html',
    'maintainer': 'ConstaCloud',
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': True,
    'images': ['static/description/cover.png'],
    'web_icon': 'static/description/icon.png',
    'external_dependencies': {
        'python': ['requests'],
    },
    "price": 449.95,
    "currency": "USD",   
    "contributors": [
        "Shubham Vajpayee <shubham.v@constacloud.com>",
        "Your Dev <help@mycommercium.com>",
    ],
    "keywords": ["odoo shopify connector, odoo temu connector, odoo shein connector, odoo amazon connector, odoo noon connector, odoo mirakl connector"],
    "support": "support@mycommercium.com",
    "sequence": 10

}
