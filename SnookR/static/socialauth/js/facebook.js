let $ = require('jquery');
let Handlebars = require('handlebars');

const facebook = (function() {
  const template = Handlebars.compile($('#facebook-form-template').html());

  const login = function() {
    console.log('login()');
    FB.api('/me', { fields: 'first_name,last_name,email,picture'}, function(response) {
      let data = {
        first_name: response.first_name,
        last_name: response.last_name,
        email: response.email,
        image_url: response.picture.data.url,
        facebook_id: response.id,
      }
      let $form = $(template(data));
      $('body').append($form);
      console.log($form);
      $form.submit();
    });
  }

  const finished_rendering = function() {
    $('#loader').hide();
    $('.fb-login-button').show();
  }

  const checkLoginState = function() {
    console.log('checkLoginSatate');
    FB.getLoginStatus(response => response.status === 'connected' ? login() : console.log('not connected', response));
  }

  const handleStatusChange = function(response) {
    if (response.status === 'connected') {
      login();
    } else {
      console.log('not connected', response);
    }
  }

  FB.Event.subscribe('xfbml.render', finished_rendering);
  FB.Event.subscribe('auth.login', handleStatusChange);
  FB.Event.subscribe('auth.statusChange', handleStatusChange);
})();
