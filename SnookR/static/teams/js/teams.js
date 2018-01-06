/**
 * Created by bobby on 12/29/17.
 */

let api = require('../../api/js/api');
let Handlebars = require('handlebars');

(function () {
    let team = {
        init: function () {
            this.clientCache = {};
            this.userPanelTemplate = Handlebars.compile($('#user-panel-template').html());
            this.userPanelDomCache = {};
            this.teamCreatorSelected = false;
            this.searchResults = [];
            this.addedPlayers = [];
            this.unregisteredPlayers = [];
            this.cacheDom();
            this.selectedTeamId = this.initSelectedTeam();
            this.bindEvents();
            this.render();
        },

        cacheDom: function () {
            this.$teamItemElementsDiv = $("#team-item-elements");
            this.$newTeamButton = $('#new-team-button');
            this.$teamCreatorDiv = $('#team-creator-div');
            this.$teamPlayersDiv = $('#players-div');
            this.$searchInput = $('#input-search');
            this.$loader = $('#player-loader');
            this.$searchResultsDiv = $('#search-results');
            this.$addedPlayersDiv = $('#added-players');
            this.$form = $('#team-form');
        },

        bindEvents: function () {
            this.$searchInput
                .on('keyup', this.searchPlayers.bind(this));
            this.$teamItemElementsDiv
                .on('click', '.team-item', {self: this}, this.selectTeam)
                .on('click', '.team-item', this.showTeamPlayersDiv.bind(this));
            this.$newTeamButton
                .click(this.selectTeamCreator.bind(this))
                .click(this.activateTeamCreator.bind(this))
                .click(this.hideTeamPlayersDiv.bind(this));
            this.$searchResultsDiv
                .on('click', '.panel-body', {self: this}, this.addPlayer)
                .on('mouseenter', '.panel-body', this.activatePanelMouseOver)
                .on('mouseleave', '.panel-body', this.activatePanelMouseOff);
            this.$addedPlayersDiv
                .on('mouseenter', '.panel-body', this.activatePanelMouseOver)
                .on('mouseleave', '.panel-body', this.activatePanelMouseOff)
                .on('click', '.panel-body', {self: this}, this.removePlayer);
            this.$form.find('#submit')
                .click(this.validateForm.bind(this))
                .click(this.addAddedPlayersToForm.bind(this));
            this.$form.find('#unregistered-player-add-button')
                .click(this.addUnregisteredPlayer.bind(this))
        },

        addUnregisteredPlayer: function() {
          let val = this.$form.find('#unregistered-player-text-input').val();
          this.unregisteredPlayers.push(val);
          this.render();
        },

        validateForm: function () {
            let valid = true;

            // Validate name field
            let $name = this.$form.find('#team-name');
            if ($name.val().length <= 0) {
                this.$form.find('#team-name').css('border-color', 'red');
                valid = false;
            }

            // Validate players field
            if (this.addedPlayers.length <= 0 && this.unregisteredPlayers.length <= 0) {
                let $warning = $('<strong>').css('color', 'red').append('No players selected!');
                this.$addedPlayersDiv.empty().append($warning);
                valid = false;
            }

            return valid;
        },

        searchPlayers: function () {
            this.$loader.show();
            let searchTerm = this.$searchInput.val();
            if (searchTerm) {
                this.searchForTerm(searchTerm);
            } else {
                this.searchResults = [];
            }

            self.render();
        },

        searchForTerm: function (term) {
            if (term in this.clientCache) {
                this.searchResults = this.clientCache[term];
            } else {
                self = this;
                this.$loader.show();
                api.searchForUser({query: term}).done(function (data) {
                    data = data.filter(player => !(player.id in self.addedPlayers));
                    self.clientCache[term] = data;
                    self.searchResults = data;
                    self.render();
                }).fail(function (data) {
                    console.log('err!', data);
                })
            }
        },

        initSelectedTeam: function () {
            // The first selected team is fromt he top-most .team-item element.
            let id = this.$teamItemElementsDiv
                .find('.team-item')
                .first()
                .attr('data-team-id');

            this.selectedTeamId = parseInt(id);
            return this.selectedTeamId;
        },

        selectTeamCreator: function () {
            this.teamCreatorSelected = true;
            this.render();
        },

        selectTeam: function (event) {
            let self = event.data.self;
            let id = $(this).attr('data-team-id');
            self.selectedTeamId = parseInt(id);
            self.teamCreatorSelected = false;
            self.render();
        },

        render: function () {
            let selector = `.team-item[data-team-id=${this.selectedTeamId}]`;
            this.$teamItemElementsDiv.find(selector).addClass('active');
            this.hideUnselectedPlayerGroups();
            this.showSelectedPlayerGroup();
            this.deactiveUnselectedTeams();
            this.activateSelectedTeam();

            if (this.teamCreatorSelected) {
                this.deactivateAllTeams();
                this.hideTeamPlayersDiv();
                this.showTeamCreator();
                this.activateTeamCreator();
                this.renderSearchResultsDiv();
                this.renderAddedPlayersDiv();
                this.renderUnregisteredPlayersList();
            } else {
                this.hideTeamCreator();
                this.showTeamPlayersDiv();
                this.deactivateTeamCreator();
            }
        },

        renderUnregisteredPlayersList: function() {
          let $dom = this.$form.find('#unregistered-players-list').empty();
          this.unregisteredPlayers.map( p => {
            let $li = $('<li>').append(p);
            let $input = $(`<input type="hidden" name="unregistered-player" value=${p}>`)
            $dom.append($li);
            $dom.append($input);
          });
        },

        addAddedPlayersToForm: function () {
            this.$form.append(this.addedPlayers.map( p => `<input type="hidden" value="${p.id}" name="player">`))
        },

        activatePanelMouseOver: function () {
            $(this)
                .css('background-color', '#f5f5f5')
                .css('cursor', 'pointer');
        },

        activatePanelMouseOff: function () {
            $(this)
                .css('background-color', '#ffffff')
                .css('cursor', 'auto');
        },

        getUserPanelDom: function (user) {
            if (user.id in this.userPanelDomCache) {
                return this.userPanelDomCache[user.id];
            } else {
                let html = this.userPanelTemplate(user);
                this.userPanelDomCache[user.id] = $(html);
                return this.userPanelDomCache[user.id];
            }
        },

        renderSearchResultsDiv: function () {
            this.$searchResultsDiv.empty();
            this.searchResults.map(user => {
                let $dom = this.getUserPanelDom(user);
                this.$searchResultsDiv.append($dom);
            });
        },

        renderAddedPlayersDiv: function () {
            this.$addedPlayersDiv.empty();
            this.addedPlayers.map(user => {
                let $dom = this.getUserPanelDom(user);
                this.$addedPlayersDiv.append($dom)
            });
        },

        activateSelectedTeam: function (event) {
            let selector = this.getTeamItemSelector();
            this.$teamItemElementsDiv.find(selector).addClass('active');
        },

        showSelectedPlayerGroup: function () {
            let selector = this.getPlayerGroupSelector();
            this.$teamPlayersDiv.find(selector).show();
            this.$teamPlayersDiv.find(selector).show();
        },

        hideUnselectedPlayerGroups: function () {
            let selector = this.getPlayerGroupSelector();
            this.$teamPlayersDiv.find('.player-group').not(selector).hide();
        },

        activateTeamCreator: function () {
            this.$newTeamButton.addClass('active')
        },

        deactivateTeamCreator: function () {
            this.$newTeamButton.removeClass('active')
        },

        deactiveUnselectedTeams: function () {
            this.$teamItemElementsDiv
                .find('.team-item')
                .not(this.getTeamItemSelector())
                .removeClass('active');
        },

        deactivateAllTeams: function () {
            this.$teamItemElementsDiv
                .find('.team-item')
                .removeClass('active');
        },

        showTeamCreator: function () {
            this.$teamCreatorDiv.show();
        },

        hideTeamCreator: function () {
            this.$teamCreatorDiv.hide();
        },

        showTeamPlayersDiv: function () {
            this.$teamPlayersDiv.show();
        },

        hideTeamPlayersDiv: function () {
            this.$teamPlayersDiv.hide();
        },

        getTeamItemSelector: function () {
            return `.team-item[data-team-id=${this.selectedTeamId}]`;
        }
        ,

        getPlayerGroupSelector: function () {
            return `.player-group-${this.selectedTeamId}`;
        },

        addPlayer: function (event) {
            let self = event.data.self;
            let id = parseInt($(this).attr('data-user-id'));
            let index = self.searchResults.findIndex(user => user.id === id);
            let user = self.searchResults[index];
            self.searchResults.splice(index, 1);
            self.addedPlayers.push(user);
            self.render();
        },

        removePlayer: function (event) {
            let self = event.data.self;
            let id = parseInt($(this).attr('data-user-id'));
            let index = self.addedPlayers.findIndex(user => user.id === id);
            let user = self.addedPlayers[index];
            self.addedPlayers.splice(index, 1);
            self.searchResults.push(user);
            self.render();
        }
    };

    $(document).ready(function() {
        team.init();
    });
})();
