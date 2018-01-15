require('fullcalendar');


const times = context.sessionEvents.map(event => new Date(event.date + 'T' + event.start_time).getTime());
const minTime = new Date(Math.min(...times)).getHours() - 2 + ':00:00';
const maxTime = new Date(Math.max(...times)).getHours() + 2 + ':00:00';

const events = context.sessionEvents.map(sessionEvent => {
    return {
        title: sessionEvent.session.name,
        start: sessionEvent.date + 'T' + sessionEvent.start_time,
        sessionEvent: sessionEvent
    }
});

$(document).ready(function () {
    $('#calendar').fullCalendar({
        header: {
            left: 'prev,next today',
            center: 'title',
            right: 'month'
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
        events: events,
    });
});
