from odoo import models, fields, api
from urllib.parse import urlparse
import requests
import secrets
# from odoo.addons.base.models.res_users_apikeys import ResUsersApikeys

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    platform_connected = fields.Boolean(
        string="Platform Connected",
        config_parameter='platform_connected'  # this connects it with ir.config_parameter
    )
    platform_id = fields.Char(
        string="Platform ID",
        config_parameter='platform_id'
    )

    def get_values(self):
        res = super().get_values()
        param = self.env['ir.config_parameter'].sudo()
        platform_connected = param.get_param('platform_connected') or 'False'
        res.update({
            'platform_connected': platform_connected.lower() in ['1', 'true', 'yes']
        })
        return res

    def set_values(self):
        super().set_values()
        param = self.env['ir.config_parameter'].sudo()
        param.set_param('platform_connected', str(self.platform_connected))

    commercium_username = fields.Char(
        string="Username : ",
        config_parameter='commercium_connector.username'
    )
    commercium_password = fields.Char(
        string="Password : ",
        config_parameter='commercium_connector.password'
    )
    commercium_db = fields.Char(
        string="Database : ",
        config_parameter='commercium_connector.db'
    )
    commercium_domain = fields.Char(
        string="Domain : ",
        config_parameter='commercium_connector.domain'
    )
    
    commercium_api_key = fields.Char(
        string="API Key : ",
        readonly=True
    )

    @api.model
    def disconnect_platform(self):
        print('Hello - disconnect_platform')
        try:
            # Dummy URL – replace with actual Commercium endpoint
            url = f"https://commercium-dev.constacloud.com/handle-oauth-callback?available_platform_name=ODOO&platform_id={self.platform_id}"
            print("url : ", url)
            response = requests.post(f"{url}", json={
                "platform_id": self.env.company.id,  # or any identifier
            })
            print("response.status_code : ", response.status_code)
            print("response.json() : ", response.json())

            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    # Set flag off
                    self.env['ir.config_parameter'].sudo().set_param("platform_connected", '0')
                    return {"success": True}
                else:
                    return {"success": False, "error": result.get("message", "Unknown error")}
            else:
                return {"success": False, "error": "HTTP Error {}".format(response.status_code)}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def action_connect_platform(self):
        print("`action_connect_platform` method called")
        self.ensure_one()
        self.platform_connected = True

    def action_disconnect_platform(self):

        error_message = "Platform disconnection failed. Please try again later."
        
        # Dummy URL – replace with actual Commercium endpoint
        url = f"https://commercium-dev.constacloud.com/market_connect/handle-oauth-callback?available_platform_name=ODOO&platform_id={self.platform_id}"
        response = requests.get(f"{url}")
        if response.status_code == 200:
            response_data = response.json()
            response_status_code = response_data.get("status_code")
            if response_status_code not in [200, 201]:
                error_message = response_data.get("message", "Unknown error")

            if response_status_code in [200, 201]:

                self.env['ir.config_parameter'].sudo().set_param('platform_connected', False)
                self.ensure_one()
                self.platform_connected = False

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Platform Disconnected',
                        'message': 'You have successfully disconnected the platform.',
                        'type': 'success',
                        'sticky': False,
                        'next': {
                            'type': 'ir.actions.client',
                            'tag': 'reload',
                        }
                    }
                }



        else:
            error_message = f"HTTP Error {response.status_code}: {response.text}"
            
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': ('Platform Disconnection Failed'),
                'message': error_message,
                'type': 'danger',
                'sticky': False,
            }
        }

    def copy_commercium_domain(self):
        # dummy method, button click se kuch nahi hoga
        return True

    def copy_commercium_username(self):
        # dummy method, button click se kuch nahi hoga
        return True

    def copy_commercium_password(self):
        # dummy method, button click se kuch nahi hoga
        return True

    def copy_commercium_db(self):
        # dummy method, button click se kuch nahi hoga
        return True

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        parsed_url = urlparse(url)
        clean_domain = parsed_url.netloc

        # param = self.env['ir.config_parameter'].sudo()
        # api_key = param.get_param('commercium_connector.api_key')

        # if api_key:
        #     param = self.env['ir.config_parameter'].sudo()
        #     api_key = param.set_param('commercium_connector.api_key', '')

        # if not api_key:
        #     api_key = self.env['res.users.apikeys']._generate(name='commercium_service', scope='full_access')
        #     param.set_param('commercium_connector.api_key', api_key)

        

        res.update({
            'commercium_username': self.env.user.login,
            'commercium_db': self._cr.dbname,
            'commercium_domain': clean_domain
        })

        return res

    def action_connect_commercium(self):
        # Optional if you still want to use the connect button
        self.ensure_one()
        # _logger.info(f"Trying to connect with: {self.commercium_username} / {self.commercium_db}")
        print(f"Trying to connect with: {self.commercium_username} / {self.commercium_db}")
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': ('Connection'),
                'message': ('Auto-filled credentials are displayed successfully.'),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_regenerate_api_key(self):
        param = self.env['ir.config_parameter'].sudo()
        api_key = param.get_param('commercium_connector.api_key')

        if not api_key:
            api_key = self.env['res.users.apikeys']._generate(name='commercium_service', scope='some_scope')
            param.set_param('commercium_connector.api_key', api_key)

        # self.commercium_api_key = new_key.key  # update field so it reflects

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'API Key Regenerated',
                'message': 'A new API key has been created.',
                'type': 'success',
                'sticky': False,
            }
        }
