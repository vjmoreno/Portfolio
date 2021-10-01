odoo.define('CustomFields.AffectedEmployees', function (require) {
    "use strict";

    const registry = require('web.field_registry');
    const FieldChar = require('web.basic_fields').FieldChar;

    const AffectedEmployeeChar = FieldChar.extend({
        events: _.extend({}, FieldChar.prototype.events, {
            "click": "openAffectedEmployees",
        }),
        openAffectedEmployees: function(e) {
            e.stopPropagation();
            this.trigger_up('button_clicked', {
                attrs: {
                    type: 'object',
                    name: 'see_affected_employees'
                },
                record: this.record
            });
        }
    });

    registry
        .add('affected_employee_widget', AffectedEmployeeChar)

    return { AffectedEmployeeChar };
});