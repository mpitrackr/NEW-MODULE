odoo.define('sync_web_debranding.field_upgrade', function (require) {
    "use strict";

    require('web.upgrade_widgets');
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var session = require('web.session');
    var field_registry = require('web.field_registry');
    var UpgradeBoolean = field_registry.get('upgrade_boolean');
    var UpgradeRadio = field_registry.get('upgrade_radio');

    var _t = core._t;

    if (!UpgradeBoolean) {
        return;
    }

    var include = {
        _render: function () {
            this._super.apply(this, arguments);
            this.$el.parent().parent().find("span.o_enterprise_label").hide();
            this.$el.parent().parent().parent().parent().find("span.o_enterprise_label").hide();
            this._rpc({
                model: 'ir.config_parameter',
                method: 'get_param',
                args: ['sync_app_support_url']
            }).then(function (support_url) {
                session.support_url = support_url;
            });
        },
        _openDialog: function () {
            var buttons = [
                {
                    text: _t("Cancel"),
                    close: true,
                },
            ];
            return new Dialog(this, {
                size: 'medium',
                buttons: buttons,
                $content: $('<div>', {
                    html: '<h3>Kindly contact us for this feature!! <span><a href="' + session.support_url + '" target="_blank">Click Here For More Info</a></h3>',
                }),
                title: _t(session.system_name),
            }).open();
        },
    };

    UpgradeRadio.include(include);
    UpgradeBoolean.include(include);
});