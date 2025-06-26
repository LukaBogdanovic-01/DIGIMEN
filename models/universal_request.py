from jsonschema import ValidationError
from odoo import models, fields, api

class UniversalRequest(models.Model):
    _name = 'universal.request'
    _description = 'Univerzalni poslovni zahtjev'

    name = fields.Char(string="Naziv zadatka", required=True)
    description = fields.Text(string="Opis")
    status = fields.Selection([
        ('draft', 'Kreiran'),
        ('approved', 'Odobren'),
        ('done', 'Završen'),
        ('rejected', 'Odbijen')
    ], string="Status", default='draft')
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], string="Prioritet", default='medium')
    deadline = fields.Date(string="Rok")
    assigned_user_id = fields.Many2one('res.users', string="Dodijeljeni korisnik")
    created_by_id = fields.Many2one('res.users', string="Kreator", default=lambda self: self.env.user)
    request_type_id = fields.Many2one('request.type', string="Šablon zahtjeva")

    template_description = fields.Text(compute='_compute_template_values', string="Opis (šablon)")
    template_priority = fields.Char(compute='_compute_template_values', string="Prioritet (šablon)")
    template_assigned_user = fields.Char(compute='_compute_template_values', string="Izvršilac (šablon)")

    project_id = fields.Many2one('project.project', string="Projekat")
    goals_id = fields.Many2one('code.book', string="Ciljevi")
    attachment_file = fields.Binary(string="Dokument")
    attachment_filename = fields.Char(string="Naziv fajla")





    @api.depends('request_type_id')
    def _compute_template_values(self):
        for rec in self:
            rec.template_description = rec.request_type_id.default_description or ''
            rec.template_priority = dict(rec.request_type_id._fields['default_priority'].selection).get(rec.request_type_id.default_priority, '') if rec.request_type_id.default_priority else ''
            rec.template_assigned_user = rec.request_type_id.default_assigned_user_id.name if rec.request_type_id.default_assigned_user_id else ''



    def _check_group(self, group_xml_id):
        if not self.env.user.has_group(group_xml_id):
            raise ValidationError("Nemate pravo da izvršite ovu radnju.")
        
    def _check_any_group(self, group_xml_ids):
        if not any(self.env.user.has_group(g) for g in group_xml_ids):
            raise ValidationError("Nemate pravo da izvršite ovu radnju.")



    def action_approve(self):
        self._check_any_group([
            'universal_request_manager.group_manager',
            'universal_request_manager.group_director'
        ])
        self.status = 'approved'

    def action_done(self):
        self._check_group('universal_request_manager.group_director')
        self.status = 'done'

    def action_reject(self):
        self._check_group('universal_request_manager.group_director')
        self.status = 'rejected'


    @api.constrains('request_type_id')
    def _check_request_type_access(self):
        for rec in self:
            allowed_groups = rec.request_type_id.allowed_group_ids.ids
            user_groups = self.env.user.groups_id.ids
            if allowed_groups and not any(group_id in user_groups for group_id in allowed_groups):
                raise ValidationError("Nemate pravo da koristite ovu vrstu zahtjeva.")
            








class RequestType(models.Model):
    _name = 'request.type'
    _description = 'Tip zahtjeva'

    name = fields.Char(string="Naziv tipa", required=True)
    allowed_group_ids = fields.Many2many('res.groups', string="Dozvoljene grupe")

    default_description = fields.Text(string="Podrazumijevani opis")
    default_priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], string="Podrazumijevani prioritet")
    default_assigned_user_id = fields.Many2one('res.users', string="Podrazumijevani izvršilac")
    required_documents = fields.Text(string="Tražena dokumentacija")
    requires_signature = fields.Boolean(string="Potreban fizički potpis")
    approval_responsible_group_id = fields.Many2one('res.groups', string="Grupa odgovorna za odobrenje")
    estimated_duration_days = fields.Integer(string="Procijenjeno trajanje (u danima)")
    user_note = fields.Text(string="Napomena za korisnika")

    show_deadline = fields.Boolean(string="Prikaži Rok", default=True)
    show_description = fields.Boolean(string="Prikaži Opis", default=True)
    show_priority = fields.Boolean(string="Prikaži Prioritet", default=True)
    show_assigned_user = fields.Boolean(string="Prikaži Dodijeljenog korisnika", default=True)



    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []

        user_groups = self.env.user.groups_id.ids
        args += ['|', ('allowed_group_ids', '=', False), ('allowed_group_ids', 'in', user_groups)]

        return super().name_search(name=name, args=args, operator=operator, limit=limit)


class CodeBook(models.Model):
    _name = 'code.book'
    _description = 'Šifarnik'

    name = fields.Char(string="Naziv šifre", required=True)




