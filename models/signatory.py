# -*- coding: utf-8 -*-
import os
import base64
from io import BytesIO

import PIL
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw

from odoo import models, fields, api, _

# TODO update base dir with odoo config
from odoo.exceptions import ValidationError

base_dir = os.path.dirname(os.path.realpath(__file__))
font_dir = os.path.join(base_dir, '../fonts')

signature_frame_dim = (512, 202)
signature_box_dim = (510, 200)

arial_narrow = ImageFont.truetype(os.path.join(font_dir, 'arialn.ttf'), 28, encoding="unic")
arial_italic = ImageFont.truetype(os.path.join(font_dir, 'garii.ttf'), 28, encoding="unic")
arial_bold = ImageFont.truetype(os.path.join(font_dir, 'garibd.ttf'), 28, encoding="unic")


def list_slice(lst, n):
    """
    :param lst: list object
    :param n: number of element per group
    :return:
    n = 5
    [0,4]   1
    [5,9]   2
    [10,14] 3
    """
    result = []
    start = 0
    end = n
    for i in range(0, int(len(lst) / n) + 1):
        if lst[start:end]:
            result.append(lst[start:end])
        start += n
        end += n

    return result


class Signatory(models.Model):
    _name = 'budget.signature.signatory'
    _description = 'Signatory'
    _rec_name = 'name'

    # CHOICES
    # ----------------------------------------------------------

    # BASIC FIELDS
    # ----------------------------------------------------------
    active = fields.Boolean(default=True)

    sequence = fields.Char(string="Sequence")
    name = fields.Char(string="Name")
    designation = fields.Char(string="Designation")
    remark = fields.Text(string='Remarks')

    # RELATIONSHIP
    # ----------------------------------------------------------

    signature_image = fields.Binary(attachment=True,
                                    compute='_compute_signature_image')

    @api.one
    @api.depends('name', 'designation')
    def _compute_signature_image(self):
        if not self.name or not self.designation:
            return
        jpeg_image_buffer = BytesIO()
        img = Image.new("RGBA", signature_frame_dim)
        draw = ImageDraw.Draw(img)

        # RECTANGLE 1
        rectangle_box = ((1, 1), (signature_box_dim[0], signature_box_dim[1] * .20))
        draw.rectangle(rectangle_box, fill=(175, 220, 126), outline='black')
        self.draw_text(draw, rectangle_box, arial_bold, self.designation.upper())

        # RECTANGLE 2
        rectangle_box = ((rectangle_box[0][0], rectangle_box[1][1]),
                         (rectangle_box[1][0], rectangle_box[1][1] + signature_box_dim[1] * .25))
        draw.rectangle(rectangle_box, fill='white', outline='black')
        self.draw_text(draw, rectangle_box, arial_bold, self.name.title())

        # RECTANGLE 3
        rectangle_box = ((rectangle_box[0][0], rectangle_box[1][1]),
                         (rectangle_box[1][0], rectangle_box[1][1] + signature_box_dim[1] * .35))
        draw.rectangle(rectangle_box, fill='white', outline='black')

        # RECTANGLE 4
        rectangle_box = ((rectangle_box[0][0], rectangle_box[1][1]),
                         (rectangle_box[1][0], rectangle_box[1][1] + signature_box_dim[1] * .20))
        draw.rectangle(rectangle_box, fill='white', outline='black')
        text = "___/___/{}".format(fields.Date.from_string(fields.Date.today()).year)
        self.draw_text(draw, rectangle_box, arial_narrow, text)

        self.draw_border(draw, ((1, 1), signature_box_dim), 2)

#        img.save(os.path.join(font_dir, 'test.png'))
        img.save(jpeg_image_buffer, format="PNG")
        self.signature_image = base64.b64encode(jpeg_image_buffer.getvalue())

    # MISC
    # ----------------------------------------------------------
    @api.model
    def draw_text(self, draw, box, font, msg):
        w, h = font.getsize(msg)

        box_w = box[1][0] - box[0][0]
        box_h = box[1][1] - box[0][1]

        mid_w = (box_w - w) / 2
        mid_h = (box_h - h) / 2
        draw.text((box[0][0] + mid_w, box[0][1] + mid_h), msg, fill="black", font=font)

    @api.model
    def draw_border(self, draw, dim=None, width=1):
        draw.line(((dim[0][0], dim[0][1]), (dim[1][0], dim[0][1])), fill='black', width=width)
        draw.line(((dim[1][0], dim[0][1]), (dim[1][0], dim[1][1])), fill='black', width=width)
        draw.line(((dim[1][0], dim[1][1]), (dim[0][0], dim[1][1])), fill='black', width=width)
        draw.line(((dim[0][0], dim[1][1]), (dim[0][0], dim[0][1])), fill='black', width=width)

    @api.model
    def combine_horizontal(self, horizontal_images):
        allowed_number_of_row = 2
        offset = 50
        if len(horizontal_images) > allowed_number_of_row:
            raise ValidationError('only {} signatures are allowed in a row'.format(allowed_number_of_row))

        w, h = horizontal_images[0].size
        horizontal_image = Image.new('RGBA', ((w * allowed_number_of_row) + (offset * (allowed_number_of_row - 1)), h))

        x_offset = 0
        for im in horizontal_images:
            horizontal_image.paste(im, (x_offset, 0))
            x_offset += im.size[0] + offset

        return horizontal_image

    @api.model
    def combine_vertical(self, vertical_images):
        offset = 50

        w, h = vertical_images[0].size
        count_image = len(vertical_images)
        vertical_image = Image.new('RGBA', (w, (h * count_image) + (offset * (count_image - 1))))

        y_offset = 0
        for im in vertical_images:
            vertical_image.paste(im, (0, y_offset))
            y_offset += im.size[1] + offset

        return vertical_image

    @api.model
    def create_signatories(self, ids):
        signatory_images = self.search([('id', 'in', ids)], order='sequence asc').mapped('signature_image')
        images = [Image.open(BytesIO(base64.b64decode(image))) for image in signatory_images]

        grouped = list_slice(images, 2)
        combined_horizontal = []
        for group in grouped:
            combined_horizontal.append(self.combine_horizontal(group))

        combined_vertical = self.combine_vertical(combined_horizontal)

        return combined_vertical
