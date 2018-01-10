
const createHiddenInput = function(name, val) {
    return $('<input>', {'type': 'hidden', 'name': name, 'value': val})
}
      gapi.load('auth2', function () {
        var auth2;

        auth2 = gapi.auth2.init({
          client_id: context.SOCIAL_AUTH_GOOGLE_PLUS_KEY,
        });

        auth2.then(function () {
          var button = document.getElementById("google-plus-button");
          console.log("User is signed-in in Google+ platform?", auth2.isSignedIn.get() ? "Yes" : "No");

          auth2.attachClickHandler(button, {}, function (googleUser) {
            // Send access-token to backend to finish the authenticate
            // with your application

            var authResponse = googleUser.getAuthResponse();
            var $form;
            var $input;

            $form = $("<form>");
            $form.attr("action", "/social-auth/google-plus/");
            $form.attr("method", "post");
            $input = $("<input>");
            $input.attr("name", "id_token");
            $input.attr("value", authResponse.id_token);
            $form.append($input);
            $form.append($('input[name="csrfmiddlewaretoken"]'));
            if (auth2.isSignedIn.get()) {
                var profile = auth2.currentUser.get().getBasicProfile();
                $form.append(createHiddenInput('firstname', profile.getGivenName()));
                $form.append(createHiddenInput('id', profile.getId()));
                $form.append(createHiddenInput('lastname', profile.getFamilyName()));
                $form.append(createHiddenInput('imageUrl', profile.getImageUrl()))
                $form.append(createHiddenInput('email', profile.getEmail()))
                console.log('ID: ' + profile.getId());
                console.log('Full Name: ' + profile.getName());
                console.log('Given Name: ' + profile.getGivenName());
                console.log('Family Name: ' + profile.getFamilyName());
                console.log('Image URL: ' + profile.getImageUrl());
                console.log('Email: ' + profile.getEmail());
            }
            $(document.body).append($form);
            $form.submit();



          });
        });
      });
