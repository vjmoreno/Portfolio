document.addEventListener("DOMContentLoaded", function (event) {
    odoo.define('auction_website.timer', ['web.ajax', 'web.rpc'], function (require) {
        "use strict";

        var ajax = require('web.ajax');
        var rpc = require('web.rpc');

        $(document).ready(function () {

            function getTimeRemaining(endtime, now_time, id, is_logged_in, is_product, is_in_process) {
                if (is_logged_in) {
                    return fetchingTime(id, is_product).then(function (list_time) {
                        var endtime = list_time[0]
                        var backend_now_time = list_time[1]
                        is_in_process = list_time[2]
                        const time = calculate_time(endtime, backend_now_time)
                        return [time, is_in_process]
                    });
                } else {
                    const time = calculate_time(endtime, now_time)
                    return [time, is_in_process]
                }
            }

            async function fetchingTime(_id, is_product) {
                if (is_product) {
                    var list_time = await rpc.query({
                        model: 'product.template',
                        method: 'get_countdown_time',
                        args: [_id]
                    });
                } else {
                    var list_time = await rpc.query({
                        model: 'auction',
                        method: 'get_countdown_time',
                        args: [_id]
                    });
                }
                return list_time
            }

            function calculate_time(endtime, now_time) {
                const total = endtime - now_time;
                const seconds = Math.floor((total / 1000) % 60);
                const minutes = Math.floor((total / 1000 / 60) % 60);
                const hours = Math.floor((total / (1000 * 60 * 60)) % 24);
                const days = Math.floor(total / (1000 * 60 * 60 * 24));
                return {
                    total,
                    days,
                    hours,
                    minutes,
                    seconds
                };
            }

            function writeTimeSpan(timeSpan, t, is_in_process, is_logged_in) {
                var start_bool = false;
                if (is_in_process) {
                    var starting_string = 'Finaliza en '
                    start_bool = false;
                } else {
                    starting_string = 'Comienza en '
                    start_bool = true;
                }
                if (t.total < 1000 && !is_logged_in) {
                    if (start_bool) {
                        timeSpan.innerHTML = 'La subasta ha comenzado';
                    } else {
                        timeSpan.innerHTML = 'Finalizada';
                    }
                } else if (t.total < 1000 && is_logged_in && !is_in_process) {
                    timeSpan.innerHTML = 'Finalizada';
                } else {
                    if (t.days) {
                        timeSpan.innerHTML = starting_string + t.days + ' días ' + ('0' + t.hours).slice(-2) + ' horas ' + ('0' + t.minutes).slice(-2) + ' minutos ' + ('0' + t.seconds).slice(-2) + ' segundos ';
                    } else if (t.hours) {
                        timeSpan.innerHTML = starting_string + ('0' + t.hours).slice(-2) + ' horas ' + ('0' + t.minutes).slice(-2) + ' minutos ' + ('0' + t.seconds).slice(-2) + ' segundos ';
                    } else if (t.minutes) {
                        timeSpan.innerHTML = starting_string + ('0' + t.minutes).slice(-2) + ' minutos ' + ('0' + t.seconds).slice(-2) + ' segundos ';
                    } else {
                        timeSpan.innerHTML = starting_string + ('0' + t.seconds).slice(-2) + ' segundos ';
                    }
                }
            }

            function initializeClock(id, endtime, now_time, is_in_process, is_logged_in, is_product) {
                const timeSpan = document.getElementById('time_' + id);
                var now_time = parseInt(now_time)

                function updateClock() {
                    if (is_logged_in) {
                        getTimeRemaining(endtime, now_time, id, is_logged_in, is_product, is_in_process).then(function (t_list) {
                            var t = t_list[0]
                            is_in_process = t_list[1]
                            writeTimeSpan(timeSpan, t, is_in_process, is_logged_in)
                        })

                    } else {
                        now_time += 1000
                        var t_list = getTimeRemaining(endtime, now_time, id, is_logged_in, is_product, is_in_process);
                        var t = t_list[0]
                        writeTimeSpan(timeSpan, t, is_in_process, is_logged_in)
                    }
                }

                const timeinterval = setInterval(function () {
                    updateClock()
                }, 1000);
            }

            var list = document.getElementsByClassName("timer");
            for (var i = 0; i < list.length; i++) {
                initializeClock(list[i].id, list[i].getAttribute("value"), list[i].getAttribute("now"), list[i].getAttribute("is_in_process"), list[i].getAttribute("is_logged_in"), list[i].getAttribute("is_product"));
            }
        });
    });
})