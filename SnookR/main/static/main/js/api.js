// This module defines the JS API for SnookR

var api = (function() {
    /***** AJAX Setup *****/
    var getCookie = function(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var csrftoken = getCookie('csrftoken');

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    var csrfSafeMethod = function(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    /**** SnookR API ****/

    // Returns an AJAX request for the list of all users
    //
    //   Usage:
    //       // Log all users to console
    //       request = api.requestUserList()
    //       request.done(function(data) {
    //           for (var i=0; i<data.length; i++) {
    //               console.log(data[i])
    //           }
    //       })
    var requestUserList = function() {
        return $.ajax({
            dataType: 'json',
            url: '/api/users/',
            data: {}
        });
    }

    // Return public methods for API
    return {
        requestUserList: requestUserList
    }
})()
