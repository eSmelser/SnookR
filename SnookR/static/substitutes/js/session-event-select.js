require('../../calendar/js/session-event-calendar.js');
let jQuery = require('jquery');

$(document).ready(function() {
  let invitedList = [];
  let $parent = $('.divisions-div');

  const addToInvitedList = function(_, obj) {
    let id = $(obj).attr('data-sub-id');
    invitedList.push(id);
  };

  $('#submit').click(function() {
    invitedList = [];
    $parent.find('.invite-status[data-invited="true"]').each(addToInvitedList);
    let params = jQuery.param({ sub: invitedList, teamId: context.teamId }, true);
    let url = $(this).attr('href');
    window.location.href = url + '?' + params;
  });
});
