# -*- coding: utf-8 -*-

from openerp import api, models, fields


class BackgroundForm(models.Model):
    _name = 'apiux.background.form'

    # ANTECEDENTES PERSONALES

    nombre = fields.Char('Nombre')
    _rec_name = 'nombre_completo'
    apellido_paterno = fields.Char('Apellido paterno')
    apellido_materno = fields.Char('Apellido materno')
    rut = fields.Char('RUT')
    estado_civil_options = [('Soltero', 'Soltero'), ('Casado', 'Casado'
                                                     ), ('Divorciado', 'Divorciado'), ('Viudo',
                                                                                       'Viudo')]
    estado_civil = fields.Selection(estado_civil_options, 'Estado civil'
                                    )
    cargas = fields.Char('Cargas/Hijos')
    direccion = fields.Char('Direcccion particular')
    comuna = fields.Char('Comuna')
    telefono_fijo = fields.Char('Telefono fijo')
    correo = fields.Char('Correo electronico')
    nacimiento = fields.Char('Fecha nacimiento')
    nacionalidad = fields.Char('Nacionalidad')
    edad = fields.Char('Edad')
    ciudad = fields.Char('Ciudad')
    telefono_movil = fields.Char('Telefono movil')

    # ENTIDAD PREVISIONAL

    afp = fields.Char('AFP')
    salud_options = [('Fonasa', 'Fonasa'), ('Isapre', 'Isapre')]
    salud = fields.Selection(salud_options, 'Salud')
    nombre_isapre = fields.Char('Nombre Isapre')
    cot_pactada = fields.Float('Cotizacion pactada (UF)')

    # OTROS

    tipo_cuenta_options = [('Cuenta corriente', 'Cuenta corriente'),
                           ('Cuenta vista', 'Cuenta vista'),
                           ('Cuenta RUT', 'Cuenta RUT')]
    tipo_cuenta = fields.Selection(tipo_cuenta_options, 'Tipo de cuenta'
                                   )
    nombre_banco = fields.Char('Nombre banco')
    numero_cuenta = fields.Char('Numero de cuenta')
    nombre_emergencia = fields.Char('Nombre')
    parentezco_emergencia = fields.Char('Parentezco')
    telefono_fijo_emergencia = fields.Char('Telefono fijo')
    telefono_movil_emergencia = fields.Char('Telefono movil')

    # DOCUMENTACION

    cedula_identidad_link = fields.Char('Cedula de identidad')
    certificado_afp_link = fields.Char('Certificado AFP')
    cv_link = fields.Char('Curriculum Vitae')
    cerfificado_isapre_link = fields.Char('Certificado Isapre/Fonasa')
    titulos_links = fields.Char('Titulo/s')  # crear modulo titulo y cambiar field a one2many
    acreditaciones_links = \
        fields.Char('Acreditaciones o Certificaciones')  # crear modulo acreditaciones y cambiar field a one2many

    # CONOCIMIENTOS TECNICOS

    titulo_academico = fields.Char('Titulo academico')
    institucion_academica = fields.Char('Institucion academica')
    fecha_titulacion = fields.Char('Fecha titulacion')
    lenguajes_de_programacion = fields.Char('Lenguajes de programacion')
    frameworks_backend = fields.Char('Frameworks backend')
    mobile = fields.Char('Mobile')
    web = fields.Char('Web')
    frameworks_frontend = fields.Char('Frameworks frontend')
    integracion_servicios = \
        fields.Char('Plataformas de integracion y servicios')
    plataformas_gestion_procesos = \
        fields.Char('Plataformas de gestion y procesos (BPM)')
    plataformas_documental_captura = \
        fields.Char('Plataformas de gestion documental y captura')
    plataformas_etl_informacion = \
        fields.Char('Plataformas de ETL y analisis de informacion')
    plataformas_gestion_web = \
        fields.Char('Plataformas de gestion de contenido WEB')
    plataformas_cloud = fields.Char('Plataforma Cloud')
    bases_datos = fields.Char('Bases de datos')
    sistemas_operativos_redes = \
        fields.Char('Sistemas operativos y redes')
    gestion_proyectos = fields.Char('Gestion de proyectos')
    nombre_completo = fields.Char(compute='comp_name', store=True)
    solicitante_id = fields.Many2one('hr.onboard', 'onboard')

    @api.depends('nombre', 'apellido_paterno', 'apellido_materno')
    def comp_name(self):
        self.nombre_completo = (self.nombre or '') + ' ' \
                               + (self.apellido_paterno or '') + ' ' \
                               + (self.apellido_materno or '')
