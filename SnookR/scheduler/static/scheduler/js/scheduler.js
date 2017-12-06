$(document).ready(function () {
    let division = $('#id_division').val();
    console.log('divison=', division);

    api.getSessionList()
        .done(function (data) {
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
                defaultDate: '2017-11-12',
                navLinks: true, // can click day/week names to navigate views
                editable: false,
                eventLimit: true, // allow "more" link when too many events
                eventClick: function (calEvent, jsEvent, view) {
                    console.log('eventClick', calEvent);


                    // Expand the right column
                    $('#right-column').text(calEvent.title);

                    // change the border color just for fun
                    $(this).css('border-color', 'red');
                },
                events: eventList,
            });
        });
});