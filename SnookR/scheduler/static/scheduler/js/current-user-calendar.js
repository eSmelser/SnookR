$(document).ready(function () {
    console.log('here', initialSessionEvents);

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
            window.location.href = calEvent.sessionEvent.url;
        },
        events: initialSessionEvents.map(sessionEvent => {
            return {
                title: sessionEvent.session.name,
                start: sessionEvent.date + 'T' + sessionEvent.start_time,
                sessionEvent: sessionEvent
            }
        }),
    });
});
