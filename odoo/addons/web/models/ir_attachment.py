# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64

from odoo import api, models
from odoo.tools.image import image_process


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def web_image_data_preview(self, b64_content):
        """Decode image bytes (e.g. HEIC), return JPEG/PNG base64 for browser preview."""
        if not b64_content:
            return b64_content
        raw = base64.b64decode(b64_content)
        processed = image_process(raw, quality=85, output_format='JPEG')
        if not processed:
            return b64_content
        return base64.b64encode(processed).decode('ascii')

    @api.model
    def web_create_image_variants(self, variants):
        """Create linked image variants in batch using `create_unique`."""
        ids = []
        main_attachment_id = False

        for variant in variants:
            values_list = variant.get('images', [])
            if not values_list:
                continue

            resized_attachment_id = False

            for vals in values_list:
                values = dict(vals)
                values['res_model'] = 'ir.attachment'
                values['res_id'] = resized_attachment_id or main_attachment_id

                created_ids = self.create_unique([values])
                attachment_id = created_ids[0].id if created_ids else False
                ids.append(attachment_id)

                resized_attachment_id = attachment_id
                main_attachment_id = main_attachment_id or attachment_id

        return ids
