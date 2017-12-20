/**
 * Created by bobby on 12/16/17.
 */

function createUserPanel(userName, profileUrl, thumbnailUrl, inviteUrl) {
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
                            <h4 class="pull-left"><a href="#"
                                                     style="text-decoration:none;"><strong>${userName}</strong></a>
                            </h4>

                            <button class="session-button pull-right" type="button" href="${inviteUrl}">Invite
                            </button>
                        </div>
                    </div>
    `;

    return $(domString)
}

$(document).ready(function () {
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
            return {title: SESSION_NAME, start: elem.date + 'T' + elem.start_time, sessionEventId: elem.id}
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


                api.getSubList({
                    session_event__id: sessionEventId
                }).done(function (data) {
                    // TODO: implement these in API
                    let thumbnailUrl = null;
                    let inviteUrl = null;
                    let $list = $('#sub-list').empty();

                    data.map( elem => $list.append((createUserPanel(elem.user.username, elem.user.url, thumbnailUrl, inviteUrl))) );
                });
            },
            events: eventList,
        });
    });
});