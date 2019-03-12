// pos_return_order js
odoo.define('bi_pos_multi_ticket.pos', function(require) {
	"use strict";
	var models = require('point_of_sale.models');
	var screens = require('point_of_sale.screens');
	var core = require('web.core');
	var gui = require('point_of_sale.gui');
	var popups = require('point_of_sale.popups');
	//var Model = require('web.DataModel');
	var QWeb = core.qweb;
	var rpc = require('web.rpc');
	var utils = require('web.utils');
	var field_utils = require('web.field_utils');
	var session = require('web.session');
	var _t = core._t;
	var sequence_no;
	var s_no;


	models.load_models({
		model: 'pos.order',
		fields: ['ticket_number'],
		domain: function(self){ return [['session_id', '=', self.pos_session.name],['state', 'not in', ['draft', 'cancel']]]; },
		loaded: function(self, pos_order) {
			self.pos_order = pos_order;
			
		},
	});

	var _super_posmodel = models.PosModel.prototype;
	models.PosModel = models.PosModel.extend({
		initialize: function(session, attributes) {
			var partner_model = _.find(this.models, function(model) {
				return model.model === 'pos.session';
			});
			partner_model.fields.push('serial_no');
			return _super_posmodel.initialize.call(this, session, attributes);

		},
		
	});

	var posorder_super = models.Order.prototype;
	var OrderSuper = models.Order;
	models.Order = models.Order.extend({

		initialize: function(attr,options) {
			posorder_super.initialize.call(this,attr,options);
			this.get_sequence();        
		},
		
		export_for_printing: function(){
	        var orderlines = [];
	        var self = this;

	        this.orderlines.each(function(orderline){
	            orderlines.push(orderline.export_for_printing());
	        });

	        var paymentlines = [];
	        this.paymentlines.each(function(paymentline){
	            paymentlines.push(paymentline.export_for_printing());
	        });
	        var client  = this.get('client');
	        var cashier = this.pos.get_cashier();
	        var company = this.pos.company;
	        var shop    = this.pos.shop;
	        var date    = new Date();

	        function is_xml(subreceipt){
	            return subreceipt ? (subreceipt.split('\n')[0].indexOf('<!DOCTYPE QWEB') >= 0) : false;
	        }

	        function render_xml(subreceipt){
	            if (!is_xml(subreceipt)) {
	                return subreceipt;
	            } else {
	                subreceipt = subreceipt.split('\n').slice(1).join('\n');
	                var qweb = new QWeb2.Engine();
	                    qweb.debug = config.debug;
	                    qweb.default_dict = _.clone(QWeb.default_dict);
	                    qweb.add_template('<templates><t t-name="subreceipt">'+subreceipt+'</t></templates>');

	                return qweb.render('subreceipt',{'pos':self.pos,'widget':self.pos.chrome,'order':self, 'receipt': receipt}) ;
	            }
	        }

	        var receipt = {
	            orderlines: orderlines,
	            paymentlines: paymentlines,
	            subtotal: this.get_subtotal(),
	            total_with_tax: this.get_total_with_tax(),
	            total_without_tax: this.get_total_without_tax(),
	            total_tax: this.get_total_tax(),
	            total_paid: this.get_total_paid(),
	            total_discount: this.get_total_discount(),
	            tax_details: this.get_tax_details(),
	            change: this.get_change(),
	            name : this.get_name(),
	            client: client ? client.name : null ,
	            ticket_number : s_no,
	            invoice_id: null,   //TODO
	            cashier: cashier ? cashier.name : null,
	            precision: {
	                price: 2,
	                money: 2,
	                quantity: 3,
	            },
	            date: {
	                year: date.getFullYear(),
	                month: date.getMonth(),
	                date: date.getDate(),       // day of the month
	                day: date.getDay(),         // day of the week
	                hour: date.getHours(),
	                minute: date.getMinutes() ,
	                isostring: date.toISOString(),
	                localestring: date.toLocaleString(),
	            },
	            company:{
	                email: company.email,
	                website: company.website,
	                company_registry: company.company_registry,
	                contact_address: company.partner_id[1],
	                vat: company.vat,
	                vat_label: company.country && company.country.vat_label || '',
	                name: company.name,
	                phone: company.phone,
	                logo:  this.pos.company_logo_base64,
	            },
	            shop:{
	                name: shop.name,
	            },
	            currency: this.pos.currency,
	        };

	        if (is_xml(this.pos.config.receipt_header)){
	            receipt.header = '';
	            receipt.header_xml = render_xml(this.pos.config.receipt_header);
	        } else {
	            receipt.header = this.pos.config.receipt_header || '';
	        }

	        if (is_xml(this.pos.config.receipt_footer)){
	            receipt.footer = '';
	            receipt.footer_xml = render_xml(this.pos.config.receipt_footer);
	        } else {
	            receipt.footer = this.pos.config.receipt_footer || '';
	        }

	        return receipt;
	    },

		get_sequence: function(){
			var self = this;
			var digits = this.pos.config.digits_serial_no;
			var prefix = this.pos.config.prefix_serial_no;
			var session = this.pos.pos_session;
			var str = this.name
			var name = parseInt(str.substr(str.length - 4));
			var serial_no = name 
			var serial_str = String(serial_no)
			var serial_no_digit=serial_str.length
			var diffrence = Math.abs(serial_no_digit - digits) 
			var no;
			if (diffrence > 0)
			{
				no = "0"
				for(var x =0;x<diffrence-1;x++)
				{
					no = no + "0"
				}
			}	
			else {
					no = ""
			} 
			if(self.pos.config.enable_invoive_prefix == true)
			{
				s_no = prefix+no+serial_str;
			}
			else
			{
				s_no = " "
			}
			
		},

		

		export_as_JSON: function() {
			var self = this;
			var loaded = OrderSuper.prototype.export_as_JSON.call(this);
			loaded.ticket_number = s_no;
			loaded.serial_no = this.get_sequence();

			return loaded;
		},
	});

	screens.PaymentScreenWidget.include({

		finalize_validation: function() {
		var self = this;
		var order = this.pos.get_order();

		if (order.is_paid_with_cash() && this.pos.config.iface_cashdrawer) { 

				this.pos.proxy.open_cashbox();
		}
		// order.get_sequence();
		order.initialize_validation_date();
		order.finalized = true;

		if (order.is_to_invoice()) {
			var invoiced = this.pos.push_and_invoice_order(order);
			this.invoicing = true;

			invoiced.fail(function(error){
				self.invoicing = false;
				order.finalized = false;
				if (error.message === 'Missing Customer') {
					self.gui.show_popup('confirm',{
						'title': _t('Please select the Customer'),
						'body': _t('You need to select the customer before you can invoice an order.'),
						confirm: function(){
							self.gui.show_screen('clientlist');
						},
					});
				} else if (error.message === 'Backend Invoice') {
					self.gui.show_popup('confirm',{
						'title': _t('Please print the invoice from the backend'),
						'body': _t('The order has been synchronized earlier. Please make the invoice from the backend for the order: ') + error.data.order.name,
						confirm: function () {
							this.gui.show_screen('receipt');
						},
						cancel: function () {
							this.gui.show_screen('receipt');
						},
					});
				} else if (error.code < 0) {        // XmlHttpRequest Errors
					self.gui.show_popup('error',{
						'title': _t('The order could not be sent'),
						'body': _t('Check your internet connection and try again.'),
					});
				} else if (error.code === 200) {    // OpenERP Server Errors
					self.gui.show_popup('error-traceback',{
						'title': error.data.message || _t("Server Error"),
						'body': error.data.debug || _t('The server encountered an error while receiving your order.'),
					});
				} else {                            // ???
					self.gui.show_popup('error',{
						'title': _t("Unknown Error"),
						'body':  _t("The order could not be sent to the server due to an unknown error"),
					});
				}
			});

			invoiced.done(function(){
				self.invoicing = false;
				self.gui.show_screen('receipt');
			});
		} else {
			this.pos.push_order(order);
			this.gui.show_screen('receipt');
		}
	},
	   
	})
});
