odoo.define('hr.send_message_hide', function (require) {
    "use strict";

    var FormRenderer = require('web.FormRenderer');

    FormRenderer.include({

        autofocus: function () {
            var self = this;
            if(self.state.model === 'hr.employee.alert.rule'){
                var node = window.$('button.o_chatter_button_new_message');
                node.hide();
            }
            return this._super();
        },
    });

});
