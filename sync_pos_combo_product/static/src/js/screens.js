odoo.define('pos_product_combo.screens', function (require) {
    "use strict";

    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var QWeb = core.qweb;

    screens.ProductScreenWidget.include({
        click_product: function(product) {
            if (product.is_combo) {
                var self = this;
                var order = this.pos.get_order();
                var require_products_id = [];
                var unrequired_products_id = [];
                var product_dic = {};
                var product_list = [];
                var require_product_list = [];
                var unrequire_product_list = [];
                _.each(self.pos.combo_products_by_id, function(value) {
                    if (order && value.product_template_id[0] === product.product_tmpl_id) {
                        if (value.is_required_product) {
                            _.each(value.product_ids, function(product_id) {
                                require_products_id.push(product_id);
                            });
                        }
                        else if (!(value.is_required_product)) {
                            _.each(value.product_ids, function(product_id) {
                                unrequired_products_id.push(product_id);
                            });
                        }
                        product_dic = {
                            'combo_id': value,
                            'no_of_items': value.no_of_items,
                            'require': value.is_required_product,
                            'category_id': value.category_id,
                        };
                        product_list.push(product_dic)
                        if (value.is_required_product) {
                            require_product_list.push(product_dic)
                        } else {
                            unrequire_product_list.push(product_dic)
                        }
                    }
                });
                var set_unreq_product = [];
                var select_require_product = [];
                var select_unrequire_product = [];
                var set_req_products = [];
                self.gui.show_popup('combo_apply_popup', {
                    pricelists: order.pricelist,
                    product: product,
                    product_info: product_list,
                    require_product_info: require_product_list,
                    unrequire_product_info: unrequire_product_list,
                    confirm: function(products) {
                        if(!_.isEmpty(products)) {
                            _.each(products, function(product_id) {
                                var req_product = _.find(require_products_id, function (product_ids) {
                                    return product_ids === product_id;
                                });
                                if(!_.isUndefined(req_product)){
                                    select_require_product.push(req_product);
                                }
                                var un_req_product = _.find(unrequired_products_id, function (product_ids) {
                                    return product_ids === product_id;
                                });
                                if(!_.isUndefined(un_req_product)){
                                    select_unrequire_product.push(un_req_product);
                                }
                            });
                            _.each(select_require_product, function(req_product_id){
                                var req_products = self.pos.db.get_product_by_id(req_product_id);
                                set_req_products.push(req_products);
                            });
                            _.each(select_unrequire_product, function(unreq_product_id){
                                var un_req_products = self.pos.db.get_product_by_id(unreq_product_id);
                                set_unreq_product.push(un_req_products);
                            });
                        }
                        var orderline = self.pos.get_order().get_orderlines();
                        var last_order_line = _.find(orderline, function (lines) {
                            return lines.is_combo_line === true;
                        });
                        var last_order_line = self.pos.get_order().get_last_orderline()
                        if (last_order_line.product.id === product.id) {
                            last_order_line.set_require_product(set_req_products);
                            last_order_line.set_unrequire_product(set_unreq_product);
                            var price = last_order_line.get_combo_price();
                            last_order_line.set_unit_price(price);
                            last_order_line.price_manually_set = true;
                        }
                    },
                });

            }
            else {
                this._super(product);
            }
        },
    });

    screens.OrderWidget.include({
        set_value: function(val) {
            var order = this.pos.get_order();
            var selected_orderline = order.get_selected_orderline();
            var mode = this.numpad_state.get('mode');
            if (!_.isUndefined(selected_orderline)){
                if( mode === 'quantity' && selected_orderline.is_combo_line){
                    var combo_price = selected_orderline.get_combo_price();
                    selected_orderline.price_manually_set = true;
                    selected_orderline.set_unit_price(combo_price);
                }
            }
            this._super(val);
        },
        render_orderline: function(orderline) {
            var node = this._super(orderline);
            var order = this.pos.get_order();
            var self = this;
            var unrequired_products_id = [];
            var require_products_id = [];
            var no_of_items = [];
            var product_dic = {};
            var product_list = [];
            var require_product_list = [];
            var unrequire_product_list = [];
            _.each(self.pos.combo_products_by_id, function(value) {
                if (orderline.is_combo_line && value.product_template_id[0] === orderline.get_product().product_tmpl_id) {
                    if (!(value.is_required_product)) {
                        _.each(value.product_ids, function(product_id) {
                            unrequired_products_id.push(product_id);
                        });
                    }
                    else {
                        _.each(value.product_ids, function(product_id) {
                            require_products_id.push(product_id);
                        });
                    }
                    product_dic = {
                        'combo_id': value,
                        'no_of_items': value.no_of_items,
                        'require': value.is_required_product,
                        'category_id': value.category_id,
                    };
                    product_list.push(product_dic)
                    if (value.is_required_product) {
                        require_product_list.push(product_dic)
                    } else {
                        unrequire_product_list.push(product_dic)
                    }

                }
            });
            var edit_button = node.querySelector('.edit_it');
            var select_require_product = [];
            var select_unrequire_product = [];
            var set_req_products = [];
            var set_unreq_product = [];
            if(edit_button) {
                edit_button.addEventListener('click', (function() {
                    self.gui.show_popup('combo_apply_popup', {
                        pricelists: order.pricelist,
                        selected_unreq_product: orderline.unreq_product,
                        selected_req_product: orderline.req_product,
                        product_info: product_list,
                        require_product_info: require_product_list,
                        unrequire_product_info: unrequire_product_list,
                        confirm: function(products) {
                            if(!_.isEmpty(products)) {
                                _.each(products, function(product_id) {
                                    var req_product = _.find(require_products_id, function (product_ids) {
                                        return product_ids === product_id;
                                    });
                                    if(!_.isUndefined(req_product)){
                                        select_require_product.push(req_product);
                                    }
                                    var un_req_product = _.find(unrequired_products_id, function (product_ids) {
                                        return product_ids === product_id;
                                    });
                                    if(!_.isUndefined(un_req_product)){
                                        select_unrequire_product.push(un_req_product);
                                    }
                                });
                                _.each(select_require_product, function(req_product_id){
                                    var req_products = self.pos.db.get_product_by_id(req_product_id);
                                    set_req_products.push(req_products);
                                });
                                _.each(select_unrequire_product, function(unreq_product_id){
                                    var un_req_products = self.pos.db.get_product_by_id(unreq_product_id);
                                    set_unreq_product.push(un_req_products);
                                });
                            }
                            orderline.set_require_product(set_req_products);
                            orderline.set_unrequire_product(set_unreq_product);
                            var price = orderline.get_combo_price();
                            orderline.set_unit_price(price);
                            orderline.price_manually_set = true;
                        },
                    });
                }.bind(this)));
            }
            return node;
        },
    });

    var ProductNotesScreenWidget = screens.ScreenWidget.extend({
        template: 'ProductNotesScreenWidget',
        events: {
            'click .note-line': function (event) {
                var id = event.currentTarget.getAttribute('data-id');
                var line = $('.note-list-contents').find(".note-line[data-id='" +parseInt(id)+"']");
                this.set_active_note_status(line, Number(id));
            },
            'click .note-back': function () {
                this.gui.back();
            },
            'click .note-next': function () {
                this.save_changes();
                this.gui.back();
            },
        },
        auto_back: true,
        show: function(){
            this._super();
            this.notes = this.gui.get_current_screen_param('notes');
            this.render_list(this.notes);
        },
        set_active_note_status: function(note_obj, id){
            if (note_obj.hasClass("highlight")) {
                note_obj.removeClass("highlight");
                this.get_note_by_id(id).active = false;
            } else {
                note_obj.addClass("highlight");
                this.get_note_by_id(id).active = true;
            }
        },
        render_list: function(notes){
            var contents = this.$el[0].querySelector('.note-list-contents');
            contents.innerHTML = "";
            for(var i = 0, len = Math.min(notes.length,1000); i < len; i++){
                var product_note_html = QWeb.render('ProductNotes',{widget: this, note:notes[i]});
                var product_note = document.createElement('tbody');
                product_note.innerHTML = product_note_html;
                product_note = product_note.childNodes[1];

                if (notes[i].active) {
                    product_note.classList.add('highlight');
                } else {
                    product_note.classList.remove('highlight');
                }
                contents.appendChild(product_note);
            }
        },
        save_changes: function(){
            var order = this.pos.get_order();
            var line = order.get_selected_orderline();

            var notes = this.notes.filter(function(note){
                return note.active === true;
            });

            var simple_note = $('.popup-confirm-note textarea').val();

            if (order.note_type === "Order") {
                order.set_custom_notes(notes);
                order.set_note(simple_note);
            } else if (order.note_type === "Product") {
                line.set_custom_notes(notes);
                line.set_note(simple_note);
            }
        },
        get_note_by_id: function(id) {
            return _.find(this.notes, function(item) {
                return item.id === Number(id);
            });
        },
    });
    gui.define_screen({name:'notes_screen', widget: ProductNotesScreenWidget});

});