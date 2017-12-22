$(document).ready(function () {

    let times = initialSessionEvents.map( event => new Date(event.date + 'T' + event.start_time).getTime() );
    let minTime = new Date(Math.min(...times)).getHours() - 2 + ':00:00';
    let maxTime = new Date(Math.min(...times)).getHours() + 2 + ':00:00';

    $('#calendar').fullCalendar({
        header: {
            left: 'prev,next today',
            center: 'title',
            right: 'month,agendaWeek,agendaDay,listWeek'
        },
        defaultDate: new Date().toISOString(),
        minTime: minTime,
        maxTime: maxTime,
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
