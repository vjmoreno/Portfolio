
odoo.define('addon_hr_customizations.CalendarView', function (require) {
"use strict";

var CalendarPopover = require('web.CalendarPopover');

CalendarPopover.include({
    events: _.extend({}, CalendarPopover.prototype.events, {
        'click .o_cw_popover_timesheet': '_onClickAddTimesheet'
    }),
    init: function () {
        var self = this;
        this._super.apply(this, arguments);
        // Show status dropdown if user is in attendees list
        this.has_timesheet = this.event.record.timesheet_id ? true : false;
    },
    _onClickAddTimesheet: function (ev) {
        ev.preventDefault();
        var self = this;

        console.log('THIS EVENT', this.event);
        if (this.event.id === parseInt(this.event.id, 10))
            var event_id = this.event.id;
        else
            var event_id = parseInt(this.event.id.split("-", 1)[0]);

        this.do_action({
            //context: {create: false},
            name: 'Add Timesheet',
            type: 'ir.actions.act_window',
            views: [[false, 'form']],
            res_model: 'event.create.timesheet.wizard',
            view_mode: 'form',
            target: 'new',
            context: {default_google_event_id: event_id}
            //flags: {mode: 'edit'},
        });
        $(this.el.parentElement).popover('dispose');

    },
})

});
