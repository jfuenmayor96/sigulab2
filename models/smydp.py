#------------------------------------ Modulo de Sustancias, materiales y desechos peligrosos -------------------------------------------

##############################################################################
#
#                     TABLAS DEL CATALOGO DE SUSTANCIAS
#
###############################################################################

#t_Unidades_de_medida: Tabla de unidades de medida de las sustancias (ml, l, g, kg, etc.)
db.define_table(
    #Nombre de la entidad
    't_Unidad_de_medida',

    #Atributos;
    Field('f_nombre', 'string', requires=IS_NOT_EMPTY(), label=T('Nombre')),
    Field('f_abreviatura', 'string', requires=IS_NOT_EMPTY(), label=T('Abreviatura'))
    )

#t_Sustancia: Tabla de sustancias de la cual se obtiene informacion del listado (catalogo de sustancias)
db.define_table(
    #Nombre de la entidad
    't_Sustancia',

    #Atributos;
    Field('f_nombre', 'string', requires=IS_NOT_EMPTY(), label=T('Nombre')),

    Field('f_cas', 'string', requires=[IS_NOT_EMPTY(), IS_MATCH('^[0-9]+\-[0-9]+\-[0-9]+$',
          error_message='El CAS debe contener tres números separados entre sí por guiones. Por ejemplo, 7732-18-5')],
          unique=True, label=T('CAS')),

    Field('f_pureza', 	'integer',	requires=IS_INT_IN_RANGE(0, 101), label=T('Pureza')),

    Field('f_estado', 'list:string',requires=IS_IN_SET(['Sólido','Líquido','Gaseoso']), 
          widget=SQLFORM.widgets.options.widget, label=T('Estado')),

    Field('f_control', 'list:string',requires=IS_IN_SET(['N/A','RL4','RL7', 'RL4 y RL7']), 
          widget=SQLFORM.widgets.options.widget, label=T('Control')),

    # *!* La unidad no va aqui, porque alguien podria querer solicitar la sustancia 
    # en ml porque es muy poca y estaria obligada a usar una unidad 
    #Field('f_unidad', 'list:string',requires=IS_IN_SET(['kg','g','l', 'ml']), 
    # widget=SQLFORM.widgets.options.widget, label=T('Unidad')),

    Field('f_peligrosidad', 'list:string',
          requires=IS_IN_SET(['Inflamable','Tóxico','Tóxico para el ambiente',
                    'Corrosivo','Comburente','Nocivo','Explosivo','Irritante'],
          multiple = True), widget=SQLFORM.widgets.checkboxes.widget, 
          label=T('Peligrosidad')),
    
    # Hoja de seguridad (archivo pdf)
    Field('f_hds','upload',requires=IS_NULL_OR(IS_UPLOAD_FILENAME(extension='pdf')),
          label=T('Hoja de seguridad')),
    # Agrega los campos adicionales created_by, created_on, modified_by, modified_on para los logs de la tabla
    auth.signature
    )

db.t_Sustancia.id.readable=False
db.t_Sustancia.id.writable=False
db.t_Sustancia.f_hds.readable=(auth.has_membership('Gestor de SMyDP') or \
                               auth.has_membership('WEBMASTER')) #-*-* Chequear permisos aqui
db.t_Sustancia._singular='Catálogo de Sustancias'
db.t_Sustancia._plural='Catálogo de Sustancias'


##############################################################################
#
#                     TABLAS DEL INVENTARIO Y BITACORA
#
###############################################################################


#t_Inventario: Tabla de la entidad debil Inventario que contiene la existencia de 
# cada sustancia en cada espacio fisico
db.define_table(
    #Nombre de la entidad
    't_Inventario',

    #Atributos;

    # Cantidades (el excedente es calculado dinamicamente como existencia - uso interno)
    Field('f_existencia', 'double', requires=IS_NOT_EMPTY(), label=T('Existencia')),

    Field('f_uso_interno', 'double', requires=IS_NOT_EMPTY(), label=T('Uso interno')),
    
    Field('f_medida', 'reference t_Unidad_de_medida',
          requires=IS_IN_DB(db, db.t_Unidad_de_medida.id, '%(f_nombre)s', zero=None), 
          label=T('Unidad de medida'), notnull=True),
    
    # Referencias a otras tablas
    Field('espacio', 'reference espacios_fisicos',
          requires=IS_IN_DB(db, db.espacios_fisicos.id, '%(nombre)s', zero=None), 
          label=T('Espacio Físico'), notnull=True),
    
    Field('sustancia', 'reference t_Sustancia',
          requires=IS_IN_DB(db, db.t_Sustancia.id, '%(f_nombre)s', zero=None), 
          label=T('Sustancia'), notnull=True),
    
    # Agrega los campos adicionales created_by, created_on, modified_by, modified_on 
    # para los logs de la tabla
    auth.signature
    )

