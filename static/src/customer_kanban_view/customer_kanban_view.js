/** @odoo-module */

import {KanbanController} from "@web/views/kanban/kanban_controller";
import {kanbanView} from "@web/views/kanban/kanban_view";
import {registry} from "@web/core/registry";
import {SmartSearchWidget} from "../smart_search/smart_search";
// import {CustomerList} from "../customer_list/customer_list";


class CustomerKanbanController extends KanbanController {

    setup() {
        super.setup()
        this.archInfo = {...this.props.archInfo}
        this.archInfo.className += ' flex-grow-1'
    }

    // selectCustomer(costumer_id, customer_name) {
    //     this.env.searchModel.setDomainParts({
    //         customer: {
    //             domain: [["customer_id", "=", costumer_id]],
    //             facetLabel: customer_name,
    //         },
    //     });
    // }

}


CustomerKanbanController.components = {
    ...KanbanController.components,
    SmartSearchWidget
    // CustomerList
}
CustomerKanbanController.template = "awesome_tshirt.CustomerKanbanController"

export const customerKanbanView = {
    ...kanbanView,
    Controller: CustomerKanbanController
}

registry.category('views').add('customer_kanban', customerKanbanView)