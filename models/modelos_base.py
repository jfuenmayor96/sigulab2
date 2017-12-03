# Usemos la siguiente convencion:
#
# Los nombres de cada tabla seran en minusculas, separados con _ y en plural.
#
# Los nombres de los atributos seran en minusculas y singular, a menos de que se trate de una lista, en ese caso
# se intentara tomar un nombre distinto al de una tabla
#
# Si un atributo tiene como referencia a un record de otra tabla, se le agregara el sufijo _<tabla> si es dificil
# identificar que se trata de una referencia, si no es asi, se adoptara la convencion normal de atributos

######################################################################################################################
#
# Tablas principales de los modulos
# Se definira antes que las tablas de autenticacion porque son necesarias para estas
#
######################################################################################################################

# Tabla de Sedes, necesaria para las Dependencias


db.define_table(
    'sedes',
    Field('nombre', 'string', unique=True, notnull=True, label=T('Nombre de la Sede'))
)

# Tabla de Dependencias, Incluira la Direccion, los laboratorios y sus secciones y las coordinaciones

db.define_table(
    #Nombre de la entidad
    'dependencias',
    #Atributos;
    Field('nombre', 'string', notnull=True, label=T('Nombre')),

    Field('email', 'string', requires=IS_EMAIL(error_message='Debe tener un formato válido. EJ: example@org.com'), label=T('Correo')),

    # Auto-Referencia
    Field('unidad_de_adscripcion', 'reference dependencias', requires=False, label=T('Unidad de Adscripción')),

    Field('id_sede', 'reference sedes', requires=IS_IN_DB(db, db.sedes.id, '%(nombre)s'), label=T('Sede')),

    Field('ext_USB', 'list:integer', label=T('Extension Telefonica USB')),

    Field('ext_interna', 'string', label=T('Extension Telefonica Interna')),

    Field('fax', 'integer', label=T('Fax')),

    Field('pagina_web', 'string', label=T('Pagina Web')),

    Field('id_jefe_dependencia', 'integer', label=T('Responsable')),
)

# Auto-Referencia, se definira cual dependencia es la unidad de adscripcion, esta sera una relacion de 0-1 a muchos
# una dependencia tendra adscrita varias, pero cada dependencia tendra o ninguna o una dependencia 'jefe'

# Se define fuera de la tabla para asegurar su existencia antes de ser referenciada

db.dependencias.unidad_de_adscripcion.requires = IS_EMPTY_OR(IS_IN_DB(db, db.dependencias.id, '%(nombre)s', zero=None))
db.dependencias._plural = 'Dependencias'
db.dependencias._singular = 'Dependencia'

#######################################################################################################################
#
# Tablas de Autenticacion de Usuarios
#
#######################################################################################################################

# Aqui se crearan las tablas de autenticacion, antes de ser estas definidas por web2py.
# Despues de auth = Auth(db) pero antes de auth.define_tables(username=True)
# (En el archivo 'db.py', la linea auth.define_tables(username=True) fue eliminada para ser usada aqui)

# La tabla de auth_membership funcionara como la tabla de roles, asociaremos a esta una referencia a las dependencias.
auth.settings.extra_fields['auth_membership'] = [
    Field('dependencia_asociada', 'string',
          label=T('Dependencia Asociada al Rol')),
    Field('f_personal_membership', 'string', label=T('Ci'))
]


# Definimos todas las tablas de web2py por defecto con las modificaciones hechas

auth.define_tables()

db.auth_membership.dependencia_asociada.requires = IS_IN_DB(db, db.dependencias.id, '%(nombre)s', zero=None)
db.auth_membership.dependencia_asociada.type = 'reference dependencias'
db.dependencias.id_jefe_dependencia.requires = IS_IN_DB(db, db.auth_user, '%(first_name)s %(last_name)s | %(email)s')
db.dependencias.id_jefe_dependencia.type = 'reference auth_user'

