# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class RepairOrder(models.Model):
    _inherit = "repair.order"

    rma_id = fields.Many2one(
        comodel_name="rma", string="RMA", readonly=True, ondelete="restrict"
    )
