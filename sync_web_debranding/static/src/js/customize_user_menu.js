odoo.define('sync_web_debranding.UserMenu', function (require) {
    "use strict";

    var UserMenu = require('web.UserMenu');
    var documentation_url = '';
    var documentation_dev_url;
    var support_url;
    var account_title;
    var account_url;

    UserMenu.include({
        init: function () {
            this._super.apply(this, arguments);
            var self = this;
            var session = this.getSession();
            var lang_list = '';

            self._rpc({
                model: 'res.lang',
                method: 'search_read',
                domain: [],
                fields: ['name', 'code'],
                lazy: false,
            }).then(function (res) {
                _.each(res, function (lang) {
                    var a = '';
                    if (lang['code'] === session.user_context.lang) {
                        a = '<i class="fa fa-check"></i>';
                    } else {
                        a = '';
                    }
                    lang_list += '<a role="menuitem" href="#" class="dropdown-item" data-lang-menu="lang" data-lang-id="' + lang['code'] + '"><img class="flag" src="/sync_web_debranding/static/src/img/flags/' + lang['code'] + '.png"/>' + lang['name'] + a + '</a>';
                });
                lang_list += '<div role="separator" class="dropdown-divider"/>';
                $('switch-lang').replaceWith(lang_list);
            })

            //Take parameters
            self._rpc({
                model: 'ir.config_parameter',
                method: 'search_read',
                domain: [['key', '=like', 'sync_app_%']],
                fields: ['key', 'value'],
                lazy: false,
            }).then(function (res) {
                $.each(res, function (key, val) {
                    if (val.key == 'sync_app_documentation_url')
                        documentation_url = val.value;
                    if (val.key == 'sync_app_documentation_dev_url')
                        documentation_dev_url = val.value;
                    if (val.key == 'sync_app_support_url')
                        support_url = val.value;
                    if (val.key == 'sync_app_account_title')
                        account_title = val.value;
                    if (val.key == 'sync_app_account_url')
                        account_url = val.value;
                    if (val.key == 'sync_app_show_lang' && val.value == "False") {
                        $('switch-lang').hide();
                    }
                    if (session.user_context.uid > 2 || (val.key == 'sync_app_show_debug' && val.value == "False")) {
                        $('[data-menu="debug"]').hide();
                        $('[data-menu="debugassets"]').hide();
                        $('[data-menu="quitdebug"]').hide();
                    }
                    if (val.key == 'sync_app_show_documentation' && val.value == "False") {
                        $('[data-menu="documentation"]').hide();
                    }
                    if (val.key == 'sync_app_show_documentation_dev' && val.value == "False") {
                        $('[data-menu="documentation_dev"]').hide();
                    }
                    if (val.key == 'sync_app_show_support' && val.value == "False") {
                        $('[data-menu="support"]').hide();
                    }
                    if (val.key == 'sync_app_show_account' && val.value == "False") {
                        $('[data-menu="account"]').hide();
                    }
                    if (val.key == 'sync_app_account_title' && val.value) {
                        $('[data-menu="account"]').html(account_title);
                    }
                    if (val.key == 'sync_app_show_poweredby' && val.value == "False") {
                        $('.o_sub_menu_footer').hide();
                    }
                });
            })
        },
        /**
         * @override
         * Since odoo11 did not pass the ev to the event, it was overloaded.
         */
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                //Language switching special processing
                self.$el.on('click', 'a[data-lang-menu]', function (ev) {
                    ev.preventDefault();
                    var f = self['_onMenuLang']
                    f.call(self, $(this));
                });
                //Control debug display
                var mMode = 'normal';
                if (window.location.href.indexOf('debug') != -1)
                    mMode = 'debug';
                if (window.location.href.indexOf('debug=assets') != -1)
                    mMode = 'assets';
                if (mMode == 'normal')
                    $('[data-menu="quitdebug"]').hide();
                if (mMode == 'debug')
                    $('[data-menu="debug"]').hide();
                if (mMode == 'assets')
                    $('[data-menu="debugassets"]').hide();
            });
        },
        _onMenuAccount: function () {
            window.open(account_url, '_blank');
        },
        _onMenuDocumentation: function () {
            window.open(documentation_url, '_blank');
        },
        _onMenuSupport: function () {
            window.open(support_url, '_blank');
        },
        //Increased method
        _onMenuDebug: function () {
            window.location = $.param.querystring(window.location.href, 'debug');
        },
        _onMenuDebugassets: function () {
            window.location = $.param.querystring(window.location.href, 'debug=assets');
        },
        _onMenuQuitdebug: function () {
            window.location.search = "?";
        },
        _onMenuDocumentation_dev: function () {
            window.open(documentation_dev_url, '_blank');
        },
        _onMenuLang: function (ev) {
            var self = this;
            var lang = ($(ev).data("lang-id"));
            var session = this.getSession();
            return this._rpc({
                model: 'res.users',
                method: 'write',
                args: [session.uid, {'lang': lang}],
            }).then(function (result) {
                self.do_action({
                    type: 'ir.actions.client',
                    res_model: 'res.users',
                    tag: 'reload_context',
                    target: 'current',
                });
            });
        },
    })
});
