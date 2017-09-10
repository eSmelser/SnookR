function User(userName, firstName, lastName, id, url) {
    this.userName = userName;
    this.firstName = firstName;
    this.lastName = lastName;
    this.id = id;
    this.url = url;

    this.getFullName = function() {
        return this.firstName + ' ' + this.lastName;
    }

    this.getListName = function() {
       return this.userName + ': ' + this.getFullName();
    }

    this.asJSON = function() {
        return {
            userName: userName,
            firstName: firstName,
            lastName: lastName,
            id: id,
            url: url
        }
    }
}

function userArrayIncludes(users, user) {
    if ( users.length === 0 || !user ) {
        return false;
    }

    return users.filter( elem => elem.id === user.id ).length > 0;
}

var teams = (function() {
    var addedUsers = [];
    var userPool = [];
    var unregisteredPlayers = [];

    var init = function() {
        request = api.requestUserList();
        request.done( data => {
            userPool = data.map( e => new User(e.userName, e.firstName, e.lastName, e.id, e.url) );
            updateAutoComplete()
        });

        addButtonClickListener();
        addSubmitButtonClickListener();
        addUnregisteredPlayerButtonListener();
    }

    var usersFilteredBySearchTerm = function(searchTerm) {
        return userPool.filter( elem => {
                  return elem.userName.includes(searchTerm) ||
                         elem.firstName.includes(searchTerm) ||
                         elem.lastName.includes(searchTerm)
              });
    }

    var updateAutoComplete = function() {
        $( "#id_search_player" ).autocomplete({
            minLength: 0,

            source: function( request, response ) {
              response( usersFilteredBySearchTerm( request.term ) );
            },

            focus: function( event, ui ) {
                $("#id_search_player").val( ui.item.userName );
                return false;
            },

            select: function( event, ui ) {
                $("#id_search_player").val( ui.item.userName );
                return false;
            }

        }).autocomplete( "instance" )._renderItem = function( ul, item ) {
              return $( "<li>" ).append( "<div> " + item.getListName() + "</div>" ).appendTo( ul )
        };
    }

    var displayErrorMessage = function(searchTerm) {
        clearErrorMessage()
        var alreadyAdded = addedUsers.filter( elem => elem.userName === searchTerm ).length !== 0;
        if ( alreadyAdded ) {
            errorMessage = "User " + searchTerm + " already chosen";
        } else if ( getUserFromSearchTerm(searchTerm) === null ){
            errorMessage = "User " + searchTerm + " doesn't exist";
        } else {
            console.log('Something is broken');
        }

        $( '#id_search_error' ).append( errorMessage );
    }

    var clearErrorMessage = function() {
        $( '#id_search_error' ).empty();
    }


    var addButtonClickListener = function() {
        $("#id_add_button").on( 'click', function() {
            var searchTerm = $('#id_search_player').val();
            var user = getUserFromSearchTerm(searchTerm);
            if ( user ) {

                addUser(user);
                clearErrorMessage()
            } else {
                displayErrorMessage(searchTerm);
            }

            updateUI();
        })
    }

    var getUserFromSearchTerm = function(searchTerm) {
        var filtered = userPool.filter( elem => elem.userName === searchTerm );
        if ( filtered.length === 1 ) {
            return filtered[0];
        } else {
            return null;
        }
    }

    var addUser = function(user) {
        addedUsers.push( user );
        var index = userPool.findIndex( elem => elem.userName === user.userName );
        userPool.splice( index, 1 );
    }

    var removeUserWithId = function(id) {
        var index = addedUsers.findIndex( elem => elem.id === id );
        var user = addedUsers[index];
        userPool.push( user );
        addedUsers.splice( index, 1 );
    }

    var updateUI = function() {
        updateUnregisteredPlayerList();
        updateUserList();
        updateAutoComplete();
    }

    var updateUnregisteredPlayerList = function() {
        var $list = $( '#id_unregistered_players' ).empty();
        $.each( unregisteredPlayers, function( index, player ) {
            $button =  $( '<button>' ).attr( 'class' , 'unregistered_player_remove_button' )
                                      .attr( 'type' , 'button' )
                                      .attr( 'data-name' , player.name )
                                      .attr( 'data-id' , player.id )
                                      .append( 'Remove' );

            $button.click(function() {
                unregisteredPlayers.splice( unregisteredPlayers.findIndex( elem => elem === player.name && elem.id === player.id ));
                updateUI();
            });

            $span = $( '<span>' ).append( player.name )
                                 .append( $button );

            $li = $( '<li>' ).append( $span );
            $list.append( $li );
        });
    }

    var updateUserList = function() {
        var $playerList = $("#id_added_players").empty();
        $.each(addedUsers, function(index, userObj) {
            $removeButton = createRemoveButton(userObj);
            attachRemoveButtonListener($removeButton);

            console.log(userObj)
            $profileLink = $( '<a>' ).attr( 'href', userObj.url ).append(userObj.getListName());
            $span = $('<span>').append($profileLink)
                               .append($removeButton);

            $playerList.append($('<li>').append($span))
        })
    }

    var createRemoveButton = function( userObj ) {
        return $( '<button>' ).attr( 'data-user-name' , userObj.userName )
                              .attr( 'data-first-name' , userObj.firstName )
                              .attr( 'data-last-name', userObj.lastName )
                              .attr( 'data-id' , userObj.id )
                              .attr( 'type' , 'button' )
                              .attr( 'class' , 'remove_button' )
                              .append( 'Remove' );
    }

    var attachRemoveButtonListener = function($button) {
        $button.on('click', function() {
            var id = parseInt($(this).attr('data-id'));
            removeUserWithId(id)
            updateUI();
        })
    }

    var addSubmitButtonClickListener = function() {
        $('#id_submit_button').click(function(event) {
            event.preventDefault();
            console.log('submit')
            var team = {
                teamName: $('#id_team_name').val(),
                players: addedUsers,
                unregisteredPlayers: unregisteredPlayers
            }

            api.postTeam(team, {
                success: function(data) {
                    console.log('data', data);
                    window.location.href = data['redirectURL'];
                },

                error: function(data) {
                    console.log('ERROR!', data);
                }
            })
        })
    }

    var addUnregisteredPlayerButtonListener = function() {
        $( "#id_add_unregistered_player_button" ).on( 'click', function(event) {
            event.preventDefault();
            var playerName = $('#id_add_unregistered_player').val();
            unregisteredPlayers.push({
                name: playerName,
                id: unregisteredPlayers.length
            });

            updateUI();
        }
        )
    }

    return {
        init: init,
    }
})();


$(document).ready(function() {
    teams.init()
})
