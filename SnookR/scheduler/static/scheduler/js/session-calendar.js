/**
 * Created by bobby on 12/16/17.
 */

const genericUserPanelDOM = function (user, actionDOMString) {
    //This layout is inspired by the snippet found here: https://bootsnipp.com/snippets/56ExR
    return $(`
                    <div class="panel panel-default">
                        <div class="panel-body">
                            <div class="pull-left">
                                <a href="${user.url}">
                                    <img class="img-circle" width="50px" height="50px"
                                         style="margin-right:8px; margin-top:-5px;"
                                         src="${user.thumbnail_url}"
                                    >
                                </a>
                            </div>
                            <h4 class="pull-left"><a href="${user.url}"
                                                     style="text-decoration:none;"><strong>${user.username}</strong></a>
                            </h4>
                            ${actionDOMString}
                        </div>
                    </div>
    `);
};

const currentUserPanelDOM = function (user, unregisterUrl) {
    let formDOMString =
        `<form class="pull-right session-button" action="${unregisterUrl}">
                <input type="submit" value="Unregister">
            </form>`;

    return genericUserPanelDOM(user, formDOMString);
};

const subUserPanelDOM = function (user) {
    let buttonDOMString =
        `<button class="session-button pull-right" type="button" href="${user.inviteUrl}">Invite</button>`;

    return genericUserPanelDOM(user, buttonDOMString);
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

const renderRegisterForm = function (currentUserSub, unregisterUrl) {
    let $div = $('#register-form-div').empty();

    // There only exists a sub for the current user if he is registered for the current session
    if (!currentUserSub) {
        let action = `${unregisterUrl}?next=${window.location.pathname + window.location.search}`;
        let DOMString =
            `<form action="${action}">
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
    let currentUserSub = getCurrentUserSub(currentUser, initialSubArray);
    let subArray = removeCurrentUserSub(currentUser, initialSubArray);

    renderCurrentUserHeader(initialSessionEvent, currentUserSub);
    renderSublistHeader(initialSessionEvent);
    renderCurrentUserPanel(currentUserSub);
    renderRegisterForm(currentUserSub, initialSessionEvent.unregister_url);
    renderSublistPanels(subArray);

    setUrl(initialSessionEvent);
};

$(document).ready(function () {
    api.getLoggedInUser().done(function (currentUser) {
        initializePage(currentUser);

        api.getSessionEventList({
            // SESSION_SLUG comes from the Django template that includes this script
            session__slug: SESSION_SLUG,
        }).done(function (sessionEvents) {
            $('#calendar').fullCalendar({
                header: {
                    left: 'prev,next today',
                    center: 'title',
                    right: 'month,agendaWeek,agendaDay,listWeek'
                },
                defaultDate: new Date().toISOString(),
                navLinks: true, // can click day/week names to navigate views
                editable: false,
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
                        renderRegisterForm(currentUserSub, sessionEvent.unregister_url);
                        renderSublistPanels(subArray);
                    });
                },
                events: sessionEvents.map(sessionEvent => {
                    return {
                        title: SESSION_NAME,
                        start: sessionEvent.date + 'T' + sessionEvent.start_time,
                        sessionEvent: sessionEvent
                    }
                }),
            });
        });
    });
});