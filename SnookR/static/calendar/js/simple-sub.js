/**
 * Created by bobby on 12/31/17.
 */

let Handlebars = require('handlebars');
let $ = require('jquery');
let template = require('./panel.handlebars');
let User = require('../../accounts/js/user');

const Sub = function (sub) {
    this.id = sub.id;
    this.user = new User(sub.user);
    this.sessionEvent = sub.session_event;
    this.invited = false;
    this.cacheDom();
    this.render();
    this.bindEvents();
};

Sub.prototype.template = template;

Sub.prototype.cacheDom = function() {
    this.$dom = $('<div>');
};

Sub.prototype.render = function() {
  let $templateDom = $(this.template({ sub: this }));
  this.$dom.empty().append($templateDom);
}

Sub.prototype.bindEvents = function() {
    this.$dom.on('click', '.invite-button', this.toggleInvited.bind(this))
    this.$dom.on('click', '.checkmark-button', this.toggleInvited.bind(this))
};

Sub.prototype.toggleInvited = function(event) {
  this.invited= !this.invited;
  this.render();
};

Sub.prototype.constructor = Sub;
module.exports = Sub;
