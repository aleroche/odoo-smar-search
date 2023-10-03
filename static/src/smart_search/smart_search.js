/** @odoo-module */

import {registry} from "@web/core/registry";
import {Component, useState} from "@odoo/owl";
import {useService} from "@web/core/utils/hooks";

export class SmartSearchWidget extends Component {
    setup() {
        this.orm = useService('orm')
        this.state = useState({
            searchString: "desk",
        });
    }

    _onChageSearch(evt) {
        this.state.searchString = evt.target.value
    }

    async _onKeyPress(evt) {
        if (evt.keyCode === 13) {
            evt.preventDefault()
            const question = this.state.searchString.trim()
            if (question.length === 0) return

            const productsTemplatesId = await this.getProductsIds(question)

            console.log("productsTemplatesId", productsTemplatesId)
            console.log("this.env", this.env.searchModel)
            return this.env.searchModel.setDomainParts({
                product: {
                    domain: [["id", "in", productsTemplatesId]],
                    facetLabel: this.state.searchString
                }
            })


            // this.env.searchModel.setDomainParts({
            //     customer: {
            //         domain: [["customer_id", "=", costumer_id]],
            //         facetLabel: customer_name,
            //     },
            // });

        }

    }

    async getProductsIds(query) {

        const response = await this.orm.call(
            'smart.search',
            "query_with_params",
            [query],
        );
        // get a list of ids of products_templates
        return response

    }


}

SmartSearchWidget.template = "smart_search.SmartSearchWidget"

registry.category('view_widgets').add('smart_search', SmartSearchWidget)