# *!* Ver not nulls y constraints de t_Bitacora

#t_Bitacora: Tabla de la bitacora de los movimientos en los inventarios de todos 
# los espacios fisicos
db.define_table(
    #Nombre de la entidad
    't_Bitacora',

    #Atributos;

    # Cantidad ingresada o egresada
    Field('f_cantidad', 'double', requires=IS_NOT_EMPTY(), label=T('Cantidad')),

    # Concepto del ingreso, egreso o cambio en el inventario
    Field('f_concepto', 'list:string', label=T('Calidad'),
          requires=IS_IN_SET(['Ingreso','Egreso']), 
          widget=SQLFORM.widgets.options.widget),
    
    # Tipo de ingreso de la sustancia (Null si f_concepto no es Ingreso) *!*
    Field('f_tipo_ingreso', 'list:string', label=T('Tipo de ingreso'),
          requires=IS_IN_SET(['Compra','Suministrado por almacén','Otorgado por otra sección']), 
          widget=SQLFORM.widgets.options.widget),

    # Tipo de egreso de la sustancia (Null si f_concepto no es Egreso) *!*
    Field('f_tipo_egreso', 'list:string', label=T('Tipo de egreso'),
          requires=IS_IN_SET(['Docencia','Investigación','Extensión']), 
          widget=SQLFORM.widgets.options.widget),
        

    Field('f_uso_interno', 'double', requires=IS_NOT_EMPTY(), label=T('Uso interno')),
    
    # Referencias a otras tablas

    Field('f_medida', 'reference t_Unidad_de_medida',
          requires=IS_IN_DB(db, db.t_Unidad_de_medida.id, '%(f_nombre)s', zero=None), 
          label=T('Unidad de medida'), notnull=True),
    
    # Instancia del servicio en el que se empleara la sustancia egresada
    Field('f_servicio', 'reference servicios',
          requires=IS_IN_DB(db, db.servicios.id, '%(nombre)s', zero=None), 
          label=T('Servicio')),
    
    # Referencia hacia el inventario al cual pertenece el registro de la bitacora
    Field('f_inventario', 'reference t_Inventario',
          requires=IS_IN_DB(db, db.t_Inventario.id, zero=None), 
          label=T('Inventario'), notnull=True),
    
    # Agrega los campos adicionales created_by, created_on, modified_by, modified_on 
    # para los logs de la tabla
    auth.signature
    )

##############################################################################
#
#                     TABLAS DE SOLICITUDES DE SUSTANCIAS
#
###############################################################################

# *!* revisar todos los campos y sus contraints
# *!* poner los mismos nombres en el pdf UL04-18-049 Inf complementaria sobre Solicitudes  Sust

#t_Solicitud: Tabla con los datos de solicitudes de sustancias entre espacios fisicos
db.define_table(
    #Nombre de la entidad
    't_Solicitud_smydp',

    #Atributos;

    Field('f_cantidad', 'double', requires=IS_NOT_EMPTY(), label=T('Cantidad')),

    # Cantidad de sustancia que ya ha sido prometida por otros espacios al aceptar
    # la solicitud
    Field('f_cantidad_confirmada', 'double', requires=IS_NOT_EMPTY(), label=T('Cantidad')),

    Field('f_medida', 'reference t_Unidad_de_medida',
          requires=IS_IN_DB(db, db.t_Unidad_de_medida.id, '%(f_nombre)s', zero=None), 
          label=T('Unidad de medida'), notnull=True),
    
    Field('f_estatus', 'list:string', widget=SQLFORM.widgets.options.widget, 
          requires=IS_IN_SET(['Caducada','En espera','Completada', 'Por entregar', 
                            'Por recibir', 'Prestamo por devolver']), 
          label=T('Estatus de la solicitud')),
    
    Field('f_uso', 'list:string',requires=IS_IN_SET(['Docencia','Investigación','Extensión']), 
          widget=SQLFORM.widgets.options.widget, label=T('Uso de la sustancia')),
    
    Field('f_justificacion', 'string', label=T('Justificación')),

    Field('f_preferencia', 'list:string',requires=IS_IN_SET(['Cesión','Préstamo']), 
          widget=SQLFORM.widgets.options.widget, label=T('Preferencia')),
    
    Field('f_fecha_caducidad', 'string', requires=IS_DATE(format=T('%d/%m/%Y'), 
          error_message='Debe tener el siguiente formato: dd/mm/yyyy'), notnull=True, 
          label=T('Fecha de caducidad')),
    
    # Referencias a otras tablas
    Field('f_espacio', 'reference espacios_fisicos',
          requires=IS_IN_DB(db, db.espacios_fisicos.id, '%(nombre)s', zero=None), 
          label=T('Espacio solicitante'), notnull=True),
    
    Field('f_sustancia', 'reference t_Sustancia',
          requires=IS_IN_DB(db, db.t_Sustancia.id, '%(f_nombre)s', zero=None), 
          label=T('Sustancia'), notnull=True),
    
    Field('f_solicitante', 'reference t_Personal', 
            requires=IS_IN_DB(db, db.t_Personal.id, '%(f_email)s', zero=None)),
    auth.signature
    )


