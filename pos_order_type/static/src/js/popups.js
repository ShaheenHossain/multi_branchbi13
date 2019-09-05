odoo.define('pos_order_type.popups', function (require) {
"use strict";

var PopupWidget = require('point_of_sale.popups');
var gui = require('point_of_sale.gui');
var core = require('web.core');
var _t = core._t;

var OrderTypePopupWidget = PopupWidget.extend({
    template: 'OrderTypePopupWidget',

    show: function(options){
        var self = this;
        options = options || {};
        this._super(options);
        this.list = options.list || [];
        this.selected_item = this.selected_item || "customer";
        this.is_selected = options.is_selected || function (item) { return false; };
        this.code_needed = false;
        if (this.pos.config.iface_vkeyboard && this.chrome.widget.keyboard) {
            this.chrome.widget.keyboard.connect($(this.el.querySelector('input')));
        }

        this.renderElement();
    },

    click_item: function(event) {
        if (this.options.confirm) {
            var item = this.list[parseInt($(event.target).data('item-index'))];
            item = item ? item.item : item;
            this.selected_item = item;

            $(event.target).parent().find('.selection-item').removeClass('selected');
            $(event.target).addClass('selected');

            if (_.contains(["manager", "staff"], item)) {
                this.$('input').attr('type', 'password').focus();
                this.code_needed = true;
            } else {
                this.$('input').attr('type', 'hidden');
                this.code_needed = false;
            }
        }
    },

    click_confirm: function(){
        var codevalue = this.$('input').val();
        this.gui.close_popup();
        if(this.options.confirm){
            var authorised_user = _.find(this.pos.users, function (user) {
                return user.pos_authorisation_code === codevalue;
            });
            if (this.code_needed && !codevalue) {
                this.gui.show_popup('error',{
                    'title': _t('Code Needed!'),
                    'body': _t('Code needed of authorised user.'),
                });
            } else if (this.code_needed && codevalue && _.isUndefined(authorised_user)) {
                this.gui.show_popup('error',{
                    'title': _t('Incorrect Code!'),
                    'body': _t('No authorised user found for entered code.'),
                });
            } else {
                this.options.confirm.call(this, this.selected_item, authorised_user);
            }
        }
    },

});

gui.define_popup({name: 'order_type', widget: OrderTypePopupWidget});

});
