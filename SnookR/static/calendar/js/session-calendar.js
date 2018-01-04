/**
 * Created by bobby on 12/16/17.
 */

let $ = require('jquery');
require('moment');
require('fullcalendar');
let api = require('../../api/js/api.js');
let Sub = require('./sub');
let User = require('../../accounts/js/user');


let substitutes = {
    init: function () {
        this.currentUser = new User(context.currentUser);
        this.currentSessionEvent = context.initialSessionEvent;
        this.sessionEvents = context.initialSessionEvents;
        this.sessionName = context.sessionName;
        this.currentUserPreviousInvites = context.currentUserPreviousInvites;
        this.subs = context.initialSubArray.map(sub => this.getSub(sub));
        this.currentUserSub = this.getCurrentUserSub();
        this.cacheDom();
        this.render();
        this.bindEvents();
    },

    cacheDom: function () {
        this.$rightColumn = $('#right-column');
        this.$subList = this.$rightColumn.find('#sub-list');
        this.$calendar = $('#calendar');
        this.$sessionName = this.$rightColumn.find('.session-name');
        this.$sessionDate = this.$rightColumn.find('.session-date');
        this.$currentUserPanel = this.$rightColumn.find('#current-user-panel');
        this.$currentUserHeader = this.$rightColumn.find('#current-user-header');
        this.$currentUserRegisterButton = this.$rightColumn.find('#current-user-register-button');
        this.$subListHeader = this.$rightColumn.find('#sub-list-header');
        this.$dateHeader = this.$rightColumn.find('#date-header');
    },

    bindEvents: function () {
        this.$currentUserRegisterButton.click(this.registerCurrentUser.bind(this));
    },

    registerCurrentUser: function() {
        self = this;
        api.postSub({
          session_event: { id: this.currentSessionEvent.id },
          user: { username: this.currentUser.username },
        }).done(function(data) {
          self.subs.push(self.getSub(data));
          self.currentUserSub = self.getCurrentUserSub();
          self.render()
        }).fail(function(data) {
          console.log('registerCurrentUser failed:', data);
        });
    },

    getSub: function (subJson) {
        let id = subJson.id;
        let alreadyInvited = this.currentUserPreviousInvites.filter( invite => invite.sub.id === id ).length > 0;
        return new Sub(subJson, this.currentUser, alreadyInvited);
    },

    getCurrentUserSub: function () {
        return this.subs.find(sub => sub.isCurrentUser) || null;
    },


    render: function () {
        this.$subList.empty();
        this.subs
            .filter(sub => !sub.isCurrentUser)
            .map(sub => this.$subList.append(sub.$dom));

        this.$currentUserPanel.empty();
        if (this.currentUserSub) {
            this.$currentUserPanel.append(this.currentUserSub.$dom);
            this.$currentUserHeader.show()
            this.$currentUserRegisterButton.hide();
        } else {
            this.$currentUserHeader.hide();
            this.$currentUserRegisterButton.show();
        }
        this.$sessionName.text(this.currentSessionEvent.name);
        this.$sessionDate.text(this.currentSessionEvent.date);
        this.$subListHeader.show();
        this.$dateHeader.show();
        this.renderCalendar();
        console.log('user sub', this.currentUserSub);
    },

    getMinTime: function (sessionEvents) {
        let times = sessionEvents.map(event => new Date(event.date + 'T' + event.start_time).getTime());
        return new Date(Math.min(...times)).getHours() - 2 + ':00:00';
    },

    getMaxTime: function (sessionEvents) {
        let times = sessionEvents.map(event => new Date(event.date + 'T' + event.start_time).getTime());
        let minTime = new Date(Math.min(...times)).getHours() - 2 + ':00:00';
        return maxTime;
    },

    setUrl: function (sessionEvent) {
        const message = `Clicked Session ${sessionEvent.id}`;
        const queryParams = `?sessionEventId=${sessionEvent.id}`;
        history.pushState({SessionEvent: sessionEvent}, message, queryParams);
    },

    changeSessionEvent: function (calEvent, jsEvent, view) {
        this.currentSessionEvent = calEvent.sessionEvent;
        this.setUrl(this.currentSessionEvent);
        let self = this;
        api.getSubList({
            session_event__id: this.currentSessionEvent.id
        }).done(subArray => {
            this.subs = subArray.map(sub => this.getSub(sub));
            this.currentUserSub = this.getCurrentUserSub();
            self.render();
        });
    },

    renderCalendar: function () {
        this.$calendar.fullCalendar({
            header: {
                left: 'prev,next today',
                center: 'title',
                right: 'month,agendaWeek,agendaDay,listWeek'
            },
            defaultDate: new Date(this.currentSessionEvent.date).toISOString(),
            navLinks: true, // can click day/week names to navigate views
            editable: false,
            eventLimit: true, // allow "more" link when too many events
            eventClick: this.changeSessionEvent.bind(this),
            events: this.sessionEvents.map(sessionEvent => {
                return {
                    title: this.sessionName,
                    start: sessionEvent.date + 'T' + sessionEvent.start_time,
                    sessionEvent: sessionEvent
                }
            }),
        });
    }
};

$(document).ready(function () {
    substitutes.init();
});