#t_Respuesta: Respuestas a la solicitud de sustancias
db.define_table(
    #Nombre de la entidad
    't_Respuesta',

    #Atributos;

    # Cantidad a suministrar. Vacio si la respuesta es una negacion
    Field('f_cantidad', 'double', label=T('Cantidad')),

    # Unidad de medida de la cantidad indicada (None si f_cantidad lo es y viceversa *!*)
    Field('f_medida', 'reference t_Unidad_de_medida',
          requires=IS_IN_DB(db, db.t_Unidad_de_medida.id, '%(f_nombre)s', zero=None), 
          label=T('Unidad de medida')),
    
    # Indica si la solicitud fue aceptada o rechazada
    Field('f_tipo_respuesta', 'list:string', requires=IS_IN_SET(['Negación','Aceptación']), 
        label=T('Respuesta a la solicitud')),
    
    # Almacena información como la causa de la negación de la solicitud
    Field('f_justificacion', 'string', label=T('Justificación')),

    Field('f_uso', 'list:string',requires=IS_IN_SET(['Docencia','Investigación','Extensión']), 
          widget=SQLFORM.widgets.options.widget, label=T('Uso de la sustancia')),
    
    # En que terminos se esta aceptando dar la sustancia
    Field('f_calidad', 'list:string',requires=IS_IN_SET(['Cesión','Préstamo']), 
          widget=SQLFORM.widgets.options.widget, label=T('Calidad')),
    
    # Fecha en que se recibe la sustancia solicitada
    Field('f_fecha_recepcion', 'datetime', requires = IS_DATE(format=('%d-%m-%Y')),
          label=T('Fecha de devolución')),

    # Fecha en que se hace constar la devolucion de la sustancia
    Field('f_fecha_devolucion', 'datetime', requires = IS_DATE(format=('%d-%m-%Y')),
          label=T('Fecha de devolución')),

    # Indica la fecha tope en que debe devolverse el material prestado (solo si 
    # f_calidad es "prestamo" *!*)
    Field('f_fecha_tope_devolucion', 'string', requires=IS_DATE(format=T('%d/%m/%Y'), 
          error_message='Debe tener el siguiente formato: dd/mm/yyyy'),
          label=T('Fecha tope para la devolución')),

    # Referencias a otras tablas
    
    # Espacio que responde a la solicitud
    Field('f_espacio', 'reference espacios_fisicos',
          requires=IS_IN_DB(db, db.espacios_fisicos.id, '%(nombre)s', zero=None), 
          label=T('Espacio solicitante'), notnull=True),

    # Responsable que entrega la sustancia
    Field('f_responsable_entrega', 'reference t_Personal', 
          requires=IS_IN_DB(db, db.t_Personal.id, '%(f_email)s', zero=None)),

    # Responsable que hace constar la recepcion de la sustancia solicitada
    Field('f_responsable_recepcion', 'reference t_Personal', 
          requires=IS_IN_DB(db, db.t_Personal.id, '%(f_email)s', zero=None)),

    # Responsable que hace constar la devolucion
    Field('f_responsable_devolucion', 'reference t_Personal', 
          requires=IS_IN_DB(db, db.t_Personal.id, '%(f_email)s', zero=None)),

    # ID de la solicitud a la que se esta dando respuesta
    Field('f_solicitud', 'reference t_Solicitud_smydp',
          requires=IS_IN_DB(db, db.t_Solicitud_smydp.id, zero=None), 
          label=T('Solicitud'), notnull=True),
    
    # Almacena el id del responsable que acepta o niega la solicitud y fecha en que lo hace
    auth.signature
    )


