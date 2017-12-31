/**
 * Created by bobby on 12/31/17.
 */
let Handlebars = require('handlebars');
let $ = require('jquery');
let template = require('./user.handlebars');


const User = function (user) {
    this.id = user.id;
    this.firstname = user.first_name;
    this.lastname = user.last_name;
    this.thumbnailUrl = user.thumbnail_url;
    this.username = user.username;
    this.url = user.url;
    this.isCaptain = user.is_captain;
    this.isCurrentUser = user.is_current_user;
    this.$dom = this.getDOM();

    // Assign extra
    this.extras = null;
};

// All users have the same template and getDOM function();
User.prototype.template = template;
User.prototype.getDOM = function () {
    return $(this.template(this));
};

User.prototype.constructor = User;
module.exports = User;