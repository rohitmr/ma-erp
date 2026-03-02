/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class MaDashboard extends Component {
    static template = "ma_base.MaDashboard";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");

        this.state = useState({
            loading: true,
            today: new Date().toLocaleDateString("en-GB", {
                weekday: "long",
                year: "numeric",
                month: "long",
                day: "numeric",
            }),
            total_receivables_formatted: "...",
            overdue_amount_formatted: "...",
            overdue_count: 0,
            pending_jobs: 0,
            overdue_jobs: 0,
            ongoing_projects: 0,
            expiring_docs: 0,
        });

        onWillStart(async () => {
            await this._loadData();
        });
    }

    async _loadData() {
        try {
            const data = await this.orm.call("ma.division", "get_dashboard_data", [], {});
            Object.assign(this.state, data, { loading: false });
        } catch {
            this.state.loading = false;
        }
    }

    openAction(xmlId) {
        this.action.doAction(xmlId);
    }

    openOverdue() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Overdue Invoices",
            res_model: "account.move",
            view_mode: "list,form",
            domain: [
                ["move_type", "in", ["out_invoice", "out_refund"]],
                ["state", "=", "posted"],
                ["payment_state", "in", ["not_paid", "partial"]],
                ["invoice_date_due", "<", new Date().toISOString().slice(0, 10)],
            ],
        });
    }

    openPendingJobs() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Pending Service Jobs",
            res_model: "project.task",
            view_mode: "list,kanban,form",
            domain: [["stage_id.is_closed", "=", false]],
            context: { search_default_my_tasks: 0 },
        });
    }

    openProjects() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Contracting Projects",
            res_model: "project.project",
            view_mode: "list,kanban,form",
        });
    }
}

registry.category("actions").add("ma_base.MaDashboard", MaDashboard);
