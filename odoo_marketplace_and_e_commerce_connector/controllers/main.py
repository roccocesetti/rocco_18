from odoo import http
from odoo.http import request
import json

class PlatformConnectionController(http.Controller):


    @http.route('/api/platform_connection', type='http', auth='public', methods=['GET'], csrf=False)
    def platform_connection(self, **kwargs):
        try:
            response_data = False
            platform_id = request.params.get('platform_id')
            platform_connected = request.params.get('platform_connected')
            if platform_id is None or platform_connected is None:
                response_data = {'success': False, 'error': 'platform_id or platform_connected missing'}

            if not response_data:

                company = request.env['res.company'].sudo().search([], limit=1)
                if not company:
                    # Agar system me koi company hai hi nahi toh error bhej do
                    response_data = {'success': False, 'error': 'No company found in system'}
                
                if not response_data:


                    param = request.env['ir.config_parameter'].sudo()
                    
                    # Convert to boolean safely
                    platform_connected_bool = str(platform_connected).lower() in ['1', 'true', 'yes']

                    # Save values in ir.config_parameter
                    param.set_param('platform_id', platform_id)
                    param.set_param('platform_connected', str(platform_connected_bool))

                    # Prepare response from stored values
                    response_data = {
                        'success': True,
                        'platform_id': param.get_param('platform_id'),
                        'platform_connected': param.get_param('platform_connected') == 'True'
                    }

                    print("response_data : ", response_data)

            # Return JSON response properly
            return request.make_response(
                json.dumps(response_data),
                headers=[('Content-Type', 'application/json')]
            )
        
        except Exception as e:
            return request.make_response(
                json.dumps({"success": "False", "message": str(e)}),
                headers=[('Content-Type', 'application/json')],
                status=500
            )

    
    @http.route('/api/test_ping', type='http', auth='public', methods=['GET'], csrf=False)
    def test_ping(self, **kw):
        # Query parameters ko get karne ke liye:
        platform_id = request.params.get('platform_id')
        # ya
        # platform_id = request.httprequest.args.get('platform_id')

        return f"ping - {platform_id}"
