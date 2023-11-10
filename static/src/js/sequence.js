odoo.define('walkway_program.sequence', function (require) {
    'use strict';
    console.log('kkkk')

    var ListRenderer = require('web.ListRenderer');

    ListRenderer.include({
        events: _.extend({}, ListRenderer.prototype.events, {
            'click .o_data_row .o_list_number': '_onClickSequence',
        }),

        _onClickSequence: function (ev) {
            ev.preventDefault();
            var $row = $(ev.currentTarget).closest('.o_data_row');
            // Your logic to handle sequence click event
        },
    });
});