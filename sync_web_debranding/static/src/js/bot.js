odoo.define('sync_web_debranding.Bot', function (require) {
    "use strict";

    var session = require('web.session');
    var WebClient = require('web.WebClient');

    WebClient.include({
        show_application: function () {
            var self = this;
            return $.when(this._super.apply(this, arguments)).then(function () {
                self._rpc({
                    model: 'ir.config_parameter',
                    method: 'get_param',
                    args: ['sync_app_system_name']
                }).then(function (system_name) {
                    session.system_name = system_name;
                    self._rpc({
                        model: 'ir.model.data',
                        method: 'get_object_reference',
                        args: ['base','partner_root']
                    }).then(function (partner_id) {
                        self._rpc({
                            model: 'res.partner',
                            method: 'write',
                            args: [partner_id[1], {name: system_name + ' ' + 'Bot'}],
                        });
                    });
                });
            });
        },
    });

});