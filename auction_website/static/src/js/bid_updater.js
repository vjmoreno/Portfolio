document.addEventListener("DOMContentLoaded", function (event) {
    odoo.define('auction_website.bid_updater', ['web.ajax', 'web.rpc'], function (require) {
        "use strict";

        var ajax = require('web.ajax');
        var rpc = require('web.rpc');

        $(document).ready(function () {

            function getData(pricelist_id, product_id) {
                return fetchData(pricelist_id, product_id).then(function ([current_price, next_bid_price, ownership]) {
                    return [current_price, next_bid_price, ownership]
                });
            }

            async function fetchData(pricelist_id, product_id) {
                var [current_price, next_bid_price, ownership] = await rpc.query({
                    model: 'product.template',
                    method: 'get_lot_price',
                    args: [[], {'pricelist_id': pricelist_id, 'product_id': product_id}]
                });
                return [current_price, next_bid_price, ownership]
            }

            function update(lot_price, bid_button, bid_input, current_price, currency_symbol, next_bid_price, ownership) {
                lot_price.innerHTML = 'Oferta actual: ' + current_price + ' ' + currency_symbol
                if (current_price == 0){
                    lot_price.innerHTML += '(Haz la primera oferta!)'
                }
                else if (ownership) {
                    lot_price.innerHTML += ' (Vas ganando la subasta!)'
                } else {
                    lot_price.innerHTML += ' (Otro usuario va ganando la subasta!)'
                }
                if (bid_input.value == '') {
                    if (next_bid_price != undefined) {
                        bid_button.innerHTML = 'Oferta: ' + next_bid_price + ' ' + currency_symbol
                    } else {
                        bid_button.innerHTML = 'Oferta'
                    }
                } else {
                    bid_button.innerHTML = 'Oferta: ' + bid_input.value + ' ' + currency_symbol
                }
            }

            function BidUpdater() {
                const lot_price = document.getElementById('lot_price');
                if (lot_price) {
                    const bid_button = document.getElementsByClassName('bid-button')[0];
                    const bid_input = document.getElementById('bid_input');
                    const pricelist_id = lot_price.getAttribute('pricelist_id');
                    const product_id = lot_price.getAttribute('product_id');
                    const currency_symbol = lot_price.getAttribute('currency_symbol');
                    if (bid_input) {
                        function updatePage() {
                            getData(pricelist_id, product_id).then(function ([current_price, next_bid_price, ownership]) {
                                update(lot_price, bid_button, bid_input, current_price, currency_symbol, next_bid_price, ownership)
                            })
                        }

                        bid_button.style.pointerEvents = "auto";
                        const timeinterval = setInterval(function () {
                            updatePage()
                        }, 1000)
                    }
                }
            }
            BidUpdater();
        });
    });
})
