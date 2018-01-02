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
    console.log('Sub!');
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
    console.log('here');
    this.$inviteButton.click(this.createInvite.bind(this))
};

Sub.prototype.createInvite = function(event) {
    event.preventDefault();
    console.log('id', this.id);
    let data = { invitee: this, event: this.sessionEvent };
    console.log('data', data);
    api.postSessionEventInvite(data)
    .done(function(data) {
        console.log('success!', data);
        this.displaySuccessfulInvite();
    }).fail(function(data) {
        console.log('error!', data);
    });
};

Sub.prototype.displaySuccessfulInvite = function() {
    this.$inviteButton.replaceWith(`<strong>Successful Invite!</strong>`);
};

Sub.prototype.constructor = Sub;
module.exports = Sub;