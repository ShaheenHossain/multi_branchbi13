odoo.define('pos_receipt_kitchen.pos', function (require) {
"use strict";

var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');


var _super_order = models.Order.prototype;
models.Order = models.Order.extend({
    export_for_printing: function() {
        var self = this;
        var json = _super_order.export_for_printing.apply(this,arguments);
        var receipt_date_time = this.formatted_validation_date.split(' ')
        json.receipt_date = receipt_date_time[0]
        json.receipt_time = receipt_date_time[1]
        json.dine_option = $('#dine_in_out').val()
        json.order_name = self.name.split(' ')[1]
        return json;
    },
});

screens.ReceiptScreenWidget.include({
    handle_auto_print: function() {
        this._super();
        this.click_next();
    }
});

});