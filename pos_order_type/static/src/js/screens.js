odoo.define('pos_order_type.screens', function (require) {
"use strict";

var core = require('web.core');
var screens = require('point_of_sale.screens');

var QWeb = core.qweb;
var _t = core._t;

screens.ClientListScreenWidget.include({
    save_changes: function(){
        var self = this;
        self._super();
        var order = self.pos.get_order();
        order.change_pricelist_on_order_type();
    },
});

var set_ordertype_button = screens.ActionButtonWidget.extend({
    template: 'SetOrderTypeButton',
    init: function (parent, options) {
        this._super(parent, options);

        this.pos.get('orders').bind('add remove change', function () {
            this.renderElement();
        }, this);

        this.pos.bind('change:selectedOrder', function () {
            this.renderElement();
        }, this);

        this.types = [{
            label: _("Customer"),
            item: "customer"
        }, {
            label: _("Manager"),
            item: "manager"
        }, {
            label: _("Staff"),
            item: "staff"
        }];
    },

    button_click: function () {
        var self = this;
        self.gui.show_popup('order_type', {
            title: _t('Select Order Type'),
            list: self.types,
            confirm: function (type, user) {
                var order = self.pos.get_order();
                order.set_ordertype(type);
                if (!_.isUndefined(user) && _.isObject(user)) {
                    order.set_authorised_user(user.id);
                }
            },
            is_selected: function (type) {
                return type === self.pos.get_order().get_ordertype();
            }
        });
    },

    get_current_order_type: function () {
        var name = _t('Order Type');
        var order = this.pos.get_order();

        if (order) {
            var order_type = order.get_ordertype();
            if (order_type) {
                name = _.findWhere(this.types, {'item': order_type}).label;
            }
        }

        return name;
    },
});

screens.define_action_button({
    'name': 'set_ordertype',
    'widget': set_ordertype_button,
    'condition': function(){
        return this.pos.config.iface_ordertype;
    },
});

return {
    set_ordertype_button: set_ordertype_button,
};

});
