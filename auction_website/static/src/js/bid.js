document.addEventListener("DOMContentLoaded", function (event) {
    odoo.define('auction_website.bid', ['web.ajax', 'web.rpc'], function (require) {
        "use strict";

        var ajax = require('web.ajax');
        var rpc = require('web.rpc');

        $(document).ready(function () {

            $(document).on('click', ".bid-button", function () {
                const bid_input = document.getElementById('bid_input');
                const bid_button = document.getElementsByClassName('bid-button');
                const value = bid_input.value
                const pricelist_id = bid_button[0].getAttribute("pricelist_id");
                bid_request(value, this.id, pricelist_id);
                bid_input.value = ''
            });

            function bid_request(value, product_id, pricelist_id) {
                return check_bid(value, product_id, pricelist_id).then(function (res) {
                    const bid_span = document.getElementById('bid_span');
                    bid_span.innerHTML = res;
                    return res
                });
            }

            async function check_bid(value, product_id, pricelist_id) {
                var res = await rpc.query({
                    model: 'product.template',
                    method: 'check_bid_request',
                    args: [[], {
                        'value': value,
                        'pricelist_id': parseInt(pricelist_id),
                        'product_id': parseInt(product_id)
                    }]
                });
                return res
            }
        });
        $(document).ready(function () {
            $("#bid_input").keypress(function () {
                var value = String(this.value)
                value = value.split(".");
                var int_value = String(value[0]);
                var decimal_value = String(value[1]);
                if (decimal_value != 'undefined') {
                    var length = decimal_value.length;
                    if (length > 1) {
                        $(this).val(int_value + '.' + decimal_value.substr(0, 1));

                    }
                }
            });
        });
    });
})