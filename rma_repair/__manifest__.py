# Copyright NuoBiT - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    "name": "RMA Repair",
    "summary": "Allows to link RMA with repair orders",
    "version": "14.0.0.0.0",
    "development_status": "Production/Stable",
    "category": "RMA",
    "website": "https://github.com/OCA/rma",
    "author": "NuoBiT Solutions, S.L., Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["rma", "repair"],
    "data": [
        "security/ir.model.access.csv",
        "views/repair_views.xml",
        "wizards/rma_repair_wizard_views.xml",
        "views/rma_views.xml",
    ],
}
