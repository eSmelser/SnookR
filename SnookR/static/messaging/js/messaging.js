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
  const $recentMessageGroup = $('#recent-messages-group');
  const $firstMessage = $messagesList.find('.message-item').first()
  const $loader = $('#loader').hide();

  // Init
  let scheduledUpdates = [];
  let userId = $('#user-id').val();
  let friendId = $('#friend-id').val();
  let username = $('#friend-name').attr('data-friend-username');
  let scrolledToBottom = true;
  let firstMessageId = $firstMessage.attr('id').split('-').pop();
  firstMessageId = parseInt(firstMessageId);
  $textInput.focus();

  const scrollDownMessageList = function() {
    let dom = document.getElementById('messages-list');
    let scrollHeight = dom.scrollHeight;

    let $dom = $(dom);
    $dom.scrollTop(scrollHeight);
  }

  const update = function() {
    api.getNewMessage({ username: username }).done(function(data) {
       if (data) {
         $messagesList.append($(data));
         if(!scrolledToBottom) {
           scrollDownMessageList()
         }
       }
     }).fail(function(data) {
       console.log('update failed', data);
     });
     scheduledUpdate = setTimeout(update, 5000);
     scheduledUpdates.push(scheduledUpdate);
  };

  const unscheduleUpdates = function() {
    scheduledUpdates.map( id => clearTimeout(id) );
    scheduledUpdates = [];
  };

  const goToConversation = function() {
    let href = $(this).attr('href');
    Turbolinks.visit(href);
  };

  const moveCurrentConversationToTopOfRecent = function() {
    let $friendRecent = $recentMessageGroup.find(`[data-friend-id=${friendId}]`);
    let $header = $recentMessageGroup.find('#recent-header');

    $friendRecent.detach();
    $header.detach();
    $recentMessageGroup.prepend($friendRecent).prepend($header);
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
          if(!scrolledToBottom) {
            scrollDownMessageList()
          }
          $textInput.val('');
          //moveCurrentConversationToTopOfRecent();
        }).fail(function(data) {
    });
  };

  const unbindEvents = function() {
    $recentMessageItems.unbind();
    $messageTextForm.unbind();
    $messagesList.unbind();
  };

  const destroy = function() {
    unscheduleUpdates();
    unbindEvents();
  }

  // Bind events
  $recentMessageItems.click(goToConversation);
  $messageTextForm.submit(sendMessage);
  $messagesList.scroll(function(event) {
    // Stick to bottom when new messages come up if user has scrolled to bottom manually
    let scrollDiff = this.scrollHeight - $(this).scrollTop();
    let height = $(this).outerHeight();
    let scrolledToBottom = scrollDiff == Math.floor(height);
  })

  document.addEventListener("turbolinks:before-visit", destroy);
  $messagesList.scroll(function(event) {
    if ($(this).scrollTop() === 0) {
      $loader.show();

      let userSent = {
        'sender__id': userId,
        'receiver_id': friendId,
        'id__lt': firstMessageId,
        'id__gt': firstMessageId - 20,
      };

      let friendSent = {
        'sender__id': friendId,
        'receiver_id': userId,
        'id__lt': firstMessageId,
        'id__gt': firstMessageId - 20,
      };

      api.getMessages(userSent).done(function(userSentMessages) {
          api.getMessages(friendSent).done(function(friendSentMessages) {
            $loader.hide();

            let messages = userSentMessages.concat(friendSentMessages);
            messages.sort( (a, b) => a.id - b.id );
            console.log('meseages', messages);
          });
      });
    }
  });

  // Setup
  scrollDownMessageList()
  update();
})()
});
