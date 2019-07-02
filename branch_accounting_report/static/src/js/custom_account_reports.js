odoo.define('branch_accounting_report.account_report_generic', function (require) {
'use strict';

var core = require('web.core');
var Widget = require('web.Widget');
var ControlPanelMixin = require('web.ControlPanelMixin');
var Dialog = require('web.Dialog');
var framework = require('web.framework');
var crash_manager = require('web.crash_manager');
var ActionManager = require('web.ActionManager');
var datepicker = require('web.datepicker');
var session = require('web.session');
var field_utils = require('web.field_utils');

var account_report_generic = require('account_reports.account_report');

var QWeb = core.qweb;
var _t = core._t;

    account_report_generic.include({



        render_searchview_buttons: function() {
            var self = this;
            self._super();
            // this._super();
            
            // branch filter
            this.$searchview_buttons.find('.js_branch_auto_complete').select2();
            self.$searchview_buttons.find('[data-filter="branch"]').select2("val", self.report_options.branch);
            //self.$searchview_buttons.find('[data-filter="analytic_tags"]').select2("val", self.report_options.analytic_tags);

            this.$searchview_buttons.find('.js_branch_auto_complete').on('change', function(){
                self.report_options.branch = self.$searchview_buttons.find('[data-filter="branch"]').val();
                //self.report_options.analytic_tags = self.$searchview_buttons.find('[data-filter="analytic_tags"]').val();
                return self.reload().then(function(){
                    self.$searchview_buttons.find('.account_branch_filter').click();
                })
            });
            // self._super();
        },




    });


});
