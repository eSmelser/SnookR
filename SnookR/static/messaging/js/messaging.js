let $ = require('jquery');
let api = require('../../api/js/api.js')
let Turbolinks = require("turbolinks");
Turbolinks.start()

document.addEventListener("turbolinks:load", function() {
let messaging = (function() {
  // Cache dom
  const $recentMessageItems = $('.recent-message-item');
  const $messageTextForm = $('#message-text-form');
  const $messagesList = $('#messages-list');
  const $textInput = $messageTextForm.find('#id_text');

  // Init
  let scheduledUpdates = [];
  let userId = $('#user-id').val();
  let friendId = $('#friend-id').val();

  $textInput.focus();

  const scrollDownMessageList = function() {
    let dom = document.getElementById('messages-list');
    let scrollHeight = dom.scrollHeight;

    let $dom = $(dom);
    $dom.scrollTop(scrollHeight);
  }

  const update = function() {
    let username = $('#friend-name').attr('data-friend-username');
    api.getNewMessage({ username: username }).done(function(data) {
       $('#messages-list').append($(data));
       scrollDownMessageList();
     }).fail(function(data) {
       console.log('fail', data);
     });
     scheduledUpdate = setTimeout(update, 5000);
     scheduledUpdates.push(scheduledUpdate);
  };

  const unscheduleUpdates = function() {
    scheduledUpdates.map( id => clearTimeout(id) );
  };

  const goToConversation = function() {
    let href = $(this).attr('href');
    Turbolinks.visit(href);
  };

  const sendMessage = function(event) {
    event.preventDefault();
    let data = {
      sender: userId,
      receiver: friendId,
      text: $textInput.val()
    };

    api.postMessage(data)
        .done(function(data) {
          $messagesList.append($(data));
          scrollDownMessageList()
          $textInput.val('');
        }).fail(function(data) {
    });
  };

  // Bind events
  $recentMessageItems.click(goToConversation);
  $messageTextForm.submit(sendMessage);

  document.addEventListener("turbolinks:before-visit", function() {
    unscheduleUpdates();
  });

  scrollDownMessageList()
  update();
})()
});
