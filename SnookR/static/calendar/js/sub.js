/**
 * Created by bobby on 12/31/17.
 */

let Handlebars = require('handlebars');
let $ = require('jquery');
let template = require('./sub.handlebars');
let User = require('../../accounts/js/user');
let api = require('../../api/js/api');

const Sub = function (sub, currentUser, alreadyInvited = false) {
    this.id = sub.id;
    this.user = new User(sub.user);
    this.currentUser = currentUser;
    this.isCurrentUser = this.user.id === this.currentUser.id;
    console.log('sub', this);
    this.sessionEvent = sub.session_event;
    this.alreadyInvited = alreadyInvited;
    this.cacheDom();
    this.bindEvents();
    this.render();
};

// All users have the same template and getDOM function();
Sub.prototype.template = template;

Sub.prototype.getDOM = function () {
    return $('<div>').append( $(this.template({ sub: this })) );
};

Sub.prototype.cacheDom = function() {
    this.$dom = this.getDOM();
    this.$inviteButton = this.$dom.find('.invite-button');
};


Sub.prototype.render = function() {
  this.$dom.replaceWith(this.getDOM());
  this.bindEvents();
}

Sub.prototype.bindEvents = function() {
    this.$inviteButton.click(this.createInvite.bind(this))
};

Sub.prototype.createInvite = function(event) {
  console.log('createInvite')
    event.preventDefault();
    self = this;
    api.postSessionEventInvite(this.getPostData())
    .done(function(data) {
        self.alreadyInvited = true
        self.render();
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

Sub.prototype.constructor = Sub;
module.exports = Sub;
