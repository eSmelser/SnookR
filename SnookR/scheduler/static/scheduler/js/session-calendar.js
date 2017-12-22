/**
 * Created by bobby on 12/16/17.
 */

function genericUserPanelDOM(user, actionDOMString) {
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
}

function currentUserPanelDOM(user, unregisterUrl) {
    let formDOMString =
        `<form class="pull-right session-button" action="${unregisterUrl}">
                <input type="submit" value="Unregister">
            </form>`;

    return genericUserPanelDOM(user, formDOMString);
}

function subUserPanelDOM(user) {
    let buttonDOMString =
        `<button class="session-button pull-right" type="button" href="${user.inviteUrl}">Invite</button>`;

    return genericUserPanelDOM(user, buttonDOMString);
}


function renderSublistPanels(userId, subArray) {
    // We only need to empty the list once
    $list = $('#sub-list').empty();
    subArray.filter(sub => sub.user.id !== userId).map(sub => $list.append(subUserPanelDOM(sub.user)));
}

function renderCurrentUserPanels(userId, unregisterUrl, subArray) {
    $currentUserPanel = $('#current-user-panel').empty();
    subArray
        .filter(sub => sub.user.id === userId)
        .slice(0, 1)
        .map(sub => $currentUserPanel.append(currentUserPanelDOM(sub.user, unregisterUrl)));
}

function renderSublistHeader(sessionEvent) {
    $('#sub-list-header')
        .replaceWith(`<h2 id="sub-list-header">Subs Available for ${sessionEvent.session.name} on ${sessionEvent.date}</h2>`);
}

function renderCurrentUserHeader(sessionEvent) {
    $('#current-user-header')
        .replaceWith(`<h2>You Are Available for ${sessionEvent.session.name} on ${sessionEvent.date}</h2>`)
}

// Setup the page with the initial data set by the template
function initializePage(currentUser) {
    renderSublistHeader(initialSessionEvent);
    renderCurrentUserHeader(initialSessionEvent);
    renderSublistPanels(currentUser.id, initialSubArray);
    renderCurrentUserPanels(currentUser.id, initialSessionEvent.unregister_url, initialSubArray);
}

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
                    renderCurrentUserHeader(sessionEvent);

                    api.getSubList({
                        session_event__id: sessionEvent.id
                    }).done(subArray => {
                        renderSublistPanels(currentUser.id, subArray);
                        renderCurrentUserPanels(currentUser.id, sessionEvent.unregister_url, subArray);
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