# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import http, _
from odoo.http import request
from odoo.exceptions import UserError
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.addons.website_sale.controllers.main import WebsiteSale, TableCompute
import logging

_logger = logging.getLogger(__name__)


class AuctionHomepage(http.Controller):

    @http.route('/', website=True, auth='public')
    def auctions(self):
        auctions = request.env['auction'].sudo().search([])
        future_auctions = []
        in_process_auctions = []
        past_auctions = []
        now = datetime.today()
        for auction in auctions:
            start = datetime.strptime(str(auction.start_date), '%Y-%m-%d %H:%M:%S')
            end = datetime.strptime(str(auction.end_date), '%Y-%m-%d %H:%M:%S')
            if now < start:
                future_auctions.append(auction)
            elif now < end:
                in_process_auctions.append(auction)
            else:
                past_auctions.append(auction)

        return request.render('auction_website.auction_homepage', {'future_auctions': future_auctions,
                                                                   'in_process_auctions': in_process_auctions,
                                                                   'past_auctions': past_auctions,
                                                                   'category': request.env['product.public.category'],
                                                                   '_': _})

    @http.route('/past-auctions', website=True, auth='public')
    def past_auctions(self):
        auctions = request.env['auction'].sudo().search([])
        past_auctions_dict = {}
        now = datetime.today()
        for auction in auctions:
            end = datetime.strptime(str(auction.end_date), '%Y-%m-%d %H:%M:%S')
            if now > end:
                if end.year not in past_auctions_dict.keys():
                    past_auctions_dict[end.year] = [auction]
                else:
                    past_auctions_dict[end.year].append(auction)

        return request.render('auction_website.past_auctions', {'past_auctions_dict': past_auctions_dict,
                                                                '_': _})


def get_auctions_domain(search, category):
    if search and category:
        domain = ['&', '&', '|',
                  ('name', 'ilike', search),
                  ('product_public_category_id', 'child_of', category.id),
                  ('description', 'ilike', search),
                  ('product_public_category_id', 'child_of', category.id),
                  ('auction_status_id.title', '=', 'Process')]
    elif search:
        domain = ['&', '|',
                  ('name', 'ilike', search),
                  ('description', 'ilike', search),
                  ('auction_status_id.title', '=', 'Process')]
    elif category:
        domain = [('product_public_category_id', 'child_of', category.id),
                  ('auction_status_id.title', '=', 'Process')]
    else:
        domain = [('auction_status_id.title', '=', 'Process')]

    return domain


