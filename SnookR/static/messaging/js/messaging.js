let $ = require('jquery');
let api = require('../../api/js/api.js')
let Turbolinks = require("turbolinks");
Turbolinks.start()


let text = '';

document.addEventListener("turbolinks:before-visit", function() {
  text = $('#id_text').val();
  console.log(text);
})

document.addEventListener("turbolinks:load", function() {

    let userId = $('#user-id').val();
    let friendId = $('#friend-id').val();

    const scrollDownMessageList = function() {
      let dom = document.getElementById('messages-list');
      let scrollHeight = dom.scrollHeight;

      let $dom = $(dom);
      $dom.scrollTop(scrollHeight);

      if($dom.css('opacity') != '1') {
        $dom.fadeTo(500, 1);
      }
    }

    scrollDownMessageList();
    $('#id_text').focus();

    $('.recent-message-item').click(function() {
      let href = $(this).attr('href');
      Turbolinks.visit(href);
    });

    $('#message-text-form').submit(function(event) {
      event.preventDefault();
      let data = {
        sender: userId,
        receiver: friendId,
        text: $(this).find('#id_text').val()
      };
      console.log('sending...', data);
      api.postMessage(data)
      .done(function(data) {
        $('#messages-list').append($(data));
      }).fail(function(data) {

      });
    });

    const update = function() {
      let username = $('#friend-name').attr('data-friend-username');
      api.getNewMessage({ username: username }).done(function(data) {
         $('#messages-list').append($(data));
         scrollDownMessageList();
       }).fail(function(data) {
         console.log('fail', data);
       });
       setTimeout(update, 5000);
    };
    update();
    //setInterval(function(){ persist += 1; console.log(persist) }, 1000);
});
