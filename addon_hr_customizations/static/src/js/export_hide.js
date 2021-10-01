odoo.define("hr.export_hide", function(require) {
    "use strict";

    const core = require("web.core");
    const Sidebar = require("web.Sidebar");
    const session = require("web.session");

    const _t = core._t;

    Sidebar.include({
        _addItems: function(sectionCode, items) {
            let _items = items;
            if ( this.env.model === 'hr.employee.alert')
            {
                _items = _.reject(_items, {label: _t("Export")});
            }
            this._super(sectionCode, _items);
        },
    });
});
