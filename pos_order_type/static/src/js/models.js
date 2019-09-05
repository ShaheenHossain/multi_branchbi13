odoo.define('pos_order_type.models', function (require) {
"use strict";

    var models = require('point_of_sale.models');

    _.each(models.PosModel.prototype.models, function(modelObj) {
        if (modelObj.model === "product.pricelist") {
            modelObj.domain = function(self) { return ['|', ['id', 'in', self.config.available_pricelist_ids], ['has_zero_price', '=', true]]; };
        }
    });

    models.load_fields("res.users", "pos_authorisation_code");
    models.load_fields("product.pricelist", "has_zero_price");

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function() {
            _super_order.initialize.apply(this, arguments);
            this.order_type = this.order_type || "customer";
        },

        set_ordertype: function(type) {
            this.order_type = type;
            this.change_pricelist_on_order_type();
        },

        get_ordertype: function() {
            return this.order_type;
        },

        set_authorised_user: function(user) {
            this.authorised_user = user;
        },

        get_authorised_user: function() {
            return this.authorised_user;
        },

        change_pricelist_on_order_type: function() {
            var self = this;
            var zero_pricelist = _.findWhere(self.pos.pricelists, {'has_zero_price': true});
            if (_.contains(["manager", "staff"], self.order_type) && zero_pricelist) {
                self.set_pricelist(zero_pricelist);
            } else  {
                var order = self.pos.get_order();
                var partner = order && order.get_client();
                if (partner) {
                    self.set_pricelist(_.findWhere(this.pos.pricelists, {'id': partner.property_product_pricelist[0]}) || self.pos.default_pricelist);
                } else {
                    self.set_pricelist(self.pos.default_pricelist);
                }
            }
        },

        init_from_JSON: function(json) {
            _super_order.init_from_JSON.apply(this, arguments);
            this.order_type = json.order_type;
            this.authorised_user = json.authorised_user;
        },

        export_as_JSON: function(){
            var json = _super_order.export_as_JSON.call(this);
            json.order_type = this.get_ordertype();
            json.authorised_user = this.get_authorised_user();
            return json;
        },

    });
});