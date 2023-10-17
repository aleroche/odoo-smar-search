/** @odoo-module **/


import publicWidget from 'web.public.widget';

publicWidget.registry.KramerSearch = publicWidget.Widget.extend({
    selector: '.kramer_searchbar',

    events: {
        // 'input .karamer_input_search': 'onChangeInput',
        'keydown .karamer_input_search': 'onHandleKeydown',
        'input .karamer_input_search': 'onHandleInput',
        'click .submit-button': 'onHandleClickSubmit',
        // 'click .link-button': 'onHandleRedirect',

    },
    start: function () {
        this.kramerSpinner = this.el.querySelector('.kramer-spinner')
        this.productContainer = document.getElementsByClassName('product-container')
        this.searchText = ''
    },


    async onHandleKeydown(evt) {
        const value = evt.target.value.trim()
        this.searchText = value
        if (evt.keyCode === 13) {
            evt.preventDefault()
            await this.getProductData(value)
        }
    },


    async onHandleInput(evt) {
        this.searchText = evt.target.value.trim()
    },

    async onHandleClickSubmit(evt) {
        evt.preventDefault()
        await this.getProductData(this.searchText)

    },


    async renderData(data) {
        let html = ''
        const container = this.el.querySelector("#product-list")
        const sqlContainer = this.el.querySelector("#show-sql")
        const {products, sql_ai} = data
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
        sqlContainer.innerHTML = sql_ai

    },


    async searchProductData(value) {
        const data = await this._rpc({
            route: '/website/snippet/kramer/smart-search',
            params: {
                'term': value,
            }
        })

        await this.renderData(data)
    },

    async getProductData(value) {
        this.toggleSpinner('show')
        this.toggleContainer('hidden')
        try {
            await this.searchProductData(value)
            this.toggleSpinner('hidden')
            this.toggleContainer('show')
        } catch (e) {
            this.toggleSpinner('hidden')
            this.toggleContainer('hidden')
        }
    },

    toggleSpinner(action) {
        this.kramerSpinner.classList.toggle('d-none')
    },

    toggleContainer(action) {
        console.log("Action", action)
        const productList = Object.values(this.productContainer)
        if (action === 'hidden') {
            productList.map(pc => {
                pc.classList.add('d-none')
            })
        } else {
            productList.map(pc => {
                pc.classList.remove('d-none')
            })
        }
    }
});

export default publicWidget.registry.KramerSearch;