#######################################################################################################################
#
# Tabla principal del modulo de t_personal. Englobara la info de cada persona en la unidad de laboratorios. Es necesaria
# para el funcionamiento de cualquier otro modulo
#
#######################################################################################################################

db.define_table(
    #Nombre de la entidad
    't_Personal',
    #Atributos;
    Field('f_nombre',         'string',
          requires=IS_MATCH('^[a-zA-ZñÑáéíóúÁÉÍÓÚ]([a-zA-ZñÑáéíóúÁÉÍÓÚ\s]+[\s-]?[a-zA-ZñÑáéíóúÁÉÍÓÚ\s][a-zA-ZñÑáéíóúÁÉÍÓÚ\s]+)*$',
                            error_message='Debe ser no vacío y contener sólo letras, guiones o espacios.'),

          notnull=True, label=T('Nombre')),

    Field('f_apellido',         'string',
          requires=IS_MATCH('^[a-zA-ZñÑáéíóúÁÉÍÓÚ]([a-zA-ZñÑáéíóúÁÉÍÓÚ\s]+[\s-]?[a-zA-ZñÑáéíóúÁÉÍÓÚ\s][a-zA-ZñÑáéíóúÁÉÍÓÚ\s]+)*$',
                            error_message='Debe ser no vacío y contener sólo letras, guiones o espacios.'),

          notnull=True, label=T('Apellido')),

    Field('f_categoria',      'string',
          requires=IS_IN_SET(['Docente', 'Administrativo', 'Técnico', 'Obrero']), notnull=True, label=T('Categoría')),

    Field('f_cargo',          'string',
          requires=IS_NOT_EMPTY(), notnull=True, label=T('Cargo')),

    Field('f_ci',             'integer',
          requires=IS_INT_IN_RANGE(minimum=1,maximum=100000000, error_message='Número de cedula no válido.'),
          notnull=True, label=T('Cédula')),

    Field('f_email',          'string',
          requires=IS_EMAIL(error_message='Debe tener un formato válido. EJ: example@org.com'),
          notnull=True, label=T('Correo Electrónico')),

    Field('f_telefono',       'integer',  default = '00', label=T('Teléfono')),
    Field('f_pagina_web',     'string', default = 'N/A', label=T('Página web')),

    Field('f_estatus',        'string', requires=IS_IN_SET(['Activo', 'Jubilado', 'Retirado']),
          default='Activo', notnull=True, label=T('Estatus')),

    Field('f_fecha_ingreso',  'string', default='N/A', label=T('Fecha de Ingreso')),
    Field('f_fecha_salida',   'string', default='N/A', label=T('Fecha de Salida')),

    # #Referencias
     Field('f_usuario', 'reference auth_user',
           requires=IS_IN_DB(db, db.auth_user.id, '%(first_name)s %(last_name)s | %(email)s'), label=T('Usuario Asociado')),

    Field('f_dependencia', 'reference dependencias',
          requires=IS_IN_DB(db, db.dependencias, '%(nombre)s'), label=T('Pertenece A'))
    )

db.t_Personal._plural = 'Personal'
db.t_Personal._singular = 'Personal'

db.auth_membership.f_personal_membership.type = 'reference t_Personal'
db.auth_membership.f_personal_membership.requires = IS_IN_DB(db, db.t_Personal.id, '%(f_ci)s', zero=None)

#######################################################################################################################
#
# Tablas Generales
#
#######################################################################################################################


# Tabla de Espacios Fisicos, incluira el nombre, la direccion de este y bajo que dependencia esta adscrito
db.define_table(
    'espacios_fisicos',
    #Atributos;
    Field('nombre', 'string', unique=True, notnull=True, label=T('Nombre')),
    Field('direccion', 'string', unique=True, notnull=True, label=T('Direccion')),
    #Referencia (Revisar si el label es asistio o organizo)
    Field('dependencia_adscrita', 'reference dependencias',
          requires=IS_IN_DB(db, db.dependencias.id, '%(nombre)s', zero=None), label=T('Ubicacion')),
    )
