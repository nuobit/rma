# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class RmaRepairWizard(models.TransientModel):
    _name = "rma.repair.wizard"
    _description = "RMA Repair Wizard"

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        rma_ids = self.env.context["active_ids"] or []
        active_model = self.env.context["active_model"]
        if not rma_ids:
            return res
        if active_model != "rma":
            raise UserError(
                _("The expected model for this action is 'rma', not '%s'.")
                % active_model
            )
        rma = self.env["rma"].browse(rma_ids)
        res["rma_id"] = rma.id
        res["partner_id"] = rma.partner_id.id
        res["product_id"] = rma.product_id.id
        return res

    @api.constrains("lot_ids")
    def _check_lot_ids(self):
        for rec in self:
            dup_lot = rec.rma_id.repair_order_ids.filtered(
                lambda x: x.lot_id in rec.lot_ids
            )
            if dup_lot:
                raise ValidationError(
                    _("You already have a repair order for the lot [%s].")
                    % ", ".join(dup_lot.mapped("lot_id.name"))
                )

    @api.constrains("product_qty")
    def _check_product_qty(self):
        for rec in self:
            if not rec.has_lots:
                if rec.product_qty <= 0.0:
                    raise ValidationError(_("Quantity must be positive."))
                if (
                    rec.product_qty + rec.rma_id.product_qty_in_repair
                    > rec.rma_id.product_uom_qty
                ):
                    raise ValidationError(
                        _(
                            "Total quantity to repair must be less "
                            "than or equal to the RMA quantity."
                        )
                    )

    rma_id = fields.Many2one(
        comodel_name="rma", string="RMA", readonly=True, required=True
    )
    product_id = fields.Many2one(
        comodel_name="product.product", readonly=True, required=True
    )
    product_qty = fields.Float(string="Quantity to repair", digits="Product UoS")
    partner_id = fields.Many2one(
        comodel_name="res.partner", readonly=True, required=True
    )
    lot_ids = fields.Many2many(comodel_name="stock.production.lot")

    @api.onchange("rma_id")
    def _onchange_domain_lot_ids(self):
        for rec in self:
            rma_lots = rec.rma_id.reception_move_id.picking_id.move_line_ids.lot_id
            return {"domain": {"lot_ids": [("id", "in", rma_lots.ids)]}}

    has_lots = fields.Boolean(compute="_compute_has_lots")

    @api.depends("rma_id")
    def _compute_has_lots(self):
        for rec in self:
            rec.has_lots = bool(
                rec.rma_id.reception_move_id.picking_id.move_line_ids.lot_id
            )

    def _prepare_repair_order(self, lot_id=None):
        self.ensure_one()
        vals = {
            "rma_id": self.rma_id.id,
            "product_id": self.product_id.id,
            "partner_id": self.partner_id.id,
            "product_qty": self.product_qty or 1.0,
            "product_uom": self.product_id.uom_id.id,
            "company_id": self.rma_id.company_id.id,
            "location_id": self.rma_id.location_id.id,
            "lot_id": lot_id,
        }
        if self.rma_id.user_id:
            vals["user_id"] = self.rma_id.user_id.id
        return vals

    def action_create_repair_order(self):
        self.ensure_one()
        lot_ids = self.lot_ids or [None]
        idx = 0
        repairs = []
        while True:
            lot_id = lot_ids[idx]
            data = self._prepare_repair_order(lot_id=lot_id.id if lot_id else None)
            repairs.append(data)
            idx += 1
            if idx >= len(lot_ids):
                break
        repair_orders = self.env["repair.order"]
        for data in repairs:
            repair = self.env["repair.order"].create(data)
            repair.onchange_partner_id()
            repair_orders |= repair
        return {
            "name": _("Repair Order"),
            "view_mode": "tree,form",
            "res_model": "repair.order",
            "domain": [("id", "in", repair_orders.ids)],
            "type": "ir.actions.act_window",
        }

    def action_create_repair_order_and_block_rma(self):
        self.ensure_one()
        self.rma_id.action_lock()
        return self.action_create_repair_order()
