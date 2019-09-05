odoo.define('pos_product_combo.gui', function (require) {
    "use strict";

    var gui = require('point_of_sale.gui');

	gui.Gui.include({
        show_screen: function(screen_name, params, refresh, skip_close_popup) {
            this._super(screen_name, params, refresh, skip_close_popup);

            //compatibility with pos_mobile_restaurant
            if (odoo.is_mobile && screen_name === 'notes_screen') {
                var height = this.current_screen.$('table.note-list').height();
                var max_height = this.current_screen.$('.full-content').height();
                if (height > max_height) {
                    height = max_height;
                }
                this.current_screen.$('.subwindow-container-fix.touch-scrollable.scrollable-y').css({
                    'height': height
                });
                this.current_screen.$('.subwindow-container-fix.touch-scrollable.scrollable-y').getNiceScroll().resize();
            }
        }
    });
});
