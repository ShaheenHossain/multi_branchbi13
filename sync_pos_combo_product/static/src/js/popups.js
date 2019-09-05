odoo.define('pos_product_combo.popups', function (require) {
"use strict";

    var core = require('web.core');
    var gui = require('point_of_sale.gui');
    var PopupWidget = require('point_of_sale.popups');
    var PosBaseWidget = require('point_of_sale.BaseWidget');

    var _t = core._t;

    PosBaseWidget.include({
        init:function(parent,options){
            var self = this;
            this._super(parent,options);
            if (this.gui && this.gui.screen_instances.products && this.gui.screen_instances.products.action_buttons.orderline_note) {

                this.gui.screen_instances.products.action_buttons.orderline_note.button_click = function() {
                    var order = this.pos.get_order();
                    var line = order.get_selected_orderline();
                    var title = '';
                    var value = '';
                    if (order.note_type === "Order") {
                        title = (_t)('Add Note for Order');
                        value = order.get_note();
                    } else if (line) {
                        order.note_type = "Product";
                        title = _t('Add Note for Product');
                        value = line.get_note();
                    }
                    if (line) {
                        var old_line_custom_notes = false;
                        if (line.get_custom_notes()) {
                            old_line_custom_notes = line.get_custom_notes().concat();
                            line.set_old_custom_notes(old_line_custom_notes);
                        }
                        this.gui.show_popup('product_notes',{
                            title: title,
                            value: value,
                            custom_order_ids: order.get_custom_notes(),
                            custom_product_ids: line.get_custom_notes(),
                            confirm: function(res) {
                                if (order.note_type === "Order") {
                                    order.set_custom_notes(res.custom_order_ids);
                                    order.set_note(res.note);
                                }
                                if (order.note_type === "Product") {
                                    line.set_custom_notes(res.custom_product_ids);
                                    line.set_note(res.note);
                                }
                            },
                        });
                    }
                };
            }
        }
    });

    var ComboApplyPopup = PopupWidget.extend({
        template: 'ComboApplyPopup',
        events: _.extend({}, PopupWidget.prototype.events, {
            'click .selection-item': 'click_confirm',
        }),
        show: function(options) {
            options = options || {};
            var self = this;
            this._super(options);
            this.product = options.product || '';
            this.product_price = options.product ? options.product.get_price(options.pricelists, 1): 0.0;
            var product_list = [];
            var select_items = {};
            this.after_edit_combo = [];
            this.renderElement();
            this.product_info = options.product_info || [];
            this.require_product_info = options.require_product_info || [];
            this.unrequire_product_info = options.unrequire_product_info || [];
            this.selected_unreq_product = options.selected_unreq_product || [];
            this.selected_req_product = options.selected_req_product || [];
            if(!_.isUndefined(self.edit_product)) {
                if (!_.isUndefined(this.product.id)) {
                    while(self.edit_product.length > 0) {
                        self.edit_product.pop();
                    }
                }
            }
            _.each(this.selected_req_product, function(selected_id) {
                $('#' + selected_id.id).prop("checked", true);
                $('#' + selected_id.id).addClass("highlight_popup_combo");
            });
            _.each(this.selected_unreq_product, function(selected_id) {
                $('#' + selected_id.id).prop("checked", true);
                $('#' + selected_id.id).addClass("highlight_popup_combo");

            });
            _.each(this.product_info, function(product_info) {
                var message = {'error': _t("Only " + product_info.no_of_items + " Products allowed to select in Combo")};
                _.each(product_info.combo_id.product_ids, function(product_id) {
                    $('#' + product_id).on('change', function() {
                        if($(this).is(":checked")) {
                            if(_.isUndefined(self.edit_product)) {
                                product_list.push($(this).val());
                                select_items = _.countBy(product_list, function(num) { return Math.ceil(num); });
                                if($(this).val() == product_info.combo_id.id) {
                                    if (product_info.combo_id.no_of_items < select_items[$(this).val()]) {
                                        self.pos.gui.show_popup('error', {
                                            title: _t('Oops! Failed to Select Products.'),
                                            body: message.error,
                                        });
                                    }
                                }
                            }
                            else {
                                self.edit_product.push($(this).val());
                                self.after_edit_combo.push($(this).val());
                                select_items = _.countBy(self.edit_product, function(num) { return Math.ceil(num); });
                                if($(this).val() == product_info.combo_id.id) {
                                    if(product_info.combo_id.no_of_items < select_items[$(this).val()]) {
                                        _.each(self.after_edit_combo, function(items) {
                                            var index = self.edit_product.indexOf(items)
                                            if (index > -1) {
                                                self.edit_product.splice(index, 1);
                                            }
                                            self.pos.gui.show_popup('error', {
                                                title: _t('Oops! Failed to Edit Products.'),
                                                body: message.error,
                                            });
                                        })

                                    }
                                }
                            }
                            $(this).addClass("highlight_popup_combo");
                        } else {
                            product_list.pop($(this).val());
                            if(!_.isUndefined(self.edit_product)) {
                                var index = self.edit_product.indexOf($(this).val())
                                if (index > -1) {
                                    self.edit_product.splice(index, 1);
                                }
                            }
                            $(this).removeClass("highlight_popup_combo");
                        }
                    });
                });
            });
        },
        click_confirm: function(event) {
            var unreq_product = [];
            var self = this;
            this.edit_product = [];
            $.each($("input[name='product']:checked"), function() {
                unreq_product.push($(this).data('tag'));
                self.edit_product.push($(this).val());
            });

            var require_products;
            var no_of_items;
            _.each(this.product_info, function(combo_line) {
                if (combo_line.require) {
                    require_products = combo_line.combo_id.product_ids;
                    no_of_items = combo_line.no_of_items;
                }
            });
            var common = [];
            if (require_products && unreq_product) {
                common = $.grep(unreq_product, function(element) {
                    return $.inArray(element, require_products) !== -1;
                });
            }

            var message = {'error': _t("Please select " + no_of_items + " required products in Combo")};
            if (require_products && no_of_items && (!common || no_of_items != common.length)) {
                return self.pos.gui.show_popup('error', {
                    title: _t('Oops! Failed to Select Products.'),
                    body: message.error,
                });
            }
            if(this.options.confirm) {
                this.gui.close_popup();
                if (_.isObject(this.product)) {
                    this.pos.get_order().add_product(this.product);
                }
                this.options.confirm.call(this,unreq_product);
            }
        },
    });
    gui.define_popup({name: 'combo_apply_popup', widget: ComboApplyPopup});

    var ProductNotesPopupWidget = PopupWidget.extend({
        template: 'ProductNotesPopupWidget',
        show: function(options) {
            options = options || {};
            this._super(options);
            var notes = this.pos.product_notes;
            if (notes) {
                this.events["click .product_note .button"] = "click_note_button";
                this.events["click .note_type .button"] = "click_note_type";
                this.notes = notes;
                this.all_notes = notes;
            }
            this.notes.forEach(function(note) {
                note.active = false;
            });

            this.custom_order_ids = options.custom_order_ids || false;
            this.custom_product_ids = options.custom_product_ids || false;

            this.set_active_note_buttons();
            this.set_available_notes();
            this.renderElement();
            this.render_active_note_type();
        },
        set_active_note_buttons: function() {
            if (!this.notes) {
                return false;
            }
            var self = this;
            var custom_notes = false;
            if (this.get_note_type() === "Order") {
               custom_notes = this.custom_order_ids;
            } else if (this.get_note_type() === "Product") {
                custom_notes = this.custom_product_ids;
            }
            if (custom_notes && custom_notes.length) {
                custom_notes.forEach(function(note) {
                    var exist_note = _.find(self.notes, function(n) {
                        return note.id === n.id;
                    });
                    if (exist_note) {
                        exist_note.active = true;
                    }
                });
            }
        },
        set_available_notes: function() {
            var type = this.get_note_type();
            if (type === "Order") {
                this.notes = this.all_notes;
            }
            if (type === "Product") {
                var order = this.pos.get_order();
                var orderline = order.get_selected_orderline();
                var category_ids = [];
                if (orderline.product.pos_categ_id && orderline.product.pos_categ_id.length) {
                    category_ids = [orderline.product.pos_categ_id[0]];
                } else if (orderline.product.pos_category_ids) {
                    category_ids = orderline.product.pos_category_ids;
                }
                this.notes = this.get_notes_by_category_ids(category_ids);
            }
        },
        get_notes_by_category_ids: function(category_ids) {
            var self = this;

            var cat_ids = [];
            function get_parent_category_ids(child_category_id) {
                if (cat_ids.indexOf(child_category_id) === -1) {
                    cat_ids.push(child_category_id);
                }
                var parent_category_id = self.pos.db.get_category_parent_id(child_category_id);
                if (parent_category_id && parent_category_id !== 0) {
                    cat_ids.push(parent_category_id);
                    return get_parent_category_ids(parent_category_id);
                }
                return cat_ids;
            }

            var all_categories_ids = [];
            category_ids.forEach(function(id) {
                all_categories_ids = all_categories_ids.concat(get_parent_category_ids(id));
            });
            all_categories_ids = _.uniq(all_categories_ids);

            return this.all_notes.filter(function(note) {
                if (_.isEmpty(note.pos_category_ids)) {
                    return true;
                }
                var res = _.intersection(note.pos_category_ids, all_categories_ids);
                if (_.isEmpty(res)) {
                    return false;
                }
                return true;
            });
        },
        render_active_note_type: function() {
            var product_type = $(".note_type .product_type");
            var order_type = $(".note_type .order_type");
            if (this.get_note_type() === "Order") {
                if (product_type.hasClass("active")){
                    product_type.removeClass("active");
                }
                order_type.addClass("active");
            } else if (this.get_note_type() === "Product") {
                if (order_type.hasClass("active")) {
                    order_type.removeClass("active");
                }
                product_type.addClass("active");
            }
        },
        get_note_type: function() {
            return this.pos.get_order().note_type;
        },
        set_note_type: function(type) {
            var order = this.pos.get_order();
            order.note_type = type;
        },
        get_note_by_id: function(id) {
            return _.find(this.notes, function(item) {
                return item.id === Number(id);
            });
        },
        click_note_type: function(e) {
            var old_note_type = {};
            old_note_type.note_type = this.get_note_type();
            if (e.currentTarget.classList[0] === "product_type") {
                this.set_note_type("Product");
            } else if (e.currentTarget.classList[0] === "order_type") {
                this.set_note_type("Order");
            }
            if (old_note_type.note_type !== this.get_note_type()) {
                this.gui.screen_instances.products.action_buttons.orderline_note.button_click();
            }
        },
        click_note_button: function(e) {
            var self = this;
            var id = e.currentTarget.getAttribute('data-id');
            if (id === 'other') {
                self.gui.show_screen('notes_screen', {notes: this.notes});
            } else {
                self.set_active_note_status($(e.target), Number(id));
            }
        },
        set_active_note_status: function(note_obj, id) {
            if (note_obj.hasClass("active")) {
                note_obj.removeClass("active");
                this.get_note_by_id(id).active = false;
            } else {
                note_obj.addClass("active");
                this.get_note_by_id(id).active = true;
            }
        },
        click_confirm: function() {
            this.gui.close_popup();
            var value = {};
            var notes = this.notes.filter(function(note) {
                return note.active === true;
            });

            if (this.get_note_type() === "Order") {
                value.custom_order_ids = notes;
            } else if (this.get_note_type() === "Product") {
                value.custom_product_ids = notes;
            }

            if (this.options.confirm) {
                value.note = this.$('.popup-confirm-note textarea').val();
                this.options.confirm.call(this, value);
            }
        }
    });
    gui.define_popup({name:'product_notes', widget: ProductNotesPopupWidget});

});
