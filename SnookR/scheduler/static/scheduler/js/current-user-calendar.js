$(document).ready(function () {
    api.getLoggedInUser().done(function(data) {
        const username = data.username;
        api.getSessionList({
            subs__user__username: username
        }).done(function (data) {
            let sessionList = [];
            for (elem in data) {
                if (data.hasOwnProperty(elem)) {
                    sessionList.push(data[elem])
                }
            }

            let eventList = sessionList.map(elem => {
                return {title: elem.name, start: elem.start_date, end: elem.end_date}
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
                },
                events: eventList,
            });
        });
    });
});