db.espacios_fisicos._plural = 'Espacio Fisico'
db.espacios_fisicos._singular = 'Espacio Fisico'


#------------------------------------------------Modulo de Personal-----------------------------------------------------------------------------------------------------------------------------------------------------------

#t_Personal: Tabla de publicaciones.
db.define_table(
    #Nombre de la entidad
    't_Publicacion', 
    #Atributos;
    Field('f_anio',          'integer', requires=IS_INT_IN_RANGE(minimum=1900,maximum=2100, error_message='Introduzca un año válido'), notnull=True, label=T('Año de Publicación')),
    Field('f_arbitrada',          'boolean', requires=IS_NOT_EMPTY(), notnull=True, label=T('Arbitrada')),
    Field('f_titulo',          'string', requires=IS_NOT_EMPTY(), notnull=True, label=T('Título')),
    Field('f_autores',          'string', requires=IS_NOT_EMPTY(), notnull=True, label=T('Autores')),
    Field('f_referencia',          'string', requires=IS_NOT_EMPTY(), notnull=True, label=T('Referencia')),
    #Referencia
    Field('f_publicacion_Personal',         'reference t_Personal', requires=IS_IN_DB(db, db.t_Personal.id, '%(f_Personal)s', zero=None), label=T('Autor')),
    )

db.t_Publicacion._plural = 'Publicaciones'
db.t_Publicacion._singular = 'Publicacion'

#t_Personal: Tabla de eventos.
db.define_table(
    #Nombre de la entidad
    't_Evento', 
    #Atributos;
    Field('f_anio',          'integer', requires=IS_INT_IN_RANGE(minimum=1900,maximum=2100, error_message='Introduzca un año válido'), notnull=True, label=T('Año')),
    Field('f_lugar',          'string', requires=IS_NOT_EMPTY(), notnull=True, label=T('Lugar')),
    Field('f_titulo',          'string', requires=IS_NOT_EMPTY(), notnull=True, label=T('Título')),
    Field('f_coactores',          'string', requires=IS_NOT_EMPTY(), notnull=True, label=T('Coactores')),
    Field('f_nombre',          'string', requires=IS_NOT_EMPTY(), notnull=True, label=T('Nombre')),
    #Referencia (Revisar si el label es asistio o organizo)
    Field('f_evento_Personal',         'reference t_Personal', requires=IS_IN_DB(db, db.t_Personal.id, '%(f_Personal)s', zero=None), label=T('Asistió')),
    )

db.t_Evento._plural = 'Eventos'
db.t_Evento._singular = 'Evento'


#t_Personal: Tabla de Reconocimientos.
db.define_table(
    #Nombre de la entidad
    't_Reconocimiento', 
    #Atributos;
    Field('f_anio',          'integer', requires=IS_INT_IN_RANGE(minimum=1900,maximum=2100, error_message='Introduzca un año válido'), notnull=True, label=T('Año')),
    Field('f_referencia',          'string', requires=IS_NOT_EMPTY(), notnull=True, label=T('Referencia')),
    Field('f_otorgado_por',          'string', requires=IS_NOT_EMPTY(), notnull=True, label=T('Otorgado por')),
    #Referencia (Revisar si el label es asistio o organizo)
    Field('f_Reconocimiento_Personal',         'reference t_Personal', requires=IS_IN_DB(db, db.t_Personal.id, '%(f_Personal)s', zero=None), label=T('Obtuvo')),
    )

db.t_Reconocimiento._plural = 'Reconocimientos'
db.t_Reconocimiento._singular = 'Reconocimiento'

