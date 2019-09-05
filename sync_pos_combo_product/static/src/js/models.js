odoo.define('pos_product_combo.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');

    models.load_fields("product.product", ["is_combo", "pos_notes"]);

    models.load_models({
        model: 'pos.product_notes',
        fields: ['name', 'sequence', 'pos_category_ids'],
        condition: function(self) {
            // load all notes for the restaurant only (because of the Note button available in the restaurant only)
            return self.config.module_pos_restaurant;
        },
        loaded: function(self,product_notes){
            var sorting_product_notes = function(idOne, idTwo){
                return idOne.sequence - idTwo.sequence;
            };
            if (product_notes) {
                self.product_notes = product_notes.sort(sorting_product_notes);
            }
        },
    });

    models.load_models({
        model: 'product.combo',
        fields: ['product_template_id', 'is_required_product', 'is_include_in_main_product_price', 'category_id', 'product_ids', 'no_of_items'],
        loaded: function (self, combo) {
            self.combo = combo;
            self.combo_products_by_id = {};
            for (var i = 0; i < combo.length; i++) {
                self.combo_products_by_id[combo[i].id] = combo[i];
            }
        },
    });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function () {
            _super_order.initialize.apply(this, arguments);
            this.combo_products_by_id = this.combo_products_by_id || {};
            this.product_info = this.product_info || {};
        },
        set_combo: function (combo_products_by_id) {
            this.combo_products_by_id = combo_products_by_id;
        },
        get_combo: function () {
            return this.pos.combo_products_by_id;
        },
        set_valid_product: function(product_info) {
            this.product_info = product_info;
        },
        get_valid_product: function() {
            return this.product_info;
        },
        set_pricelist: function (pricelist) {
            var self = this;
            this.pricelist = pricelist;

            var lines_to_recompute = _.filter(this.get_orderlines(), function (line) {4
                if (line.is_combo_line === true) {
                    return ! line.price_manually_set || line.is_combo_line;
                }
                return ! line.price_manually_set;
            });
            _.each(lines_to_recompute, function (line) {
                if (line && line.is_combo_line) {
                    var combo_price = line.get_combo_price()
                    line.set_unit_price(combo_price)
                } else {
                    line.set_unit_price(line.product.get_price(self.pricelist, line.get_quantity()));
                    self.fix_tax_included_price(line);
                }
            });
            this.trigger('change');
        },
        set_note: function(note){
            this.old_note = this.note;
            this.note = note;
            this.trigger('change',this);
            this.trigger('new_updates_to_send');
            this.pos.gui.screen_instances.products.order_widget.renderElement(true);
        },
        get_note: function(){
            if (this.note) {
                return this.note;
            }
            return false;
        },
        set_custom_notes: function(notes) {
            this.old_custom_notes = this.custom_notes;
            this.custom_notes = notes;
            this.trigger('new_updates_to_send');
            this.trigger('change', this);
        },
        set_old_custom_notes: function(notes) {
            this.old_custom_notes = notes;
            this.trigger('new_updates_to_send');
            this.trigger('change', this);
        },
        get_custom_notes: function() {
            if (this.custom_notes && this.custom_notes.length) {
                return this.custom_notes;
            }
            return false;
        },
        get_line_resume: function(line) {
            var res = _super_order.get_line_resume.apply(this, arguments);
            res.custom_notes = line.get_custom_notes() || false;
            res.old_custom_notes = line.old_custom_notes || false;
            return res;
        },
        export_as_JSON: function() {
            var data = _super_order.export_as_JSON.apply(this, arguments);
            data.note = this.note;
            data.old_note = this.old_note;
            data.custom_notes = this.custom_notes;
            data.old_custom_notes = this.old_custom_notes;
            return data;
        },
        init_from_JSON: function(json) {
            this.note = json.note;
            this.old_note = json.old_note;
            this.custom_notes = json.custom_notes;
            this.old_custom_notes = json.old_custom_notes;
            _super_order.init_from_JSON.call(this, json);
        },
        saveChanges: function(){
            this.old_note = this.get_note();
            this.old_custom_notes = this.get_custom_notes();
            _super_order.saveChanges.call(this, arguments);
        },
    });

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function(attr, options) {
            _super_orderline.initialize.call(this,attr,options);
            this.unreq_product = this.unreq_product || [];
            this.apply_unreq_product = this.apply_unreq_product || [];
            this.req_product = this.req_product || [];
            this.pos.combo_products_by_id = this.pos.combo_products_by_id || {};
            this.qty = this.get_quantity();
            this.unit_price = this.get_unit_price();
            this.is_combo_line = this.is_combo_line || false;
            if (this.product.pos_notes && !this.note) {
                this.set_note(this.product.pos_notes);
            }
        },

        set_unrequire_product: function(unreq_product) {
            this.unreq_product = unreq_product;
            this.is_combo_line = true;
        },
        get_unrequire_product: function() {
            return this.unreq_product;
        },
        get_applied_unreq_product: function() {
            var unreq_product_ids = [];
            _.each(this.unreq_product, function(product_id) {
                unreq_product_ids.push(product_id.id);
            });
            return unreq_product_ids;
        },
        get_combo_price: function() {
            var self = this;
            var list_product_price = [];

            if (this.is_combo_line) {
                _.each(this.unreq_product, function(unreq_product_price) {
                    list_product_price.push(unreq_product_price.get_price(self.order.pricelist, self.get_quantity()));
                });
                var combo = _.find(this.pos.combo_products_by_id, function(combo_id) {
                    _.each(self.req_product, function(req_product_price) {
                        if (combo_id && combo_id.is_required_product && !combo_id.is_include_in_main_product_price && req_product_price && _.contains(combo_id.product_ids, req_product_price.id)) {
                            list_product_price.push(req_product_price.get_price(self.order.pricelist, self.get_quantity()));
                        }
                    });
                });
                var combo_price = _.reduce(list_product_price, function(price, number) {
                    return price + number;
                }, 0);
                var total_price = this.qty * combo_price;
                var product_price = this.product.get_price(self.order.pricelist, self.get_quantity())
                var final_price = product_price * this.qty + total_price;
                return final_price;
            }
        },
        set_require_product: function(req_product) {
            this.req_product = req_product;
            this.is_combo_line = true;
        },
        get_require_product: function() {
            return this.req_product;
        },
        get_applied_req_product: function() {
            var req_product_ids = [];
            _.each(this.req_product, function(product_id) {
                req_product_ids.push(product_id.id);
            });
            return req_product_ids;
        },
        set_custom_notes: function(notes) {
            this.custom_notes = notes;
            this.trigger('change', this);
            this.order.trigger('new_updates_to_send');
        },
        get_custom_notes: function() {
            if (this.custom_notes && this.custom_notes.length) {
                return this.custom_notes;
            }
            return false;
        },
        set_old_custom_notes: function(notes) {
            this.old_custom_notes = notes;
            this.trigger('change', this);
            this.order.trigger('new_updates_to_send');
        },
        can_be_merged_with: function(orderline){
            var res = _super_orderline.can_be_merged_with.call(this, orderline);
            if (orderline.get_require_product() !== this.get_require_product()) {
                return false;
            }else if (orderline.get_unrequire_product() !== this.get_unrequire_product()) {
                return false;
            }
            if (this.get_note() || this.get_custom_notes() || orderline.get_note()) {
                return false;
            }
            return res;
        },
        get_line_diff_hash: function() {
            var custom_notes_ids = [];
            var custom_notes_ids_line = false;
            var res = _super_orderline.get_line_diff_hash.apply(this,arguments);
            if (this.get_custom_notes()) {
                _.each(this.get_custom_notes(), function(custom_notes) {
                    custom_notes_ids.push(custom_notes.id);
                });
                custom_notes_ids_line = custom_notes_ids.join('');
            }
            var id = this.uid || this.id;
            if (this.get_note()) {
                if(this.get_custom_notes()) {
                    return res + '|' + custom_notes_ids_line;
                }
                return res;
            }
            if(this.get_custom_notes()) {
               return id + '|' + custom_notes_ids_line;
            }
            return res;
        },
        clone: function(){
            var orderline = _super_orderline.clone.call(this);
            orderline.custom_notes = this.custom_notes;
            return orderline;
        },
        init_from_JSON: function (json) {
            this.custom_notes = json.custom_notes;
            this.old_custom_notes = json.old_custom_notes;
            _super_orderline.init_from_JSON.apply(this, arguments);
            var self = this;
            var unreq_ids = [];
            var req_ids = [];
            _.each(json.unreq_product_ids, function(product_id) {
                var unreq_product = self.pos.db.get_product_by_id(Number(product_id));
                unreq_ids.push(unreq_product)
            });
            _.each(json.req_product_ids, function(product_id) {
                var req_product = self.pos.db.get_product_by_id(Number(product_id));
                req_ids.push(req_product)
            });
            this.unreq_product = unreq_ids;
            this.is_combo_line = json.is_combo_line;
            this.req_product = req_ids;
            this.price_manually_set = json.is_combo_line && true || false;
        },
        export_as_JSON: function() {
            var json = _super_orderline.export_as_JSON.apply(this, arguments);
            json.unreq_product_ids = this.get_applied_unreq_product();
            json.req_product_ids = this.get_applied_req_product();
            json.is_combo_line = this.is_combo_line;
            json.custom_notes = this.custom_notes;
            json.old_custom_notes = this.old_custom_notes;
            return json;
        },
    });

});
