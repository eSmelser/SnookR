/**
 * Created by bobby on 1/19/18.
 */
require('../../vendor/tokeninput/js/jquery.tokeninput');
let api = require('../../api/js/api');
let $ = require('jquery');

const $form = $('#assign-captain-form');
let users = [];


$(document).ready(function () {
    $("#text-input").tokenInput(api.tokenInputUrl, {
        preventDuplicates: true,
        onAdd: data => users.push(data),
        onDelete: data => {
            //noinspection EqualityComparisonWithCoercionJS, we want no coercion so that number ids and string ids are coerced
            users = users.filter(user => user.id != data.id);
        },
    });

    $form.submit(function (event) {
        users.map(user => {
            let $hidden = $('<input>', {'type': 'hidden', 'name': 'user', 'value': user.id});
            $form.append($hidden);
        });
    });
});