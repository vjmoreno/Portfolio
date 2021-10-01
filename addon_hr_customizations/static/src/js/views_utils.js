odoo.define('nanoramic.tree_no_open', function (require) {
"use strict";

    var core = require('web.core');
    var ActionManager = require('web.ActionManager');
    var List = require('web.ListRenderer');
    var ListController = require('web.ListController');
    var FormController = require('web.FormController');
    var _t = core._t;

    ListController.include({
         _onCreateRecord: function (ev) {
            var self = this;
            if (this.modelName === 'hr.employee') {
                // alert('CREATE');
                var action_manager = new ActionManager(self);
                action_manager.do_action("addon_hr_customizations.create_employee_action");
            } else {
            return this._super.apply(this, arguments);
            }
        }
    });

    FormController.include({
    createRecord: function (parentID) {
        var self = this;
        if (this.modelName === 'hr.employee') {
            var action_manager = new ActionManager(self);
            action_manager.do_action("addon_hr_customizations.create_employee_action");
        } else {
            return this._super.apply(this, arguments);
        }
    }
    });
    
    List.include({
    /**
     * @private
     * prevents form view open upon
     * clicking on tree row when
     * in no-edit mode
     * usage <tree class="tree_no_open" >
     */
    _onRowClicked:function(e){
        if(!this.el.classList.contains('tree_no_open')) {
            this._super.apply(this,arguments);
            }
        },

    });
});