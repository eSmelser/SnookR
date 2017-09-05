var teams = (function() {
    var users = [];
    var name = null;
    var userName = null;
    var firstName = null;
    var lastName = null;
    var chosenUsers = [];
    var userPool = [];
    var user = null;

    var init = function() {
        request = api.requestUserList();
        request.done( data => {
            userPool = data;
            updateAutoComplete()
        });

        addButtonClickListener();
    }

    var getFullName = function(user) {
        return user.firstName + ' ' + user.lastName;
    }

    var getListName = function(user) {
       return user.userName + ': ' + getFullName(user);
    }

    var updateAutoComplete = function() {
        $( "#id_search_player" ).autocomplete({
            minLength: 0,

            source: function( request, response ) {
              var matchingUsers = userPool.filter( elem => {
                  return elem.userName.includes(request.term) ||
                         elem.firstName.includes(request.term) ||
                         elem.lastName.includes(request.term)
              });

              response( matchingUsers );
            },

            focus: function( event, ui ) {
                $("#id_search_player").val( getListName(ui.item) );
                return false;
            },

            select: function( event, ui ) {
                user = ui.item;
                return false;
            }

        }).autocomplete( "instance" )._renderItem = function( ul, item ) {
              return $( "<li>" ).append( "<div> " + getListName(item) + "</div>" ).appendTo( ul )
        };
    }

    var addButtonClickListener = function() {
        $("#id_add_button").on('click', function() {
            if (user != null && arrayIncludes(userPool, user) && !arrayIncludes(chosenUsers, user)) {
                chosenUsers.push( user );
                var index = userPool.findIndex( elem => elem.userName === user.userName );
                userPool.splice( index, 1 );
                user = null;
            }
            updateUserList();
            updateAutoComplete();
        })
    }

    var createRemoveButton = function(userObj) {
        return $('<button>').attr('data-user-name', userObj.userName)
                            .attr('data-first-name', userObj.firstName)
                            .attr('data-last-name', userObj.lastName)
                            .attr('data-id', userObj.id)
                            .attr('type', 'button')
                            .attr('class', 'remove_button')
                            .append('Remove');
    }

    var attachRemoveButtonListener = function($button) {
        $button.on('click', function() {
            var removeId = $(this).attr('data-id');
            // Add the name back onto the users list and remove from chosenUsers
            userPool.push();
            var index = chosenUsers.findIndex( elem => elem.id === parseInt(removeId) );
            userPool.push(chosenUsers[index]);
            chosenUsers.splice( index, 1 );
            updateUserList();
            updateAutoComplete();
        })
    }

    var updateUserList = function() {
        var $playerList = $("#id_added_players").empty();
        $.each(chosenUsers, function(index, userObj) {
            $removeButton = createRemoveButton(userObj);
            attachRemoveButtonListener($removeButton);
            $span = $('<span>').append(getListName(userObj))
                               .append($removeButton);
            $playerList.append($('<li>').append($span))
        })
    }

    return {
        init: init,
    }
})();


$(document).ready(function() {
    teams.init()
})
