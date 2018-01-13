const facebook = (function() {
  // This is called with the results from from FB.getLoginStatus().
  const statusChangeCallback = function(response) {
    console.log('statusChangeCallback');
    console.log(response);
    // The response object is returned with a status field that lets the
    // app know the current login status of the person.
    // Full docs on the response object can be found in the documentation
    // for FB.getLoginStatus().
    if (response.status === 'connected') {
      // Logged into your app and Facebook.
      testAPI();
    } else {
      // The person is not logged into your app or we are unable to tell.
      console.log('not connected');
      console.log(' not connected', response);
    }
  }

  /*const init = function() {
    // Load the SDK asynchronously
    (function(d, s, id) {
      var js, fjs = d.getElementsByTagName(s)[0];
      if (d.getElementById(id)) return;
      js = d.createElement(s);
      js.id = id;
      js.src = 'https://connect.facebook.net/en_US/sdk.js#xfbml=1&version=v2.11&appId=500234237042833';
      fjs.parentNode.insertBefore(js, fjs);
    }(document, 'script', 'facebook-jssdk'));
  }*/

  // Here we run a very simple test of the Graph API after login is
  // successful.  See statusChangeCallback() for when this call is made.
  const testAPI = function() {
    console.log('Welcome!  Fetching your information.... ');
    FB.api('/me', { fields: 'first_name,last_name,email,picture'}, function(response) {
      console.log('response:', response);
    });
  }



    // This function is called when someone finishes with the Login
    // Button.  See the onlogin handler attached to it in the sample
    // code below.
    const checkLoginState = function() {
      console.log('checkLoginState');
      FB.getLoginStatus(function(response) {
        statusChangeCallback(response);
      });
    }

    const myFunc = () => console.log('myFunc');
    FB.Event.subscribe('auth.login', checkLoginState);
    FB.Event.subscribe('auth.login', myFunc);
})();
