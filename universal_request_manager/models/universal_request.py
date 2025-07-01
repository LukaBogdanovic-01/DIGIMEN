from jsonschema import ValidationError
from odoo import models, fields, api

class UniversalRequest(models.Model):
    _name = 'universal.request'
    _description = 'Univerzalni poslovni zahtjev'

    name = fields.Char(string="Naziv zadatka", required=True)
    description = fields.Html(string="Opis")
    description_text = fields.Text(compute='_compute_description_text', store=True)
    proces = fields.Many2one('code.book.proces', string="Proces")
    tag_ids = fields.Many2many('project.tag', string="Tagovi")
    status_sequence = fields.Integer(compute="_compute_status_sequence", store=True)
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
    attachment_preview_url = fields.Html(
        string="Pregled dokumenta",
        compute='_compute_attachment_preview_url',
        sanitize=False
    )
    crm_lead_id = fields.Many2one('crm.lead', string="CRM Lead")
    show_approve_button = fields.Boolean(compute="_compute_show_approve_button")
    show_request_fields = fields.Boolean(compute="_compute_show_custom_fields")

    @api.depends('request_type_id')
    def _compute_show_custom_fields(self):
        for rec in self:
            rec.show_custom_fields = bool(rec.request_type_id)

    @api.depends('status')
    def _compute_show_approve_button(self):
        for rec in self:
            rec.show_approve_button = rec.status == 'approval'



    @api.depends('description')
    def _compute_description_text(self):
        for rec in self:
            rec.description_text = rec.description and rec.description.replace('<br>', '\n').replace('<p>', '').replace('</p>', '') or ''

    @api.depends('request_type_id')
    def _compute_template_values(self):
        for rec in self:
            rec.template_description = rec.request_type_id.default_description or ''
            rec.template_priority = dict(rec.request_type_id._fields['default_priority'].selection).get(rec.request_type_id.default_priority, '') if rec.request_type_id.default_priority else ''
            rec.template_assigned_user = rec.request_type_id.default_assigned_user_id.name if rec.request_type_id.default_assigned_user_id else ''

        
    def _check_any_group(self, group_xml_ids):
        if not any(self.env.user.has_group(g) for g in group_xml_ids):
            raise ValidationError("Nemate pravo da izvršite ovu radnju.")




    @api.constrains('request_type_id')
    def _check_request_type_access(self):
        for rec in self:
            allowed_groups = rec.request_type_id.allowed_group_ids.ids
            user_groups = self.env.user.groups_id.ids
            if allowed_groups and not any(group_id in user_groups for group_id in allowed_groups):
                raise ValidationError("Nemate pravo da koristite ovu vrstu zahtjeva.")
            

    @api.depends('status')
    def _compute_status_sequence(self):
        order_map = {
            'inbox': 0,
            'submitted': 1,
            'approval': 2,
            'approved': 3,
            'rejected': 4,
            'archived': 5,
        }
        for rec in self:
            rec.status_sequence = order_map.get(rec.status, 99)

    @api.model
    def _get_all_statuses(self):
        return [
            ('inbox', 'Inbox'),
            ('submitted', 'Zadaci'),
            ('approval', 'Odobrava'),
            ('approved', 'Planovi'),
            ('rejected', 'Ciljevi'), 
            ('archived', 'Arhiva'),
        ]


    status = fields.Selection(
        selection=_get_all_statuses,
        string="Status",
        default='inbox',
        group_expand='_expand_status'
    )

    @api.model
    def _expand_status(self, values, domain, order=None):
        return [key for key, _ in self._get_all_statuses()]



    def action_convert_to_task(self):
        self._check_any_group([
            'universal_request_manager.group_manager',
            'universal_request_manager.group_director',
            'base.group_system'
        ])
        self.status = 'submitted'


    def get_attachment_url(self):
            for rec in self:
                if rec.attachment_file:
                    return f"/web/content?model=universal.request&id={rec.id}&field=attachment_file&filename_field=attachment_filename&download=true"
                return ''

    @api.depends('attachment_file', 'attachment_filename')
    def _compute_attachment_preview_url(self):
        for rec in self:
            if rec.attachment_file:
                rec.attachment_preview_url = (
                    f'<a href="/web/content?model=universal.request&id={rec.id}&field=attachment_file&filename_field=attachment_filename" '
                    f'target="_blank" style="color:#875A7B;text-decoration:underline;">📄 Otvori dokument</a>'
                )
            else:
                rec.attachment_preview_url = ''




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
    _description = 'Šifarnik za Ciljeve'

    name = fields.Char(string="Naziv šifre", required=True)


class CodeBook(models.Model):
    _name = 'code.book.proces'
    _description = 'Šifarnik za Proces'

    name = fields.Char(string="Naziv šifre", required=True)

class Tags(models.Model):
    _name = 'project.tag'
    _description = 'Tagovi'

    name = fields.Char(string="Naziv taga", required=True)



