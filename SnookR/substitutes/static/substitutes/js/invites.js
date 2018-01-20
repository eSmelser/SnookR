var Invitation = function(team, invitee, status, id) {
    this.team = team;
    this.invitee = invitee;
    this.status = status;
    this.id = id;
    this.observers = [];

    this.addObserver = function(observer) {
        this.observers.push(observer)
    }

    this.notifyAll = function() {
        for (var i=0; i<this.observers.length; i++) {
            this.observers[i].update();
        }
    }

    this.getHTMLId = function() {
        return '#id_invite_' + this.id;
    }
}

var InvitationView = function(controller, parentView) {
    this.model = controller.model;
    this.controller = controller;
    this.parentView = parentView;

    this.getIDPrefix = function() {
        var idPrefix;
        var id = this.model.id;
        if (this.model.status === 'Pending') {
            idPrefix = 'id_pending_invite_' + id;
        } else if (this.model.status === 'Accepted') {
            idPrefix = 'id_accepted_invite_' + id;
        } else {
            idPrefix = 'id_declined_invite_' + id;
        }

        return idPrefix;
    }

    this.getDOM = function() {
        var idAttr = this.model.getHTMLId();
        $li = $( '<li>' ).attr( 'id' ,  this.getIDPrefix() )
                 .append( 'Team: ' )
                 .append( this.getTeamDOM() )
                 .append( '  Captain: ' )
                 .append( this.getCaptainDOM() )
                 .append( '  Status: ' )
                 .append( this.getStatusDOM() );

        if ( this.model.status === 'Pending' ) {
            $li.append( this.getAcceptButtonDOM() );
            $li.append( this.getDeclineButtonDOM() );
        }

        return $li;
    }

    this.update = function() {
        this.parentView.updateWithChild(this)
    }

    this.getAcceptButtonDOM = function() {
        return $( '<button>' )
                    .attr( 'id', 'id_accept_button_' + this.model.id )
                    .attr( 'class', 'accept_button')
                    .attr( 'value', 'accept' )
                    .attr( 'data-id', + this.model.id )
                    .append( 'Accept' );
    }

    this.getDeclineButtonDOM = function() {
        return $( '<button>' )
                    .attr( 'id', 'id_decline_button_' + this.model.id )
                    .attr( 'class', 'decline_button')
                    .attr( 'value', 'decline' )
                    .attr( 'data-id', + this.model.id )
                    .append( 'decline' );
    }

    this.getStatusDOM = function() {
        return $( '<span>' ).attr( 'id' , this.getIDPrefix() + '_status').append( this.model.status );
    }

    this.getCaptainDOM = function() {
        return $( '<span>' ).attr( 'id' , this.getIDPrefix() + '_captain').append( this.model.team.captain.username );
    }


    this.getTeamDOM = function() {
        return $( '<span>' ).attr( 'id' , this.getIDPrefix() + '_team' ).append( this.model.team.name );
    }
}

var InvitationListView = function(controller) {
    this.model = controller.model;
    this.controller = controller;
    this.model.addObserver(this);
    this.childView = new InvitationView(controller, this);


    this.update = function() {
        var id = this.model.getHTMLId();
        $( id ).remove();


        var $inviteList;
        if (this.model.status == 'Pending') {
            $inviteList = $( '#id_pending_invites_list' );
        } else if (this.model.status == 'Accepted') {
            $inviteList = $( '#id_accepted_invites_list' );
        } else {
            $inviteList = $( '#id_declined_invites_list' );
        }


        $inviteDOM = this.childView.getDOM();
        $inviteList.append($inviteDOM);

    }

    this.updateWithChild = function(childView) {
        this.childView = childView;
        this.update();
    }
}


var InvitationController = function(model) {
    this.model = model;

    var self = this;

    $( '#id_accept_button_' + self.model.id ).click(function(event) {
        event.preventDefault();
        api.patchInvitation({
            status: 'A',
            id: self.model.id
        }).done( (data) => {
        console.log('patch done')
            self.model.status = 'Accepted';
            self.model.notifyAll();
        }).fail( (data) => {
            console.log('patchInvitation() failed:', data);
        })
    })

    $( '#id_decline_button_' + self.model.id ).click(function(event) {
        event.preventDefault();
        api.patchInvitation({
            status: 'D',
            id: self.model.id
        }).done( (data) => {
            self.model.status = 'Declined';
            self.model.notifyAll();
        }).fail( (data) => {
            console.log('patchInvitation() failed:', data);
        })
    })

}

var main = function() {
    var request = api.getInvitationList();
    request.done(function(data) {
        var invites = data.map( item => new Invitation(item.team, item.invitee, item.status, item.id) );
        for (var i=0; i<invites.length; i++) {
            var controller = new InvitationController(invites[i]);
            var invitationListView = new InvitationListView(controller);
            var invitationView = new InvitationView(controller, invitationListView);
        }
    })
}

main();