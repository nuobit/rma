# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, models
from odoo.exceptions import ValidationError


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    # @api.onchange("product_id", "company_id")
    # def _onchange_lot_id_rma_return(self):
    #     self.ensure_one()
    #     rma = self.move_id.rma_id
    #     if rma:
    #         if (
    #             self.env.context.get("rma_delivery_type") == "return"
    #             or rma.state == "waiting_return"
    #         ) and rma.lot_ids:
    #             return {
    #                 "domain": {
    #                     "lot_id": [
    #                         ("id", "in", rma.lot_ids.ids),
    #                         ("product_id", "=", self.product_id.id),
    #                         ("company_id", "=", self.company_id.id),
    #                     ]
    #                 }
    #             }

    @api.constrains("lot_id")
    def _check_lot_id_rma_return(self):
        for rec in self:
            rma = rec.move_id.rma_id
            if rma:
                if rma.state == "waiting_return" and rma.lot_ids:
                    if rec.lot_id not in rma.lot_ids:
                        raise ValidationError(
                            _(
                                "You can only select a lot from the RMA. "
                                "The following lots are available: %s"
                            )
                            % rma.lot_ids.mapped("name")
                        )