#t_Personal: Tabla de Historial de trabajo.
db.define_table(
    #Nombre de la entidad
    't_Historial_trabajo', 
    #Atributos;
    Field('f_periodo',          'string', requires=IS_NOT_EMPTY(), notnull=True, label=T('Periodo')),
    Field('f_organizacion',          'string', requires=IS_NOT_EMPTY(), notnull=True, label=T('Organización')),
    Field('f_cargo',          'string', requires=IS_NOT_EMPTY(), notnull=True, label=T('Cargo')),
    #Referencia (Revisar si el label es asistio o organizo)
    Field('f_Historial_trabajo_Personal',         'reference t_Personal', requires=IS_IN_DB(db, db.t_Personal.id, '%(f_Personal)s', zero=None), label=T('Posee')),
    )

db.t_Historial_trabajo._plural = 'Historial de trabajo'
db.t_Historial_trabajo._singular = 'Historial de trabajo'


#t_Personal: Tabla de Comisiones.
db.define_table(
    #Nombre de la entidad
    't_Comision', 
    #Atributos;
    Field('f_fecha',          'string', requires=IS_DATE(format=T('%d/%m/%Y'), error_message='Debe tener el siguiente formato: dd/mm/yyyy'), notnull=True, label=T('Fecha')),
    Field('f_rol',          'string', requires=IS_NOT_EMPTY(), notnull=True, label=T('Rol')),
    Field('f_nombre',          'string', requires=IS_NOT_EMPTY(), notnull=True, label=T('Nombre')),
    #Referencia (Revisar si el label es asistio o organizo)
    Field('f_Comision_Personal',         'reference t_Personal', requires=IS_IN_DB(db, db.t_Personal.id, '%(f_Personal)s', zero=None), label=T('Participó')),
    )

db.t_Comision._plural = 'Comisiones'
db.t_Comision._singular = 'Comision'

#t_Personal: Tabla de Actividades.
db.define_table(
    #Nombre de la entidad
    't_Actividad', 
    #Atributos;
    Field('f_periodo',          'string', requires=IS_NOT_EMPTY(), notnull=True, label=T('Periodo')),
    Field('f_cargo',          'string', requires=IS_NOT_EMPTY(), notnull=True, label=T('Cargo')),
    Field('f_institucion',          'string', requires=IS_NOT_EMPTY(), notnull=True, label=T('Institución')),
    #Referencia (Revisar si el label es asistio o organizo)
    Field('f_Actividad_Personal',         'reference t_Personal', requires=IS_IN_DB(db, db.t_Personal.id, '%(f_Personal)s', zero=None), label=T('Dirigió')),
    )

db.t_Actividad._plural = 'Actividades'
db.t_Actividad._singular = 'Actividad'

#t_Personal: Tabla de Materias.
db.define_table(
    #Nombre de la entidad
    't_Materia', 
    #Atributos;
    Field('f_area',          'string', requires=IS_NOT_EMPTY(), notnull=True, label=T('Area')),
    Field('f_codigo',          'string', requires=IS_NOT_EMPTY(), notnull=True, label=T('Código')),
    Field('f_nombre',          'string', requires=IS_NOT_EMPTY(), notnull=True, label=T('Nombre')),
    Field('f_periodo',          'string', requires=IS_NOT_EMPTY(), notnull=True, label=T('Periodo')),
    #Referencia (Revisar si el label es asistio o organizo)
    Field('f_Materia_Personal',         'reference t_Personal', requires=IS_IN_DB(db, db.t_Personal.id, '%(f_Personal)s', zero=None), label=T('Dirigió')),
    )

db.t_Materia._plural = 'Materias'
db.t_Materia._singular = 'Materia'

#t_Personal: Tabla de Tesis.
db.define_table(
    #Nombre de la entidad
    't_Tesis', 
    #Atributos;
    Field('f_anio',          'integer', requires=IS_INT_IN_RANGE(minimum=1900,maximum=2100, error_message='Introduzca un año válido'), notnull=True, label=T('Año')),
    Field('f_nivel',          'string', requires=IS_NOT_EMPTY(), notnull=True, label=T('Nivel')),
    Field('f_trabajo',          'string', requires=IS_NOT_EMPTY(), notnull=True, label=T('Trabajo')),
    #Referencia (Revisar si el label es asistio o organizo)
    Field('f_Tesis_Personal',         'reference t_Personal', requires=IS_IN_DB(db, db.t_Personal.id, '%(f_Personal)s', zero=None), label=T('Publicó')),
    )

