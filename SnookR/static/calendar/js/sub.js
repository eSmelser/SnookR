/**
 * Created by bobby on 12/31/17.
 */

let Handlebars = require('handlebars');
let $ = require('jquery');
let template = require('./sub.handlebars');
let User = require('../../accounts/js/user');
let api = require('../../api/js/api');

const Sub = function (sub, currentUser) {
    User.call(this, sub.user);
    console.log('sub', sub);
    this.id = sub.id;
    this.currentUser = currentUser;
    this.isCurrentUser = this.id === this.currentUser.id;
    this.sessionEvent = sub.session_event;
    this.cacheDom();
    this.bindEvents();
};

// All users have the same template and getDOM function();
Sub.prototype.template = template;

Sub.prototype.getDOM = function () {
    return $(this.template({ sub: this }));
};

Sub.prototype.cacheDom = function() {
    this.$dom = this.getDOM();
    this.$inviteButton = this.$dom.find('.invite-button');
};

Sub.prototype.bindEvents = function() {
    this.$inviteButton.click(this.createInvite.bind(this))
};

Sub.prototype.createInvite = function(event) {
    event.preventDefault();
    self = this;
    api.postSessionEventInvite(this.getPostData())
    .done(function(data) {
        console.log('success!', data);
        self.displaySuccessfulInvite();
    }).fail(function(data) {
        console.log('error!', data);
    });
};

Sub.prototype.getPostData = function() {
    return {
        sub: {
            id: this.id,
            session_event: { id: this.sessionEvent.id },
        },
        captain: { username: this.currentUser.username }
    };
};

Sub.prototype.displaySuccessfulInvite = function() {
    this.$inviteButton.replaceWith(`<strong>Successful Invite!</strong>`);
};

Sub.prototype.constructor = Sub;
module.exports = Sub;