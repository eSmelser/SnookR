/**
 * Created by bobby on 12/31/17.
 */

let Handlebars = require('handlebars');
let $ = require('jquery');
let template = require('./sub.handlebars');
let User = require('../../accounts/js/user');

const Sub = function (sub, currentUserIsCaptain) {
    User.call(this, sub.user);
    this.currentUserIsCaptain = currentUserIsCaptain;
    this.sessionEvent = sub.session_event;
    this.$dom = this.getDOM();
};

// All users have the same template and getDOM function();
Sub.prototype.template = template;
Sub.prototype.getDOM = function (currentUserIsCaptain) {
    return $(this.template({ sub: this, currentUserIsCaptain: this.currentUserIsCaptain }));
};

Sub.prototype.constructor = Sub;
module.exports = Sub;