# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from collections import OrderedDict
from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
# from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.osv import expression
import werkzeug
from datetime import datetime, date
from odoo.tools import groupby as groupbyelem
from operator import itemgetter
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo.osv.expression import OR


class CustomerPortal(CustomerPortal):

    # def _prepare_home_portal_values(self, counters):
    #     values = super()._prepare_home_portal_values(counters)
    #     partner = request.env.user.partner_id
    #     stock_scrap = request.env['stock.scrap']
    #     scrap_count = stock_scrap.search_count([
    #         ('partner_id', '=',request.env.user.partner_id.id)
    #     ])
    #     values.update({
    #         'scrap_count': scrap_count,
    #     })
    #     return values
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
   	 
        if 'scrap_count' in counters:
            scrap_obj = request.env['stock.scrap'].sudo()
            scrap_count = scrap_obj.search_count([
               	('partner_id', '=',request.env.user.partner_id.id),      	 
        	])
            values['scrap_count'] = scrap_count
        return values

    
    
    @http.route(['/my/scrap', '/my/scrap/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_scrap(self, page=1, date_begin=None, date_end=None, sortby=None,filterby=None,groupby='none',search=None,search_in='content', **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        stock_scrap = request.env['stock.scrap']
        domain = [
             ('partner_id', '=',request.env.user.partner_id.id)
        ]

        searchbar_sortings = {
            'name': {'label': _('Name'), 'order': 'name asc'},
	'product_id': {'label': _('Product'), 'order': 'product_id asc'},
        }

        # default sortby order
        if not sortby:
            sortby = 'name'

        sort_order = searchbar_sortings[sortby]['order']
		
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('All')},
            'product_id': {'input': 'product_id', 'label': _('Product')},
        }
		

        today = fields.Date.today()
        this_week_end_date = fields.Date.to_string(fields.Date.from_string(today) + timedelta(days=7))
        week_ago = datetime.today() - timedelta(days=7)
        month_ago = (datetime.today() - relativedelta(months=1)).strftime('%Y-%m-%d %H:%M:%S')
        starting_of_year = datetime.now().date().replace(month=1, day=1)    
        ending_of_year = datetime.now().date().replace(month=12, day=31)

        def sd(date):
        	return fields.Datetime.to_string(date)
        def previous_week_range(date):
        	start_date = date + timedelta(-date.weekday(), weeks=-1)
        	end_date = date + timedelta(-date.weekday() - 1)
        	return {'start_date':start_date.strftime('%Y-%m-%d %H:%M:%S'), 'end_date':end_date.strftime('%Y-%m-%d %H:%M:%S')}
		
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'today': {'label': _('Today'), 'domain': [('scrap_date', '>=', datetime.strftime(date.today(),'%Y-%m-%d 00:00:00')),('scrap_date', '<=', datetime.strftime(date.today(),'%Y-%m-%d 23:59:59'))]},
            'yesterday':{'label': _('Yesterday'), 'domain': [('scrap_date', '>=', datetime.strftime(date.today() - timedelta(days=1),'%Y-%m-%d 00:00:00')),('scrap_date', '<=', datetime.strftime(date.today(),'%Y-%m-%d 23:59:59'))]},
            'week': {'label': _('This Week'),
                     'domain': [('scrap_date', '>=', sd(datetime.today() + relativedelta(days=-today.weekday()))), ('scrap_date', '<=', this_week_end_date)]},
            'last_seven_days':{'label':_('Last 7 Days'),
                         'domain': [('scrap_date', '>=', sd(week_ago)), ('scrap_date', '<=', sd(datetime.today()))]},
            'last_week':{'label':_('Last Week'),
                         'domain': [('scrap_date', '>=', previous_week_range(datetime.today()).get('start_date')), ('scrap_date', '<=', previous_week_range(datetime.today()).get('end_date'))]},
            
            'last_month':{'label':_('Last 30 Days'),
                         'domain': [('scrap_date', '>=', month_ago), ('scrap_date', '<=', sd(datetime.today()))]},
            'month':{'label': _('This Month'),
                    'domain': [
                       ("scrap_date", ">=", sd(today.replace(day=1))),
                       ("scrap_date", "<", (today.replace(day=1) + relativedelta(months=1)).strftime('%Y-%m-%d 00:00:00'))
                    ]
                },
            'year':{'label': _('This Year'),
                    'domain': [
                       ("scrap_date", ">=", sd(starting_of_year)),
                       ("scrap_date", "<=", sd(ending_of_year)),
                    ]
                }
        }

		
        if not filterby:
        	filterby = 'all'
        domain += searchbar_filters[filterby]['domain'] 

        
        # count for pager
        scrap_count = stock_scrap.search_count(domain)

        searchbar_inputs = {
            'name': {'input': 'name', 'label': _('Search in Name')},
            'product': {'input': 'product', 'label': _('Search in Product')},
			'source_location': {'input': 'source_location', 'label': _('Search in Source Location')},
			'scrap_location_id': {'input': 'scrap_location_id', 'label': _('Search in Scrap Location')},
			'state': {'input': 'state', 'label': _('Search in State')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }

		# search
        # if search and search_in:
        # 	search_domain = []
        	
#        	if search_in in ('name', 'all'):
#        		search_domain = OR([search_domain, ['|', ('name', 'ilike', search)]])
        	# if search_in in ('product', 'all'):
        		
        	# 	search_domain = OR([search_domain, [('product_id', 'ilike', search)]])
        	# if search_in in ('source_location', 'all'):
        	# 	search_domain = OR([search_domain, [('location_id', 'ilike', search)]])
        	# if search_in in ('scrap_location_id', 'all'):
        	    
        	#     search_domain = OR([search_domain, [('scrap_location_id', 'ilike', search)]])
        	# if search_in in ('state', 'all'):
        	# 	search_domain = OR([search_domain, [('state', 'ilike', search)]])
        	# domain += search_domain
        if search and search_in:
            search_domain = []
            if search_in in ('name'):
                search_domain =   [('name', 'ilike', search)] 
            if search_in in ('product_id'):
                search_domain =   [('product_id', 'ilike', search)]  
            if search_in in ('location_id'):
                search_domain = [('location_id', 'ilike', search)]
            if search_in in ('scrap_location_id'):
                search_domain = [('scrap_location_id', 'ilike', search)]
            if search_in in ('state'):
                search_domain = [('state', 'ilike', search)]
            if search_in in ('all'):
                search_domain = ['|','|','|','|',('name', 'ilike', search),('product_id', 'ilike', search),('location_id', 'ilike', search),
                                ('scrap_location_id', 'ilike', search),('state', 'ilike', search)]    
            domain += search_domain
            
        # make pager
        pager = portal_pager(
            url="/my/scrap",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby,'search_in': search_in,'search': search},
            total=scrap_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        scrap = stock_scrap.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_contact_history'] = scrap.ids[:100] 

        if groupby == 'product_id':
        	grouped_scrap = [request.env['stock.scrap'].concat(*g) for k, g in groupbyelem(scrap, itemgetter('product_id'))]
        else:
        	grouped_scrap = [scrap]		

        values.update({
            'date': date_begin,
            'scrap': scrap.sudo(),
            'page_name': 'scrap',
            'pager': pager,
            'default_url': '/my/scrap',
            'sortby': sortby,
			'grouped_scrap': grouped_scrap,
			'filterby': filterby,
			'groupby': groupby,
			'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
			'searchbar_sortings': searchbar_sortings,
			'searchbar_groupby':searchbar_groupby,
			'searchbar_inputs': searchbar_inputs,
			'search_in': search_in,
			'search': search,
			

	
        })
        return request.render("dev_scrap_order_portal.portal_my_scrap", values)
##    
    @http.route(['/my/scrap/<int:order_id>'], type='http', auth="public", website=True)
    def portal_scrap_page(self, order_id, report_type=None, access_token=None, message=False, download=False, **kw):
        try:
            stock_scrap_sudo = self._document_check_access('stock.scrap', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        now = fields.Date.today()
        if report_type in ('html', 'pdf', 'text'):
        	return self._show_report(model=stock_scrap_sudo, report_type=report_type, report_ref='dev_scrap_report.menu_web_scrap_print', download=download)
        if stock_scrap_sudo and request.session.get('view_scrap_%s' % stock_scrap_sudo.id) != now and request.env.user.share and access_token:
            request.session['view_rma_%s' % stock_scrap_sudo.id] = now
            body = _('Leave viewed by customer')
            stock_scrap_sudo.message_post(res_model='stock.scrap', res_id=stock_scrap_sudo.id, message=body, token=stock_scrap_sudo.access_token, message_type='notification', subtype="mail.mt_note", partner_ids=stock_scrap_sudo.user_id.sudo().partner_id.ids)
        values = {
            'scrap': stock_scrap_sudo,
            'message': message,
            'token': access_token,
            'bootstrap_formatting': True,
            'report_type': 'html',
			'scrap_name':stock_scrap_sudo.name,
			
		
        }
        if stock_scrap_sudo.company_id:
            values['res_company'] = stock_scrap_sudo.company_id
        if stock_scrap_sudo.name:
            history = request.session.get('my_contact_history', [])
        values.update(get_records_pager(history, stock_scrap_sudo))
        return request.render('dev_scrap_order_portal.scrap_portal_template', values)







    # RMA
