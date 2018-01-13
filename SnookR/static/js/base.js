(function() {
    /*
     * If the user clicks 'Logout', sign them out of Facebook too.
     */
    $("#id_logout_link").click(function(event) {
        event.preventDefault();
        FB.getLoginStatus(resp => {
            if (resp.status !== 'unknown') {
                FB.logout();
            };

            window.location.href = $(this).attr('href');
        });
     });
 })();