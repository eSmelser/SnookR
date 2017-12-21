/**
 * Created by bobby on 12/16/17.
 */

function unregisterFormDOMString(unregisterUrl) {
    let domString = `
        <form class="pull-right session-button" action="${unregisterUrl}">
            <input type="submit" value="Unregister">
        </form>`;

    return domString;
}

function userPanelDOM(userName, profileUrl, thumbnailUrl, inviteUrl, isCurrentUser, unregisterUrl) {
    let buttonOrFormDOMString;
    if (isCurrentUser) {
        buttonOrFormDOMString = unregisterFormDOMString(unregisterUrl);
    } else {
        buttonOrFormDOMString =
            `<button class="session-button pull-right" type="button" href="${inviteUrl}">Invite</button>`;
    }

    let domString = `
                        <div class="panel panel-default">
                        <div class="panel-body">
                            <div class="pull-left">
                                <a href="${profileUrl}">
                                    <img class="img-circle" width="50px" height="50px"
                                         style="margin-right:8px; margin-top:-5px;"
                                         src="${thumbnailUrl}"
                                    >
                                </a>
                            </div>
                            <h4 class="pull-left"><a href="${profileUrl}"
                                                     style="text-decoration:none;"><strong>${userName}</strong></a>
                            </h4>
                            ${buttonOrFormDOMString}
                        </div>
                    </div>
    `;

    return $(domString)
}

$(document).ready(function () {
    api.getLoggedInUser().done(function (userData) {
        const userId = userData.id;
        api.getSessionEventList({
            // SESSION_SLUG comes from the Django template that includes this script
            session__slug: SESSION_SLUG,
        }).done(function (data) {
            let sessionEventList = [];
            for (elem in data) {
                if (data.hasOwnProperty(elem)) {
                    sessionEventList.push(data[elem])
                }
            }

            let eventList = sessionEventList.map(elem => {
                return {
                    title: SESSION_NAME,
                    start: elem.date + 'T' + elem.start_time,
                    sessionEventId: elem.id,
                    sessionEventRegisterUrl: elem.invite_url
                }
            });

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
                    let sessionEventId = calEvent.sessionEventId;
                    let sessionEventRegisterUrl = calEvent.sessionEventRegisterUrl;

                    const sessionUnregisterUrl = calEvent.unregisterUrl;

                    api.getSubList({
                        session_event__id: sessionEventId
                    }).done(function (data) {
                        let $list = $('#sub-list').empty();

                        const userIsAvailable = data.filter(elem => elem.user.id === userId).length !== 0;
                        if (!userIsAvailable) {
                            $(`<form action="${sessionEventRegisterUrl}">
                                 <input class="btn btn-primary" type="submit" value="Sign up for {{ session|title }}'s sub list!">
                               </form>`)
                        }

                        data.map(elem => {
                            let userName = elem.user.username;
                            let userUrl = elem.user.url;
                            let thumbnailUrl = elem.user.thumbnail_url;
                            let inviteUrl = 'dummy-url';
                            const isCurrentUser = elem.user.id !== userId;

                            $panelDOM = userPanelDOM(userName, userUrl, thumbnailUrl, inviteUrl, isCurrentUser, sessionUnregisterUrl);
                            // Avoid displaying current user in list
                            if (isCurrentUser) {
                                $list.append($panelDOM);
                            } else {
                                $('#current-user-panel')
                                    .empty()
                                    .append($panelDOM)
                            }
                        });
                    });
                },
                events: eventList,
            });
        });
    });
});