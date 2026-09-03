# -*- coding: utf-8 -*-
from odoo import models, fields


class DscEjemplo(models.Model):
    _name = 'dsc.ejemplo'
    _description = 'Modelo de ejemplo DSC'

    name = fields.Char(string='Nombre', required=True)
    descripcion = fields.Text(string='Descripción')
    activo = fields.Boolean(string='Activo', default=True)
