// This module defines the JS API for SnookR

const api = (function () {
    /***** AJAX Setup *****/

    const baseURL = 'http://127.0.0.1:8000';

    const getCookie = function (name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            let cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                let cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    };

    const csrftoken = getCookie('csrftoken');

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        contentType: 'application/json'
    });

    const csrfSafeMethod = function (method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    };

    /**** SnookR API ****/

    /* getUserList(): Returns an AJAX request for the list of all users
     *
     *
     * Arguments:
     *     data: JSON file for filtering on the User model
     *           Fields username, last_name, and first_name can be filtered
     *           on using icontains, contains, and exact equalities.
     *
     *           For example, with a user named MyUser in the database queries with the following
     *           data would return MyUser:
     *
     *           { 'username': 'MyUser' }           // exact match
     *
     *           { 'username__contains': 'yUser' }   // case-sensitive contains
     *
     *           { 'username__icontains': 'yuser' }  // case-insensitive contains
     *
     *
     *
     * Usage:
     *       // Log all users to console
     *       request = api.requestUserList()
     *       request.done(function(data) {
     *           for (var i=0; i<data.length; i++) {
     *               console.log(data[i])
     *           }
     *       })
     */
    const getUserList = function (data) {
        return $.ajax({
            dataType: 'json',
            url: '/api/users/',
            data: JSON.stringify(data)
        });
    };
    /* postTeam() : Returns a POST request for creating a Team.
     *
     * Arguments:
     *     data: An object describing the team to be created.
     *           Required fields: name, team_captain.
     *           Optional fields: players
     *
     * Permisions: User must have the 'substitutes.add_team' permission to POST a team.
     *
     * Example data arg:
     *       {
     *           'name': MyTeam,
     *           'team_captain': {
     *              'username': 'evan'
     *            },
     *           'players': [
     *               {'username': 'joe'},
     *               {'username': 'john'}
     *           ]
     *       }
     */
    const postTeam = function (data) {
        return $.post({
            dataType: 'json',
            url: '/api/team/',
            data: JSON.stringify(data),
        });
    };
    /* getInvitationList(): Returns a response object containing a list of invitations.
     *
     * Arguments:
     *    data: object
     *          The query parameters for filtering invitations.
     *          Should take the form:
     *                  {
     *                    'invitee': {  // user fields (see getUserList comments) // },
     *                    'team': { // team fields (see postTeam()) // },
     *                    'id': integer,
     *                    'status': 'P' (pending) or 'D' (declined) or 'A' (accepted)
     *
     *
     * Example:
     *
     *     // Print out every pending invite for joe
     *     getInvitationList({
     *         'invitee': {'username': 'joe'},
     *         'status': 'P'
     *     }).done(function(data) {
     *         for (var i=0; i<data.length; i++) {
     *            console.log(data[i]);
     *         }
     *     })
     *
     *
     */
    const getInvitationList = function (data) {
        return $.get({
            dataType: 'json',
            url: '/api/invites/',
            data: JSON.stringify(data),
        });
    };
    /* getLoggedInUser(): Returns a request with the data for the currently logged in user
     *
     * Arguments: None
     */
    const getLoggedInUser = function () {
        return $.get({
            dataType: 'json',
            url: '/api/auth/user',
            data: {},
        })
    };

    /* postInvitation(data): Returns a request for POSTing a single invite
     *f
     */
    const postInvitation = function (data) {
        return $.post({
            dataType: 'json',
            url: '/api/invites/',
            data: JSON.stringify(data)
        })
    };
    /* patchInvitation(data): Returns a request for POSTing a single invite
     *
     */
    const patchInvitation = function (data) {
        return $.ajax({
            type: 'PATCH',
            dataType: 'json',
            url: '/api/invites/' + data.id + '/',
            data: JSON.stringify(data)
        })
    };

    const getSessionList = function (data) {
        return $.get({
            dataType: 'json',
            url: '/api/sessions',
            data: JSON.stringify(data),
        });
    };

    const getSubList = function (data) {
        return $.get({
            dataType: 'json',
            url: '/api/subs',
            data: JSON.stringify(data),
        })
    };

    const getSessionEventList = function (data) {
        return $.get({
            dataType: 'json',
            url: '/api/session-events/',
            data: JSON.stringify(data),
        });
    };

    // Search for a user using a term search string
    const searchForUser = function(data) {
        return $.get({
            dataType: 'json',
            url: '/api/search-user/',
            data: JSON.stringify(data),
        });
    };

    const getSessionEventInviteList = function(data) {
        return $.get({
            dataType: 'json',
            url: '/api/session-event-invites/',
            data: JSON.stringify(data),
        })
    };

    const getSessionEventInvite = function(id) {
        return $.get({
            dataType: 'json',
            url: '/api/session-event-invites/' + id,
        })
    };

    const postSessionEventInvite = function(data) {
        return $.post({
            dataType: 'json',
            url: '/api/session-event-invites/',
            data: JSON.stringify(data),
        })
    };

    // Return public methods for API
    return {
        baseURL,
        getUserList,
        postTeam,
        getInvitationList,
        getLoggedInUser,
        postInvitation,
        patchInvitation,
        getSessionList,
        getSessionEventList,
        getSubList,
        searchForUser,
        getSessionEventInviteList,
        getSessionEventInvite,
        postSessionEventInvite
    }
})();

module.exports = api;