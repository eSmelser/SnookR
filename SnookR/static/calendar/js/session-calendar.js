/**
 * Created by bobby on 12/16/17.
 */

require('moment');
require('fullcalendar');
let templates = require('../../core/js/templates');
let api = require('../../api/js/api.js');

const currentUserPanelDOM = function (user, unregisterUrl) {
    let formDOMString =
        `<form class="pull-right session-button" action="${unregisterUrl}">
                <input type="submit" value="Unregister">
            </form>`;

    return templates.genericUserPanelDOM(user, formDOMString);
};

const subUserPanelDOM = function (user) {
    let buttonDOMString = context.currentUserIsCaptain ?
        `<button class="session-button pull-right" type="button" href="${user.inviteUrl}">Invite</button>` : '';

    return templates.genericUserPanelDOM(user, buttonDOMString);
};


const renderSublistPanels = function (subArray) {
    // We only need to empty the list once
    let $list = $('#sub-list').empty();
    if (subArray) {
        subArray.map(sub => $list.append(subUserPanelDOM(sub.user)));
    } else {
        $list.append('<strong>No subs registered!</strong>');
    }
};

const renderCurrentUserPanel = function (currentUserSub) {
    let $currentUserPanel = $('#current-user-panel').empty();
    if (currentUserSub) {
        $currentUserPanel
            .show()
            .append(currentUserPanelDOM(currentUserSub.user, currentUserSub.session_event.unregister_url));
    } else {
        $currentUserPanel.hide();
    }
};

const renderSublistHeader = function (sessionEvent) {
    $('#sub-list-header')
        .show()
        .text(`Subs Available for ${sessionEvent.session.name} on ${sessionEvent.date}`);
};

const renderCurrentUserHeader = function (sessionEvent, currentUserSub) {
    let $header = $('#current-user-header');
    let text = `You Are Available for ${sessionEvent.session.name} on ${sessionEvent.date}`;

    currentUserSub ? $header.text(text).show() : $header.empty().hide();
};

const getCurrentUserSub = function (user, subArray) {
    return subArray.filter(sub => sub.user.id === user.id).pop();
};

const removeCurrentUserSub = function (user, subArray) {
    return subArray.filter(sub => sub.user.id !== user.id);
};

const renderRegisterForm = function (currentUserSub, sessionEvent) {
    let $div = $('#register-form-div').empty();

    // There only exists a sub for the current user if he is registered for the current session
    if (!currentUserSub) {
        let DOMString =
            `<form action="${sessionEvent.register_url}">
                <input class="btn btn-primary" type="submit" value="Sign up for ${SESSION_NAME}'s sub list!">
            </form>`;

        let $form = $(DOMString);
        $div.append($form);
    }
};

/**
 * setUrl() changes the url to match the current session event
 * @param sessionEvent
 */
const setUrl = function (sessionEvent) {
    const message = `Clicked Session ${sessionEvent.id}`;
    const queryParams = `?sessionEventId=${sessionEvent.id}`;
    history.pushState({sessionEvent: sessionEvent}, message, queryParams);
};

/**
 * initializePage() renders DOM based on global data set by the Django template
 * @param currentUser
 *
 * Note 1:  We use global data from the Django template to reduce an unnecessary API request after page load.
 * Note 2: We must wait to get the currentUser from an API call.  This is so we don't have to put user data
 *         inside html at all, which I suspect would be a security risk.
 */
const initializePage = function (currentUser) {
    let currentUserSub = getCurrentUserSub(currentUser, context.initialSubArray);
    let subArray = removeCurrentUserSub(currentUser, context.initialSubArray);

    renderCurrentUserHeader(context.initialSessionEvent, currentUserSub);
    renderSublistHeader(context.initialSessionEvent);
    renderCurrentUserPanel(currentUserSub);
    renderRegisterForm(currentUserSub, context.initialSessionEvent);
    renderSublistPanels(subArray);

    setUrl(initialSessionEvent);
};

$(document).ready(function () {
    api.getLoggedInUser().done(function (currentUser) {
        initializePage(currentUser);

        api.getSessionEventList({
            // SESSION_SLUG comes from the Django template that includes this script
            session__slug: context.SESSION_SLUG,
        }).done(function (sessionEvents) {


            let times = sessionEvents.map(event => new Date(event.date + 'T' + event.start_time).getTime());
            let minTime = new Date(Math.min(...times)).getHours() - 2 + ':00:00';
            let maxTime = new Date(Math.min(...times)).getHours() + 2 + ':00:00';

            $('#calendar').fullCalendar({
                header: {
                    left: 'prev,next today',
                    center: 'title',
                    right: 'month,agendaWeek,agendaDay,listWeek'
                },
                defaultDate: new Date().toISOString(),
                navLinks: true, // can click day/week names to navigate views
                editable: false,
                minTime: minTime,
                maxTime: maxTime,
                eventLimit: true, // allow "more" link when too many events
                eventClick: function (calEvent, jsEvent, view) {
                    const sessionEvent = calEvent.sessionEvent;
                    renderSublistHeader(sessionEvent);
                    setUrl(sessionEvent);

                    api.getSubList({
                        session_event__id: sessionEvent.id
                    }).done(subArray => {
                        let currentUserSub = getCurrentUserSub(currentUser, subArray);
                        subArray = removeCurrentUserSub(currentUser, subArray);

                        renderCurrentUserHeader(sessionEvent, currentUserSub);
                        renderCurrentUserPanel(currentUserSub);
                        renderRegisterForm(currentUserSub, sessionEvent);
                        renderSublistPanels(subArray);
                    });
                },
                events: sessionEvents.map(sessionEvent => {
                    return {
                        title: context.SESSION_NAME,
                        start: sessionEvent.date + 'T' + sessionEvent.start_time,
                        sessionEvent: sessionEvent
                    }
                }),
            });
        });
    });
});