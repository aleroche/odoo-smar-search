/** @odoo-module **/


import publicWidget from 'web.public.widget';

publicWidget.registry.KramerSearch = publicWidget.Widget.extend({
    selector: '.kramer_searchbar',

    events: {
        // 'input .karamer_input_search': 'onChangeInput',
        'keydown .karamer_input_search': 'onHandleKeydown',

    },
    start: function () {
        this.kramerSpinner = this.el.querySelector('.kramer-spinner')
    },


    async onHandleKeydown(evt) {
        const value = evt.target.value
        if (evt.keyCode === 13) {
            this.toggleSpinner('show')
            try {
                await this.getProductData(value)
                this.toggleSpinner('hidden')
            } catch (e) {
                this.toggleSpinner('hidden')
            }


        }
    },

    async getProductData(value) {
        const data = await this._rpc({
            route: '/website/snippet/kramer/smart-search',
            params: {
                'term': value,
            }
        })
        console.log("DATA", data[0])
        await this.renderData(data)
    },

    async renderData(products) {
        let html = ''
        const container = this.el.querySelector("#product-list")
        /**
         * Todo: obtner la url del producto
         * Todo: obtener la imagen del producto
         *
         *
         *
         * **/
        products.forEach(product => {
            html += `<a class="dropdown-item p-2 text-wrap" href="${product.website_url}">
                            <div class="d-flex align-items-center o_search_result_item">
                                <img class="flex-shrink-0 o_image_64_contain" 
                                      data-oe-model="ir.ui.view" 
                                      data-oe-id="1254" data-oe-field="arch" 
                                      data-oe-xpath="/t[1]/a[1]/div[1]/img[1]" 
                                      src="${product.image_url}" 
                                      style=""
                                      alt="Product Image"
                                      />
                                <div class="o_search_result_item_detail px-3">
                                    <div class="h6 fw-bold mb-0">
                                        <span>${product.name}</span>
                                    </div>
                                   
                                </div>
                                <div class="flex-shrink-0">
                                    <b class="text-nowrap"> $ &nbsp;<span class="oe_currency_value">${product.list_price.toFixed(2)}</span>
                                    </b>
                                </div>
                            </div>
                        </a>`
        })
        container.innerHTML = html


    },


    _removeAllChildNodes(parent) {
        while (parent.firstChild) {
            parent.removeChild(parent.firstChild);
        }
    },

    toggleSpinner(action) {
        this.kramerSpinner.classList.toggle('d-none')


    }

    //
    // _onInput(evt) {
    //     this.term = evt.target.value
    // },

    // async _onKeydown(evt) {
    //     if (evt.which === 13) {
    //         await this._fetch()
    //     }
    //
    // },

    // async _fetch() {
    //     console.log("SSSSSSSSSSSSSSSSSS")
    //     // const res = await this._rpc({
    //     //     route: '/website/snippet/kramer/smart-search',
    //     //     params: {
    //     //
    //     //     },
    //     // })
    //
    //     // console.log("RESPONSE", res)
    // }

});

export default publicWidget.registry.KramerSearch;
