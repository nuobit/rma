# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import _, fields, models
from odoo.exceptions import UserError


class Rma(models.Model):
    _inherit = "rma"

    repair_order_ids = fields.One2many(
        comodel_name="repair.order",
        inverse_name="rma_id",
        readonly=True,
        copy=False,
    )
    repair_count = fields.Integer(compute="_compute_repair_count")

    def _compute_repair_count(self):
        for rma in self:
            rma.repair_count = len(rma.repair_order_ids)

    product_qty_in_repair = fields.Float(compute="_compute_product_qty_in_repair")

    def _compute_product_qty_in_repair(self):
        for rec in self:
            rec.product_qty_in_repair = sum(rec.repair_order_ids.mapped("product_qty"))

    can_create_repair_order = fields.Boolean(compute="_compute_can_create_repair_order")

    def _compute_can_create_repair_order(self):
        for rec in self:
            rec.can_create_repair_order = (
                rec.can_be_returned and rec.product_qty_in_repair < rec.product_uom_qty
            )

    def _ensure_qty_to_return(self, qty=None, uom=None):
        super()._ensure_qty_to_return(qty, uom)
        if qty and uom:
            under_repair_qty = sum(
                self.repair_order_ids.filtered(lambda x: x.state != "done").mapped(
                    "product_qty"
                )
            )
            if qty > (self.product_uom_qty - under_repair_qty):
                raise UserError(
                    _(
                        "You can't return to the partner products that are under repair. "
                        "Please check the products to be repaired."
                    )
                )

    def action_view_repair_order(self):
        action = self.env.ref("repair.action_repair_order_tree")
        result = action.sudo().read()[0]
        result["domain"] = [("id", "in", self.repair_order_ids.ids)]
        return result
