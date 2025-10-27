{
    'name': 'GLS Italy Shipping Integration',
    'category': 'Website',
    'author': "Vraja Technologies",
    'version': '18.0.1.0',
    'summary': """At 𝗩𝗿𝗮𝗷𝗮 𝗧𝗲𝗰𝗵𝗻𝗼𝗹𝗼𝗴𝗶𝗲𝘀, we continue to innovate as a globally renowned 𝘀𝗵𝗶𝗽𝗽𝗶𝗻𝗴 𝗶𝗻𝘁𝗲𝗴𝗿𝗮𝘁𝗼𝗿 𝗮𝗻𝗱 𝗢𝗱𝗼𝗼 𝗰𝘂𝘀𝘁𝗼𝗺𝗶𝘇𝗮𝘁𝗶𝗼𝗻 𝗲𝘅𝗽𝗲𝗿𝘁. Our widely accepted shipping connections are made to easily interface with Odoo, simplifying everything from creating labels to tracking shipments—all from a single dashboard. We’re excited to introduce GLS Italy Odoo Connectors your one stop solution for seamless global shipping management, now available on the Odoo App Store! At Vraja Technologies, we continue to be at the forefront of Odoo shipping integrations, ensuring your logistics run smoothly across countries. Users also search using these keywords Vraja Odoo Shipping Integration, Vraja Odoo shipping Connector, Vraja Shipping Integration, Vraja shipping Connector, GLS Italy Odoo Shipping Integration, GLS Italy Odoo shipping Connector, GLS Italy Shipping Integration, GLS Italy shipping Connector, GLS Italy vraja technologies, gls vraja technologies, Odoo GLS Italy, gls, gls shipping, gls shipping integration, gls connector, gls shipping connector, shipping connector..""",
    'description': "GLS Italy Shipping Integration",
    'depends':  ['delivery','stock','stock_delivery'],
    'data': [
             'views/res_company.xml',
             'views/delivery_carrier.xml',
             ],
    'images': ['static/description/cover.gif'],
    'maintainer': 'Vraja Technologies',
    'website': 'https://www.vrajatechnologies.com',
    'demo': [],
    'live_test_url': 'https://www.vrajatechnologies.com/contactus',
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': '199',
    'currency': 'EUR',
    'license': 'OPL-1',
    'cloc_exclude': [
        "models/*",
        "static/*",
        "view/*",
    ]
}


