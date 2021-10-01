odoo.define('addon_hr_customizations.employee_actions', function (require) {
    "use strict";

    var ListView = require('web.ListView');

    ListView.include({
        init: function() {
            this._super.apply(this, arguments);
            if (this.controllerParams.modelName === 'hr.employee') {
                var self = this;
                self.controllerParams.archiveEnabled = false;
                self.controllerParams.activeActions.delete = false;
             }
        }
    });

});