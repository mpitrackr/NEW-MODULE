// Notification view chnage
odoo.define('sync_web_debranding.native_notifications', function (require) {
    "use strict";

    var session = require('web.session');
    var Message = require('mail.model.Message')
    var BusService = require('bus.BusService');

    Message.include({
        getAvatarSource: function () {
            if (this._isOdoobotAuthor()) {
                return 'data:image/png;base64,' + session.system_logo;
            } else if (this.hasAuthor()) {
                return '/web/image/res.partner/' + this.getAuthorID() + '/image_small';
            } else if (this.getType() === 'email') {
                return '/mail/static/src/img/email_icon.png';
            }
            return '/mail/static/src/img/smiley/avatar.jpg';
        },
        _getAuthorName: function () {
            if (this._isOdoobotAuthor()) {
                return session.system_name + ' ' + 'Bot';
            }
            return this._super.apply(this, arguments);
        },
    });

    BusService.include({
        _sendNativeNotification: function (title, content, callback) {
            var notification = new Notification(title, {body: content, icon: 'data:image/png;base64,' + session.system_logo});
            notification.onclick = function () {
                window.focus();
                if (this.cancel) {
                    this.cancel();
                } else if (this.close) {
                    this.close();
                }
                if (callback) {
                    callback();
                }
            };
        },
    });

});
