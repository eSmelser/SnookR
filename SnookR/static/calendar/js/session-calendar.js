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
        this.subs = context.initialSubArray.map(sub => this.getSub(sub));
        this.sessionName = context.sessionName;
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
    },

    bindEvents: function () {
        this.$rightColumn.on('click', '.invite-button', this.createInvite);
    },

    createInvite: function() {
        $(this)
    },

    getSub: function (subJson) {
        return new Sub(subJson, this.currentUser);
    },

    getCurrentUserSub: function () {
        return this.subs.find(sub => sub.isCurrentUser) || null;
    },


    render: function () {
        this.$subList.empty();
        console.log('-=---')
        this.subs
            .filter(sub => !sub.isCurrentUser)
            .map(sub => this.$subList.append(sub.$dom));

        let currentUserSub = this.getCurrentUserSub();
        this.$currentUserPanel.empty();
        this.$currentUserHeader.hide();
        if (currentUserSub) {
            this.$currentUserPanel.append(currentUserSub.$dom);
            this.$currentUserHeader.show()
        }
        this.$sessionName.text(this.currentSessionEvent.name);
        this.$sessionDate.text(this.currentSessionEvent.date);
        this.renderCalendar();
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
            defaultDate: new Date().toISOString(),
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