db.t_Tesis._plural = 'Tesis'
db.t_Tesis._singular = 'Tesis'

#t_Personal: Tabla de Cursos.
db.define_table(
    #Nombre de la entidad
    't_Curso', 
    #Atributos;
    Field('f_anio',          'integer', requires=IS_INT_IN_RANGE(minimum=1900,maximum=2100, error_message='Introduzca un año válido'), notnull=True, label=T('Año')),
    Field('f_horas',          'integer', requires=IS_NOT_EMPTY(), notnull=True, label=T('Horas')),
    Field('f_titulo',          'string', requires=IS_NOT_EMPTY(), notnull=True, label=T('Título')),
    Field('f_dictado_por',          'string', requires=IS_NOT_EMPTY(), notnull=True, label=T('Dictado por')),
    #Referencia (Revisar si el label es asistio o organizo)
    Field('f_Curso_Personal',         'reference t_Personal', requires=IS_IN_DB(db, db.t_Personal.id, '%(f_Personal)s', zero=None), label=T('Asistió')),
    )

db.t_Curso._plural = 'Curso'
db.t_Curso._singular = 'Curso'

#t_Personal: Tabla de Trabajos.
db.define_table(
    #Nombre de la entidad
    't_Trabajo', 
    #Atributos;
    Field('f_anio',          'integer', requires=IS_INT_IN_RANGE(minimum=1900,maximum=2100, error_message='Introduzca un año válido'), notnull=True, label=T('Año')),
    Field('f_nivel',          'string', requires=IS_NOT_EMPTY(), notnull=True, label=T('Nivel')),
    Field('f_estudiantes',          'string', requires=IS_NOT_EMPTY(), notnull=True, label=T('Estudiantes')),
    Field('f_intistitucion',          'string', requires=IS_NOT_EMPTY(), notnull=True, label=T('Intistitución')),
    Field('f_nombre',          'string', requires=IS_NOT_EMPTY(), notnull=True, label=T('Nombre')),
    #Referencia (Revisar si el label es asistio o organizo)
    Field('f_Trabajo_Personal',         'reference t_Personal', requires=IS_IN_DB(db, db.t_Personal.id, '%(f_Personal)s', zero=None), label=T('Fue Parte')),
    )

db.t_Trabajo._plural = 'Trabajos'
db.t_Trabajo._singular = 'Trabajo'

#t_Personal: Tabla de Extensiones.
db.define_table(
    #Nombre de la entidad
    't_Extension', 
    #Atributos;
    Field('f_naturaleza_actividad',          'string', requires=IS_NOT_EMPTY(), notnull=True, label=T('Naturaleza de la actividad')),
    Field('f_periodo',          'string', requires=IS_NOT_EMPTY(), notnull=True, label=T('Periodo')),
    Field('f_intistitucion',          'string', requires=IS_NOT_EMPTY(), notnull=True, label=T('Intistitución')),
    Field('f_nombre',          'string', requires=IS_NOT_EMPTY(), notnull=True, label=T('Nombre')),
    #Referencia (Revisar si el label es asistio o organizo)
    Field('f_Extension_Personal',         'reference t_Personal', requires=IS_IN_DB(db, db.t_Personal.id, '%(f_Personal)s', zero=None), label=T('Realizó')),
    )

db.t_Extension._plural = 'Extensiones'
db.t_Extension._singular = 'Extension'

#######################################################################################################################
#
# Tablas de Servicios, involucran cada uno de las entidades que manejan la creacion y edicion de las fichas de servicio
#
#######################################################################################################################

# tipos_servicios: Tabla que engloba todos los tipos posibles de servicios
db.define_table(
    'tipos_servicios',
    Field('nombre', 'string', unique=True, notnull=True, label=T('Nombre')),
)

