$(document).ready(function() {
    var teams = (function() {
        var users = [];
        var name = null;

        var init = function() {
            request = api.requestUserList();
            request.done(function(data) {
                users = data;
                populateAutoComplete(data)
            });
            addButtonClickListener();
        };

        var populateAutoComplete = function(data) {
            $( "#id_search_player" ).autocomplete({
                source: data
            });
        }

        var addButtonClickListener = function() {
            $("#id_add_button").on('click', function() {
                name = getSearchName();

                // If name is still in the users list then pop it off and add it to
                // the displayed <ul>.  This is to check that the user hasn't
                // just been added (and therefore would no longer be in the list).
                if (users.includes(name)) {
                    $removeButton = createRemoveButton();
                    attachRemoveButtonListener($removeButton);
                    $userElem = createUserSpan($removeButton);
                    addUserToList($userElem);
                }
            })
        }

        var getSearchName = function() {
            return $("#id_search_player").val();
        }

        var createRemoveButton = function() {
            return $('<button>').attr('data-name', name)
                                                 .attr('type', 'button')
                                                 .attr('class', 'remove_button')
                                                 .append('Remove');
        }

        var attachRemoveButtonListener = function($button) {
            $button.on('click', function() {
                var removeName = $(this).attr('data-name');
                // Add the name back onto the users list
                users.push(removeName);

                // Remove this button's containing <li> and <span>
                $(this).parent()
                       .parent()
                       .remove();
            })
        }

        var createUserSpan = function($button) {
            return $('<span>').append(name)
                              .append($button);
        }

        var addUserToList = function($user) {
            $("#id_added_players").append($('<li>').append($user))
                var index = users.findIndex((elem) => elem == name);
                users.splice(index, 1);
            }

        return {
            init: init
        }
    })();

    teams.init()
})
