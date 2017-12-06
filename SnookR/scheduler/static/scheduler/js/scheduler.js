$(document).ready(function() {
    let division = $('#id_division').val();
    console.log('divison=', division);

    api.getSessionList()
        .done(function(data) {
            console.log('sessions=', data);
        });



    $('#calendar').fullCalendar({
        header: {
            left: 'prev,next today',
            center: 'title',
            right: 'month,agendaWeek,agendaDay,listWeek'
        },
        defaultDate: '2017-11-12',
        navLinks: true, // can click day/week names to navigate views
        editable: false,
        eventLimit: true, // allow "more" link when too many events
        eventClick: function(calEvent, jsEvent, view) {
            console.log('eventClick', calEvent);


            // Expand the right column
            $('#right-column').text(calEvent.title);

            // change the border color just for fun
            $(this).css('border-color', 'red');
        },
        events: [
            {
                title: 'All Day Event',
                start: '2017-11-01',
            },
            {
                title: 'Long Event',
                start: '2017-11-07',
                end: '2017-11-10'
            },
            {
                id: 999,
                title: 'Repeating Event',
                start: '2017-11-09T16:00:00'
            },
            {
                id: 999,
                title: 'Repeating Event',
                start: '2017-11-16T16:00:00'
            },
            {
                title: 'Conference',
                start: '2017-11-11',
                end: '2017-11-13'
            },
            {
                title: 'Meeting',
                start: '2017-11-12T10:30:00',
                end: '2017-11-12T12:30:00'
            },
            {
                title: 'Lunch',
                start: '2017-11-12T12:00:00'
            },
            {
                title: 'Meeting',
                start: '2017-11-12T14:30:00'
            },
            {
                title: 'Happy Hour',
                start: '2017-11-12T17:30:00'
            },
            {
                title: 'Dinner',
                start: '2017-11-12T20:00:00'
            },
            {
                title: 'Birthday Party',
                start: '2017-11-13T07:00:00'
            },
            {
                title: 'Click for Google',
                url: 'http://google.com/',
                start: '2017-11-28'
            }
        ]
    });
});