db.tipos_servicios._plural = 'Tipos'
db.tipos_servicios._singular = 'Tipo'

# categorias_servicios: Tabla que engloba todas las categorias posibles de servicios
db.define_table(
    'categorias_servicios',
    Field('nombre', 'string', unique=True, notnull=True, label=T('Nombre')),
)

db.categorias_servicios._plural = 'Categorías',
db.categorias_servicios._singular = 'Categoría'

# servicios: Catalogo de todos los Servicios agregados al sistema.
db.define_table(
    'servicios', # Nombre de la entidad
    # Atributos; Datos puntuales, Nombre, Objetivo, etc
    Field('nombre',             'string', notnull=True, label=T('Nombre')),
    Field('objetivo',           'string', notnull=True, label=T('Objetivo')),
    Field('alcance',            'string', notnull=True, label=T('Alcance')),
    Field('metodo',             'string', notnull=True, label=T('Método')),
    Field('rango',              'string', label=T('Rango')),
    Field('incertidumbre',      'string', label=T('Incertidumbre')),
    Field('item_ensayar',       'string', notnull=True, label=T('Item a Ensayar')),
    Field('requisitos',         'text', notnull=True, label=T('Requisitos')),
    Field('resultados',         'text', notnull=True, label=T('Resultados')),

    # Fecha de Agregacion.
    Field('fecha_de_agregacion', 'datetime', requires=IS_DATETIME(), default=request.now),

    # Tipo y Categoria
    Field('tipo',               'reference tipos_servicios',
          requires=IS_IN_DB(db, db.tipos_servicios, '%(nombre)s'), label=T('Tipo')),

    Field('categoria',          'reference categorias_servicios',
          requires=IS_IN_DB(db, db.categorias_servicios, '%(nombre)s'), label=T('Categoría')),

    # Funciones
    Field('docencia',           'boolean', default=False, label=T('Docencia')),
    Field('investigacion',      'boolean', default=False, label=T('Investigación')),
    Field('gestion',            'boolean', default=False, label=T('Gestión')),
    Field('extension',          'boolean', default=False, label=T('Extensión')),

    Field('visibilidad',        'boolean', default=True, label=T('Visible')),

    # Prof Encargado
    Field('responsable',        'reference t_Personal',
          requires=IS_IN_DB(db, db.t_Personal.id, '%(f_nombre)s'), label=T('Encargado')),

    # Dependencia
    Field('dependencia',        'reference dependencias',
          requires=IS_IN_DB(db, db.dependencias.id, '%(nombre)s'), label=T('Dependencias')),

    # Ubicacion Fisica
    Field('ubicacion',          'reference espacios_fisicos',
          requires=IS_IN_DB(db, db.espacios_fisicos.id, '%(nombre)s'), label=T('Ubicación Física')),
)

db.servicios._plural = 'Servicios'
db.servicios._singular = 'Servicio'

##################################################################################################
#                                                           TABLA: SOLICITUDES DE SERVICIOS
#
#   Esta tabla es el primer lugar en donde se encuentra un servicio al llenarse el formulario de
# solicitudes de servicios.
#
#################################################################################################

db.define_table(
    'propositos',
    Field('tipo', 'string', requires=IS_NOT_EMPTY())
)

