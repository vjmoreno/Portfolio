odoo.define('hr.action_button_raise_employee_alert', function (require) {
    "use strict";

    var ListController = require('web.ListController');
    var KanbanController = require('web.KanbanController');
    
    ListController.include({
        renderButtons: function($node) {
            this._super.apply(this, arguments);
            if (this.modelName === "hr.employee.alert") {
                var data = this.model.get(this.handle);
                if (data.context.hide_button) {
                    this.$buttons.find('.o_button_raise_employee_alert').hide(); // Hide button from employee form drilled down in alerts
                }
                else {
                    this.$buttons.find('.o_button_raise_employee_alert').click(this.proxy('action_raise_employee_alert'));
                }
            }
        },
        /**
        * @private
        * @param {MouseEvent} event
        */
        action_raise_employee_alert: function () {
            var self = this;
            this._rpc({
                model: 'hr.employee.alert',
                method: 'trigger_raise_employee_alert',
                args: [""],
            }).then(function (e) {
                self.do_action({
                    type: 'ir.actions.client',
                    tag: 'reload',
                });
            });
        },
    });

    KanbanController.include({
        renderButtons: function($node) {
            this._super.apply(this, arguments);
            if (this.modelName === "hr.employee.alert") {
                var data = this.model.get(this.handle);
                if (data.context.hide_button) {
                    this.$buttons.find('.o_button_raise_employee_alert').hide(); // Hide button from employee form drilled down in alerts
                }
                else {
                    this.$buttons.find('.o_button_raise_employee_alert').click(this.proxy('action_raise_employee_alert'));
                }
            }
        },
        /**
        * @private
        * @param {MouseEvent} event
        */
        action_raise_employee_alert: function () {
            var self = this;
            this._rpc({
                model: 'hr.employee.alert',
                method: 'trigger_raise_employee_alert',
                args: [""],
            }).then(function (e) {
                self.do_action({
                    type: 'ir.actions.client',
                    tag: 'reload',
                });
            });
        },
    });
});