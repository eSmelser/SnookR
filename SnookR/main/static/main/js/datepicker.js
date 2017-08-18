$(document).ready(
  function() {
    $( "#id_day" ).datepicker()
    $( "#id_day" ).on("change", function() {
        $( "#id_day" ).datepicker( "option", "dateFormat", "yy-mm-dd" );
    }
    )
});