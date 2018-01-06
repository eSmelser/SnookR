let $ = require('jquery');
$(document).ready(function() {
let sessionEvent = (function() {

  // Cache DOM
  let $container = $('#main-content');
  let $inviteForm = $container.find('#invites-form');
  let $inviteToggles = $container.find('.invite-toggle');

  // Initialize data
  let selected = [];

  // Function definitions
  const render = function() {
    $inviteForm.find('.hidden-sub-field').empty();

    selected.map( id => {
      let hiddenInput = $('<input>', { type: 'hidden', 'class': 'hidden-sub-field', value: id });
      $inviteForm.append(hiddenInput);

      let selector = `.invite-toggle[data-sub-id="${id}"]`
      $container.find(selector).attr('value', 'Uninvite').css('border-color', 'red');
    });

    $container.find('.invite-toggle').each(function(){
      let id = $(this).attr('data-sub-id');
      if (!selected.includes(id)) {
        $(this).attr('value', 'Invite');
        $(this).css('border-color', '');
      }
    });
  };

  const toggleInvite = function() {
    let subId = $(this).attr('data-sub-id');
    let index = selected.indexOf(subId);
    if (index === -1) {
      selected.push(subId);
    } else {
      selected.splice(index, 1);
    }

    render();
  };

  const bindEvents = function() {
    $container.on('click', '.invite-toggle', toggleInvite);
  };

  const init = function() {
    bindEvents();
    render();
  };

  return {
    init,
  }
})();

sessionEvent.init();
})
