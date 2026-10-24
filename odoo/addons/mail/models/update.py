# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api
from odoo.models import AbstractModel


class Publisher_WarrantyContract(AbstractModel):
    _name = 'publisher_warranty.contract'
    _description = 'Publisher Warranty Contract'

    @api.model
    def update_notification(self, cron_mode=True):
        """Disabled in Templorium: no outbound publisher warranty / telemetry."""
        return True
