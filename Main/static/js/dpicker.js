// Параметры DateTimePicker-а
$(function () {
    $('#date_select').datetimepicker({
        defaultDate: new Date(),
        viewMode: 'months',
        format: 'MM.YYYY',
        locale: 'ru'
    });
});

// Исправление бага с месяцем в выборе даты
$("#date_select").on('dp.hide', function (event) {
    setTimeout(function () {
        $("#date_select").data('DateTimePicker').viewMode('months');
    }, 1);
});