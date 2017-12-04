function User(userName, firstName, lastName, id, url) {
    this.userName = userName;
    this.firstName = firstName;
    this.lastName = lastName;
    this.id = id;
    this.url = url;

    this.getFullName = function () {
        return this.firstName + ' ' + this.lastName;
    };

    this.getListName = function () {
        return this.userName + ': ' + this.getFullName();
    };

    this.asJSON = function () {
        return {
            username: this.userName,
            first_name: this.firstName,
            last_name: this.lastName,
            id: this.id,
            url: this.url
        }
    }
}

function userArrayIncludes(users, user) {
    if (users.length === 0 || !user) {
        return false;
    }

    return users.filter(elem => elem.id === user.id).length > 0;
}

var teams = (function () {
    var loggedInUser = null;
    var addedUsers = [];
    var userPool = [];
    var unregisteredPlayers = [];

    var init = function () {
        request = api.getUserList();
        request.done(data => {
            console.log(data);
            userPool = data.map(e => new User(e.username, e.first_name, e.last_name, e.id, e.url));
            updateAutoComplete()
        });

        request = api.getLoggedInUser();
        request.done(function (data) {
            loggedInUser = new User(data.username, data.first_name, data.last_name, data.id, data.url);
        });
        request.fail(data => {
            console.log('getLoggedInUser failed');
        });
        addButtonClickListener();
        addSubmitButtonClickListener();
        addUnregisteredPlayerButtonListener();
    };

    const usersFilteredBySearchTerm = function (searchTerm) {
        return userPool.filter(elem => {
            return elem.userName.includes(searchTerm) ||
                elem.firstName.includes(searchTerm) ||
                elem.lastName.includes(searchTerm)
        });
    };

    const updateAutoComplete = function () {
        $("#id_search_player").autocomplete({
            minLength: 0,

            source: function (request, response) {
                response(usersFilteredBySearchTerm(request.term));
            },

            focus: function (event, ui) {
                $("#id_search_player").val(ui.item.userName);
                return false;
            },

            select: function (event, ui) {
                $("#id_search_player").val(ui.item.userName);
                return false;
            }

        }).autocomplete("instance")._renderItem = function (ul, item) {
            return $("<li>").append("<div> " + item.getListName() + "</div>").appendTo(ul)
        };
    };

    const displayErrorMessage = function (searchTerm) {
        clearErrorMessage();
        const alreadyAdded = addedUsers.filter(elem => elem.userName === searchTerm).length !== 0;
        let errorMessage;
        if (alreadyAdded) {
            errorMessage = "User " + searchTerm + " already chosen";
        } else if (getUserFromSearchTerm(searchTerm) === null) {
            errorMessage = "User " + searchTerm + " doesn't exist";
        } else {
            console.log('Something is broken');
        }

        $('#id_search_error').append(errorMessage);
    };

    const clearErrorMessage = function () {
        $('#id_search_error').empty();
    };


    const addButtonClickListener = function () {
        $("#id_add_button").on('click', function () {
            var searchTerm = $('#id_search_player').val();
            var user = getUserFromSearchTerm(searchTerm);
            if (user) {
                addUser(user);
                clearErrorMessage()
            } else {
                displayErrorMessage(searchTerm);
            }

            updateUI();
        })
    };

    const getUserFromSearchTerm = function (searchTerm) {
        const filtered = userPool.filter(elem => elem.userName === searchTerm);
        if (filtered.length === 1) {
            return filtered[0];
        } else {
            return null;
        }
    };

    const addUser = function (user) {
        addedUsers.push(user);
        const index = userPool.findIndex(elem => elem.userName === user.userName);
        userPool.splice(index, 1);
    };

    const removeUserWithId = function (id) {
        const index = addedUsers.findIndex(elem => elem.id === id);
        const user = addedUsers[index];
        userPool.push(user);
        addedUsers.splice(index, 1);
    };

    var updateUI = function () {
        updateUnregisteredPlayerList();
        updateUserList();
        updateAutoComplete();
    };

    var updateUnregisteredPlayerList = function () {
        var $list = $('#id_unregistered_players').empty();
        $.each(unregisteredPlayers, function (index, player) {
            $button = $('<button>').attr('class', 'unregistered_player_remove_button')
                .attr('type', 'button')
                .attr('data-name', player.name)
                .attr('data-id', player.id)
                .append('Remove');

            $button.click(function () {
                unregisteredPlayers.splice(unregisteredPlayers.findIndex(elem => elem === player.name && elem.id === player.id));
                updateUI();
            });

            $span = $('<span>').append(player.name)
                .append($button);

            $li = $('<li>').append($span);
            $list.append($li);
        });
    };

    var updateUserList = function () {
        var $playerList = $("#id_added_players").empty();
        $.each(addedUsers, function (index, userObj) {
            $removeButton = createRemoveButton(userObj);
            attachRemoveButtonListener($removeButton);

            console.log(userObj)
            $profileLink = $('<a>').attr('href', userObj.url).append(userObj.getListName());
            $span = $('<span>').append($profileLink)
                .append($removeButton);

            $playerList.append($('<li>').append($span))
        })
    };

    var createRemoveButton = function (userObj) {
        return $('<button>').attr('data-user-name', userObj.userName)
            .attr('data-first-name', userObj.firstName)
            .attr('data-last-name', userObj.lastName)
            .attr('data-id', userObj.id)
            .attr('type', 'button')
            .attr('class', 'remove_button')
            .append('Remove');
    };

    var attachRemoveButtonListener = function ($button) {
        $button.on('click', function () {
            var id = parseInt($(this).attr('data-id'));
            removeUserWithId(id);
            updateUI();
        })
    };

    var addSubmitButtonClickListener = function () {
        $('#id_submit_button').click(function (event) {
            event.preventDefault();
            console.log('submit');
            var team = {
                team_captain: loggedInUser.asJSON(),
                name: $('#id_team_name').val(),
                players: addedUsers.map(p => p.asJSON()),
//                unregisteredPlayers: unregisteredPlayers
            };

            console.log('TEAM', team);

            var request = api.postTeam(team);
            request.done(function (data) {
                var invites = addedUsers.map(p => {
                    var inviteRequest = api.postInvitation({
                        team: data,
                        invitee: p.asJSON()
                    }).done(data => console.log('done:', data))
                        .fail(data => console.log('fail:', data))
                });

                // Redirect to url
                window.location.href = $('#id_submit_button').attr('data-redirect-url');
            }).fail(function (data) {
                console.log('ERROR!', data);
            })
        })
    };

    var addUnregisteredPlayerButtonListener = function () {
        $("#id_add_unregistered_player_button").on('click', function (event) {
                event.preventDefault();
                var playerName = $('#id_add_unregistered_player').val();
                unregisteredPlayers.push({
                    name: playerName,
                    id: unregisteredPlayers.length
                });

                updateUI();
            }
        )
    };

    return {
        init: init,
    }
})();


$(document).ready(function () {
    console.log('here');
    teams.init()
});