class WebsiteAuctionSale(WebsiteSale):

    def sitemap_shop(env, rule, qs):
        if not qs or qs.lower() in '/auctions':
            yield {'loc': '/auctions'}

        Category = env['product.public.category']
        dom = sitemap_qs2dom(qs, '/auctions/category', Category._rec_name)
        dom += env['website'].get_current_website().website_domain()
        for cat in Category.search(dom):
            loc = '/auctions/category/%s' % slug(cat)
            if not qs or qs.lower() in loc:
                yield {'loc': loc}

    @http.route([
        '''/auctions''',
        '''/auctions/page/<int:page>''',
        '''/auctions/category/<model("product.public.category"):category>''',
        '''/auctions/category/<model("product.public.category"):category>/page/<int:page>'''
    ], type='http', auth="public", website=True, sitemap=sitemap_shop)
    def auctions_shop(self, page=0, category=None, search='', ppg=False, **post):
        add_qty = int(post.get('add_qty', 1))
        Category = request.env['product.public.category']
        if category:
            category = Category.search([('id', '=', int(category))], limit=1)
            if not category or not category.can_access_from_current_website():
                raise NotFound()
        else:
            category = Category

        if ppg:
            try:
                ppg = int(ppg)
                post['ppg'] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            ppg = request.env['website'].get_current_website().shop_ppg or 20

        ppr = request.env['website'].get_current_website().shop_ppr or 4

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}

        domain = self._get_search_domain(search, category, attrib_values)
        auction_domain = get_auctions_domain(search, category)

        keep = QueryURL('/auctions', category=category and int(category), search=search, attrib=attrib_list,
                        order=post.get('order'))

        pricelist_context, pricelist = self._get_pricelist_context()

        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

        url = "/auctions"
        is_search = False
        if search:
            is_search = True
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list
        Product = request.env['product.template'].with_context(bin_size=True)
        Auction = request.env['auction'].with_context(bin_size=True)
        domain.append(['is_published', '=', True])
        search_product = Product.search(domain, order=self._get_search_order(post))
        auctions = Auction.search(auction_domain)

        website_domain = request.website.website_domain()
        categs_domain = [('parent_id', '=', False)] + website_domain

        if search:
            search_categories = Category.search(
                [('product_tmpl_ids', 'in', search_product.ids)] + website_domain).parents_and_self
            categs_domain.append(('id', 'in', search_categories.ids))
        else:
            search_categories = Category
        categs = Category.search(categs_domain)

        if category:
            url = "/auctions/category/%s" % slug(category)
        product_count = len(search_product)
        auctions_count = len(auctions)
        pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        pager_auctions = request.website.pager(url=url, total=auctions_count, page=page, step=ppg, scope=7,
                                               url_args=post)
        offset = pager['offset']
        offset_auctions = pager_auctions['offset']
        products = search_product[offset: offset + ppg]
        auctions = auctions[offset_auctions: offset_auctions + ppg]

        ProductAttribute = request.env['product.attribute']
        if products:
            # get all products without limit
            attributes = ProductAttribute.search([('product_tmpl_ids', 'in', search_product.ids)])
        else:
            attributes = ProductAttribute.browse(attributes_ids)

        layout_mode = request.session.get('website_sale_shop_layout_mode')
        if not layout_mode:
            if request.website.viewref('website_sale.products_list_view').active:
                layout_mode = 'list'
            else:
                layout_mode = 'grid'
        future_products = []
        in_process_products = []
        past_products = []
        now = datetime.today()
        for product in products:
            try:
                start = datetime.strptime(str(product.auction_id.start_date), '%Y-%m-%d %H:%M:%S')
                end = datetime.strptime(str(product.auction_id.end_date), '%Y-%m-%d %H:%M:%S')
                if now < start:
                    future_products.append(product)
                elif now < end:
                    in_process_products.append(product)
                else:
                    past_products.append(product)
            except:
                pass
        future_auctions = []
        in_process_auctions = []
        past_auctions = []
        for auction in auctions:
            start = datetime.strptime(str(auction.start_date), '%Y-%m-%d %H:%M:%S')
            end = datetime.strptime(str(auction.end_date), '%Y-%m-%d %H:%M:%S')
            if now < start:
                future_auctions.append(auction)
            elif now < end:
                in_process_auctions.append(auction)
            else:
                past_auctions.append(auction)
        requested_url = request.httprequest.url
        if 'search' in requested_url:
            is_search = True
            if 'search' not in pager['page_next']['url']:
                for page in pager['pages']:
                    page['url'] += '&search='
                pager['page_next']['url'] += '&search='
                pager['page_previous']['url'] += '&search='
        values = {
            'search': search,
            'is_search': is_search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pager_auctions': pager_auctions,
            'pricelist': pricelist,
            'add_qty': add_qty,
            'products': products,
            'past_products': past_products,
            'in_process_products': in_process_products,
            'future_products': future_products,
            'auctions': auctions,
            'future_auctions': future_auctions,
            'in_process_auctions': in_process_auctions,
            'past_auctions': past_auctions,
            'search_count': product_count,  # common for all searchbox
            'bins': TableCompute().process(products, ppg, ppr),
            'ppg': ppg,
            'ppr': ppr,
            'categories': categs,
            'attributes': attributes,
            'keep': keep,
            'search_categories_ids': search_categories.ids,
            'layout_mode': layout_mode,
            '_': _,
        }

        if category:
            values['main_object'] = category
        return request.render("auction_website.auctions", values)

    @http.route(['/shop/<model("product.template"):product>'], type='http', auth="public", website=True, sitemap=True)
    def product(self, product, category='', search='', **kwargs):
        if not product.can_access_from_current_website():
            raise NotFound()
        values = self._prepare_product_values(product, category, search, **kwargs)
        values['_'] = _
        return request.render("website_sale.product", values)

    @http.route([
        '''/<model("auction"):auction>/lots''',
        '''/auctions/<model("auction"):auction>/lots''',
        '''/auctions/category/<model("auction"):auction>/lots''',
        '''/auctions/category/<model("product.public.category"):category>/page/<int:page>/<model("auction"):auction>/lots'''
    ], type='http', auth="public", website=True)
    def lots(self, page=0, category=None, auction=None):
        Auction = request.env['auction']
        if auction:
            auction = Auction.search([('id', '=', int(auction))], limit=1)
            lots = request.env['product.template'].search(
                [('auction_id', '=', auction.id), ('is_published', '=', True)])
        else:
            auction = False
            lots = []
        now = datetime.today()
        start = datetime.strptime(str(auction.start_date), '%Y-%m-%d %H:%M:%S')
        end = datetime.strptime(str(auction.end_date), '%Y-%m-%d %H:%M:%S')
        in_process = False
        if (now > start) and (now < end):
            in_process = True
        values = {'auction': auction,
                  'lots': lots,
                  'in_process': in_process,
                  '_': _}
        return request.render("auction_website.lots", values)

    @http.route(['/auctions/<model("auction"):auction>/lots/<model("product.template"):product>'], type='http',
                auth="public", website=True, sitemap=True)
    def lot(self, product, category='', search='', **kwargs):
        values = self._prepare_product_values(product, category, search, **kwargs)
        values['_'] = _
        return request.render("auction_website.lot", values)

    @http.route([
        '''/shop''',
        '''/shop/page/<int:page>''',
        '''/shop/category/<model("product.public.category"):category>''',
        '''/shop/category/<model("product.public.category"):category>/page/<int:page>'''
    ], type='http', auth="public", website=True, sitemap=sitemap_shop)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        add_qty = int(post.get('add_qty', 1))
        Category = request.env['product.public.category']
        if category:
            category = Category.search([('id', '=', int(category))], limit=1)
            if not category or not category.can_access_from_current_website():
                raise NotFound()
        else:
            category = Category

        if ppg:
            try:
                ppg = int(ppg)
                post['ppg'] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            ppg = request.env['website'].get_current_website().shop_ppg or 20

        ppr = request.env['website'].get_current_website().shop_ppr or 4

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}

        domain = self._get_search_domain(search, category, attrib_values)

        keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list,
                        order=post.get('order'))

        pricelist_context, pricelist = self._get_pricelist_context()

        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

        url = "/shop"
        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list

        Product = request.env['product.template'].with_context(bin_size=True)
        if not search:
            domain.append(['auction_id', '=', False])
        search_product = Product.search(domain, order=self._get_search_order(post))

        website_domain = request.website.website_domain()
        categs_domain = [('parent_id', '=', False)] + website_domain
        if search:
            search_categories = Category.search(
                [('product_tmpl_ids', 'in', search_product.ids)] + website_domain).parents_and_self
            categs_domain.append(('id', 'in', search_categories.ids))
        else:
            search_categories = Category
        categs = Category.search(categs_domain)

        if category:
            url = "/shop/category/%s" % slug(category)

        product_count = len(search_product)
        pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        offset = pager['offset']
        products = search_product[offset: offset + ppg]

        ProductAttribute = request.env['product.attribute']
        if products:
            # get all products without limit
            attributes = ProductAttribute.search([('product_tmpl_ids', 'in', search_product.ids)])
        else:
            attributes = ProductAttribute.browse(attributes_ids)

        layout_mode = request.session.get('website_sale_shop_layout_mode')
        if not layout_mode:
            if request.website.viewref('website_sale.products_list_view').active:
                layout_mode = 'list'
            else:
                layout_mode = 'grid'

        values = {
            'search': search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'add_qty': add_qty,
            'products': products,
            'search_count': product_count,  # common for all searchbox
            'bins': TableCompute().process(products, ppg, ppr),
            'ppg': ppg,
            'ppr': ppr,
            'categories': categs,
            'attributes': attributes,
            'keep': keep,
            'search_categories_ids': search_categories.ids,
            'layout_mode': layout_mode,
            '_': _,
        }
        if category:
            values['main_object'] = category
        return request.render("website_sale.products", values)

    # @http.route('/shop/products/autocomplete', type='json', auth='public', website=True)
    # def products_autocomplete(self, term, options={}, **kwargs):
    #    return False