db.define_table(
    'solicitudes',  

    Field('registro', 'string', requires=IS_NOT_EMPTY(), label=T('Número de Registro')),
    
    #Field('dependencia', 'reference dependencias', requires=IS_IN_DB(db, 'dependencias.id', '%(nombre)s'), label=T('Dependencia Solicitante')),

    #Field('jefe_dependencia', 'reference t_Personal', requires=IS_IN_DB(db, db.t_Personal.id, '%(f_nombre)s | %(f_email)s'), label=T('Jefe de la Dependencia Solicitante')),

    Field('responsable', 'reference t_Personal', requires=IS_IN_DB(db, db.t_Personal.id, '%(f_nombre)s | %(f_email)s'), label=T('Responsable de la Solicitud')),

    Field('fecha',   'date',
          requires=IS_DATE(format=('%d-%m-%Y')), default=request.now, notnull=True, label=T('Fecha de Solicitud')),

    Field('id_servicio_solicitud', 'reference servicios', requires=IS_IN_DB(db, db.servicios.id, '%(nombre)s'), label=T('Servicio Solicitado')),

    Field('proposito', 'reference propositos', requires=IS_IN_DB(db, db.propositos.id, '%(tipo)s'), label=T('Propósito del servicio solicitado')),

    Field('proposito_descripcion', 'string', requires=IS_NOT_EMPTY(), label=T('Descripción del propósito')),

    # Si el propósito es extensión, este campo se llena con el cliente final.
    Field('proposito_cliente_final', 'string', label=T('Cliente final del propósito')),
    
    Field('descripcion', 'string', label=T('Descripción de la Solicitud')),
    
    Field('observaciones', 'string', label=T('Observaciones de la Solicitud')),

    #Field('id_dependencia_ejecutora', 'reference dependencias', requires=IS_IN_DB(db, db.dependencias.id, '%(nombre)s'), label=T('Dependencia Ejecutora')),

    
    #
    #######################################################
    #Field('lugar_ejecucion', 'reference espacios_fisicos', requires=IS_IN_DB(db, db.espacios_fisicos.id, '%(nombre)s'), label=T('Lugar de Ejecución de Servicio')),

    #Field('jefe_dependencia_ejecutora', 'reference t_Personal', requires=IS_IN_DB(db, db.t_Personal.id, '%(f_nombre)s | %(f_email)s'), label=T('Jefe de la Dependencia Ejecutora')),
    
    

    #
    # Esto en vez de el email quizá pueda tener el id de la persona que aprobo la solicitud
    #
    # Otra cosa: esta tabla sería entonces una tabla de servicios solicitados "pendientes"
    #######################################################################################
    #Field('pendiente',     'boolean', default=True, label=T('Pendiente')),

    # estado=-1 rechazado
    # estado=0 pendiente por aprobar
    # estado=1 pendiente por ejecutar
    # estado=2 pendiente por certificar
    # estado=3 certificado

    Field('estado','integer', default=0, label=T('Estado de Solicitud')),


    Field('aprobada_por', 'string', label=T('Solicitud Aprobada Por')),

    Field('fecha_aprobacion',   'date',  label=T('Fecha de Aprobacion de Solicitud')),

    Field('elaborada_por', 'string', label=T('Solicitud Elaborada Por')),

    Field('fecha_elaboracion',   'date', label=T('Fecha de Elaboracion de Solicitud')),

)


##################################################################################################
#                                                           TABLA: CERTIFICACIONES DE SERVICIOS
#
#   Esta tabla en donde se encuentra una solicitud al llenarse el formulario de
# certificaciones de servicios.
#
#################################################################################################

db.define_table(
    'certificaciones',

    Field('registro', 'string', requires=IS_NOT_EMPTY(), label=T('Número de Registro')),
    Field('proyecto', 'string', requires=IS_NOT_EMPTY(), label=T('Número de Poyecto')),
    Field('elaborado_por', 'reference t_Personal',
          requires=IS_IN_DB(db, db.t_Personal.id, '%(f_nombre)s | %(f_email)s'), label=T('Elaborado Por')),
    Field('servicio', 'reference servicios',
          requires=IS_IN_DB(db, db.servicios.id, '%(nombre)s'), label=T('Servicio Solicitado')),
    Field('solicitud', 'reference solicitudes',
          requires=IS_IN_DB(db, db.solicitudes.id, '%(registro))s'), label=T('Solicitud a Certificar')),
    Field('fecha_certificacion',   'date',
          requires=IS_DATE(format=('%d-%m-%Y')), default = request.now, notnull=True, label=T('Fecha de Certificacion de Solicitud')),
)