class AuctionWebsiteSignup(AuthSignupHome):

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()
        qcontext['countries'] = request.env['res.country'].sudo().search([])
        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                self.do_signup(qcontext)
                # Send an account creation confirmation email
                if qcontext.get('token'):
                    User = request.env['res.users']
                    user_sudo = User.sudo().search(
                        User._get_login_domain(qcontext.get('login')), order=User._get_login_order(), limit=1
                    )
                    template = request.env.ref('auth_signup.mail_template_user_signup_account_created',
                                               raise_if_not_found=False)
                    if user_sudo and template:
                        template.sudo().send_mail(user_sudo.id, force_send=True)
                return self.web_login(*args, **kw)
            except UserError as e:
                qcontext['error'] = e.args[0]
            except (SignupError, AssertionError) as e:
                if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                    qcontext["error"] = _("Another user is already registered using this email address.")
                else:
                    _logger.error("%s", e)
                    qcontext['error'] = _("Could not create a new account.")

        response = request.render('auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        values = {key: qcontext.get(key) for key in (
            'login', 'name', 'password', 'lastname', 'country', 'address', 'mobile_number',
            'business_name', 'identity_document', 'national_id_number', 'newsletter')}
        values['name'] = values['name'] + ' ' + values['lastname']
        if values['newsletter'] == 'on':
            values['newsletter'] = True
        else:
            values['newsletter'] = False
        del values['lastname']
        country_id = request.env['res.country'].sudo().search([('name', '=', values['country'])])
        values['country_id'] = country_id.id
        del values['country']
        if not values:
            raise UserError(_("The form was not properly filled in."))
        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords do not match; please retype them."))
        supported_lang_codes = [code for code, _ in request.env['res.lang'].get_installed()]
        lang = request.context.get('lang', '').split('_')[0]
        if lang in supported_lang_codes:
            values['lang'] = lang
        self._signup_with_values(qcontext.get('token'), values)
        request.env.cr.commit()
