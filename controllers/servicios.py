#------------------------------------------------------------------------------
#
# Controladores de las funcionalidades del modulo de Servicios
#
#
# - Erick Flejan <12-1155@usb.ve>
# - Amanda Camacho <12-10644@usb.ve>
# - David Cabeza <13-10191@usb.ve>
# - Fabiola Martínez <13-10838@usb.ve>
# - Lautaro Villalon <12-10427@usb.ve>
# - Yarima Luciani <13-10770@usb.ve>
#------------------------------------------------------------------------------
from servicios_libreria import *
import re

# Pagina principal del modulo
@auth.requires_login(otherwise=URL('modulos', 'login'))
def index():
    return dict()


@auth.requires_login(otherwise=URL('modulos', 'login'))
def usuario():
    return dict(form=auth.profile(), form2=auth.change_password())

# Tabla de servicios agregados
@auth.requires_login(otherwise=URL('modulos', 'login'))
def listado(): 

    #----- AGREGAR SERVICIO -----#

    if request.post_vars.nombreServicio and request.post_vars.envio != "edicion":

        docencia = False if not request.post_vars.docenciaServicio else True
        investigacion = False if not request.post_vars.investigacionServicio else True
        extension = False if not request.post_vars.extensionServicio else True
        gestion = False if not request.post_vars.gestionServicio else True

        servicio_nuevo = Servicio(db, request.post_vars.nombreServicio, request.post_vars.tipoServicio,
                   request.post_vars.categoriaServicio, request.post_vars.objetivoServicio,
                   request.post_vars.alcanceServicio, request.post_vars.metodoServicio,
                   request.post_vars.rangoServicio, request.post_vars.incertidumbreServicio,
                   request.post_vars.itemServicio, request.post_vars.requisitosServicio,
                   request.post_vars.resultadosServicio, docencia,
                   investigacion, gestion, extension, True,
                   request.post_vars.responsableServicio, request.post_vars.dependenciaServicio, 
                   request.post_vars.ubicacionServicio)

        servicio_nuevo.insertar()


        # Se envia el email de notificacion al agregar un servicio 

        ########################### TO DO #############################################
        #
        #            NO TIENE POR QUE SER UN ASSERT Y SI L ES QUE SEA DE ERROR
        #
        ##############################################################################

        # datos = __queries_enviar_correo()

        # nombre_y_apellido = datos[0]
        # nombre_anade = datos[1]
        # dependencia = datos[2]
        # jefe_dependencia = datos[3]

        # OJO: VER QUE HACER CON EL TRY EXCEPT Y EL REDIRECT 

        try:
            idDependencia = db(auth.user_id == db.t_Personal.f_usuario).select(db.t_Personal.ALL)[0].f_dependencia

            dependencia = db(idDependencia == db.dependencias.id).select(db.dependencias.ALL)[0]

            jefe_dependencia = db(dependencia.id_jefe_dependencia == db.auth_user.id).select(db.auth_user.ALL)[0]

            assert(jefe_dependencia != None)
            
        except:

            return redirect(URL('servicios', 'listado'))

        nombre_y_apellido = "%s %s" % (jefe_dependencia.first_name, jefe_dependencia.last_name)

        nombre_anade = "%s %s" % (auth.user.first_name, auth.user.last_name)

        correo = '<html><head><meta charset="UTF-8"></head><body><table><tr><td><p>Hola, %s.</p><br><p>Se ha añadido un nuevo servicio. La operación fue realizada por %s, el/la cual pertenece a la dependencia de %s.</p><br><p>Para consultar dicha operación diríjase a la página web <a href="159.90.171.24">Sigulab</a></p></td></tr></table></body></html>' % (nombre_y_apellido, nombre_anade, dependencia.nombre)

        __enviar_correo(jefe_dependencia.email, 'Se ha agregado un nuevo servicio', correo)

        # Variable nombre persona que recibe el email

        # Variable nombre persona que realizo la operacion
        # nombreUsuario = auth.user.first_name + ' ' + auth.user.last_name

        # Variable rol persona que realizo la operacion
        # rolUsuario = db(auth.user_id == db.t_Personal.f_usuario).select(db.t_Personal.ALL)[0].rol   

        # Variable dependencia de la persona que realizo la operacion
        # dependenciaUsuario = db(idDependencia == db.dependencias.id).select(db.dependencias.ALL)[0].nombre

        # SI NO HAY UN PERSONAL ASOCIADO AL AUTH.USER TODO MUEREEE 

    #----- FIN AGREGAR SERVICIO -----#

    #----- EDITAR SERVICIO -----#

    elif request.post_vars.nombreServicio and request.post_vars.envio == "edicion":
        
        docencia = False if not request.post_vars.docenciaServicio else True
        investigacion = False if not request.post_vars.investigacionServicio else True
        extension = False if not request.post_vars.extensionServicio else True
        gestion = False if not request.post_vars.gestionServicio else True      

        servicio_edicion = Servicio(db)
        servicio_edicion.instanciar(request.vars.idServicioEdit)

        servicio_edicion.editar(request.post_vars.nombreServicio, request.post_vars.tipoServicio,
                   request.post_vars.categoriaServicio, request.post_vars.objetivoServicio,
                   request.post_vars.alcanceServicio, request.post_vars.metodoServicio,
                   request.post_vars.rangoServicio, request.post_vars.incertidumbreServicio,
                   request.post_vars.itemServicio, request.post_vars.requisitosServicio,
                   request.post_vars.resultadosServicio, docencia,
                   investigacion, gestion, extension, True,
                   request.post_vars.responsableServicio, request.post_vars.dependenciaServicio, 
                   request.post_vars.ubicacionServicio)

        servicio_edicion.actualizar(request.vars.idServicioEdit)

        # Se envia el email de notificacion al editar un servicio 
       
        try:
            idDependencia = db(auth.user_id == db.t_Personal.f_usuario).select(db.t_Personal.ALL)[0].f_dependencia

            dependencia = db(idDependencia == db.dependencias.id).select(db.dependencias.ALL)[0]

            jefe_dependencia = db(dependencia.id_jefe_dependencia == db.auth_user.id).select(db.auth_user.ALL)[0]

            assert(jefe_dependencia != None)
            
        except:

            return redirect(URL('listado'))

        nombre_y_apellido = "%s %s" % (jefe_dependencia.first_name, jefe_dependencia.last_name)

        nombre_anade = "%s %s" % (auth.user.first_name, auth.user.last_name)

        correo = '<html><head><meta charset="UTF-8"></head><body><table><tr><td><p>Hola, %s.</p><br><p>Se ha editado un servicio. La operación fue realizada por %s, el/la cual pertenece a la dependencia de %s.</p><br><p>Para consultar dicha operación diríjase a la página web <a href="159.90.171.24">Sigulab</a></p></td></tr></table></body></html>' % (nombre_y_apellido, nombre_anade, dependencia.nombre)

        __enviar_correo(jefe_dependencia.email, 'Se ha editado un servicio', correo)


    #----- FIN EDITAR SERVICIO -----#

    #----- COMIENZO EDITAR SERVICIO -----#

    if request.post_vars.edit and (request.post_vars.eliminar is None) and (request.post_vars.visibilidad is None):
        editar = db(db.servicios.id == request.vars.idFicha).select(db.servicios.ALL)
        
    else:
        editar = []

    #----- FIN COMIENZO EDITAR SERVICIO -----#

    #----- EDITAR VISIBILIDAD -----#

    if request.post_vars.visibilidad:
        db(db.servicios.id == request.post_vars.idFicha).update(
            visibilidad=eval(request.post_vars.visibilidad))

        if request.post_vars.visibilidad == True:
            estado_visibilidad = "mostrar"
        else:
            estado_visibilidad = "ocultar"

        # Se envia el email de notificacion al ocultar/mostrar un servicio 

        idDependencia = db(auth.user_id == db.t_Personal.f_usuario).select(db.t_Personal.ALL)[0].f_dependencia

        dependencia = db(idDependencia == db.dependencias.id).select(db.dependencias.ALL)[0]

        jefe_dependencia = db(dependencia.id_jefe_dependencia == db.auth_user.id).select(db.auth_user.ALL)[0]
            
        nombre_y_apellido = "%s %s" % (jefe_dependencia.first_name, jefe_dependencia.last_name)

        nombre_anade = "%s %s" % (auth.user.first_name, auth.user.last_name)

        correo = '<html><head><meta charset="UTF-8"></head><body><table><tr><td><p>Hola, %s.</p><br><p>Se ha cambiado la visibilidad de un servicio a %s. La operación fue realizada por %s, el/la cual pertenece a la dependencia de %s.</p><br><p>Para consultar dicha operación diríjase a la página web <a href="159.90.171.24">Sigulab</a></p></td></tr></table></body></html>' % (nombre_y_apellido, estado_visibilidad, nombre_anade, dependencia.nombre)

        __enviar_correo(jefe_dependencia.email, 'Se ha cambiado la visibilidad de un servicio', correo)


    #----- FIN EDITAR VISIBILIDAD -----#

    #----- ELIMINAR SERVICIO -----#

    if request.post_vars.eliminar:
        db(db.servicios.id == request.post_vars.idFicha).delete()

        # Se envia el email de notificacion al eliminar un servicio 

        idDependencia = db(auth.user_id == db.t_Personal.f_usuario).select(db.t_Personal.ALL)[0].f_dependencia

        dependencia = db(idDependencia == db.dependencias.id).select(db.dependencias.ALL)[0]

        jefe_dependencia = db(dependencia.id_jefe_dependencia == db.auth_user.id).select(db.auth_user.ALL)[0]
            

        nombre_y_apellido = "%s %s" % (jefe_dependencia.first_name, jefe_dependencia.last_name)

        nombre_anade = "%s %s" % (auth.user.first_name, auth.user.last_name)

        correo = '<html><head><meta charset="UTF-8"></head><body><table><tr><td><p>Hola, %s.</p><br><p>Se ha eliminado un servicio. La operación fue realizada por %s, el/la cual pertenece a la dependencia de %s.</p><br><p>Para consultar dicha operación diríjase a la página web <a href="159.90.171.24">Sigulab</a></p></td></tr></table></body></html>' % (nombre_y_apellido, nombre_anade, dependencia.nombre)

        __enviar_correo(jefe_dependencia.email, 'Se ha eliminado un servicio', correo)


    #----- FIN ELIMINAR SERVICIO -----#

    #----- SOLICITAR SERVICIO -----#

    if request.post_vars.solicitar:
        redirect(URL('solicitudes', vars=dict(idServicio=request.post_vars.solicitar)))

    #----- FIN SOLICITAR SERVICIO -----#

    return dict(categorias=listar_categorias(db), tipos=listar_tipos(db),
                sedes=listar_sedes(db), editar=editar)

#----- GESTIONAR SOLICITUDES -----#
@auth.requires_login(otherwise=URL('modulos', 'login'))
def solicitudes():
    servicio_solicitud = None

    #----- AGREGAR SOLICITUDES -----#
    if request.post_vars.numRegistro:
        id_responsable = db(auth.user_id == db.t_Personal.f_usuario).select(db.t_Personal.ALL)[0].id

        solicitud_nueva = Solicitud(db, auth, request.post_vars.numRegistro, id_responsable,
            request.now, request.post_vars.nombreServicio, request.post_vars.propositoServicio,
            request.post_vars.propositoDescripcion, None, request.post_vars.descripcionSolicitud, None, 0)

        solicitud_nueva.insertar()

    #----- FIN DE AGREGAR SOLICITUDES -----#

    #----- AGREGAR SOLICITUD DESDE SERVICIO -----#
    if request.vars.idServicio:
        servicio_solicitud = Servicio(db)
        servicio_solicitud.instanciar(int(request.vars.idServicio))


    #----- CAMBIO DE ESTADO DE SOLICITUD -----#
    if request.post_vars.idFicha:
        solicitud_a_cambiar = Solicitud(db, auth)
        solicitud_a_cambiar.instanciar(int(request.post_vars.idFicha))
        solicitud_a_cambiar.cambiar_estado(int(request.post_vars.estado), request)
        solicitud_a_cambiar.actualizar(int(request.post_vars.idFicha))
        # ENVIAR CORREO A SOLICITANTE PARA AVISAR EL CAMBIO DE ESTADO

        if request.post_vars.estado == "-1":
            solicitud_a_cambiar.eliminar(int(request.post_vars.idFicha))
            # ENVIAR CORREO A SOLICITANTE PARA AVISAR SU RECHAZO

    #----- FIN DE CAMBIO DE ESTADO DE SOLICITUD -----#

    #----- ELIMINAR SOLICITUD -----#

    if request.post_vars.eliminar:
        id_a_eliminar = int(request.post_vars.idFicha_eliminar)
        db(id_a_eliminar == db.solicitudes.id).delete()

    #----- FIN DE ELIMINAR SOLICITUD -----#

    #----- LISTAR SOLICITUDES -----#
    listado_de_solicitudes = ListaSolicitudes(db, auth, "Solicitante")
    listado_de_ejecutante = ListaSolicitudes(db, auth, "Ejecutante")

    #----- DATOS DE SOLICITANTE -----#
    num_registro = validador_registro_solicitudes(request,db)

    personal_usuario = db(auth.user_id == db.t_Personal.f_usuario).select(db.t_Personal.ALL)[0]

    dependencia_usuario = db(personal_usuario.f_dependencia == db.dependencias.id).select(db.dependencias.ALL)[0]

    nombre_dependencia = dependencia_usuario.nombre

    id_jefe_dependencia = dependencia_usuario.id_jefe_dependencia

    usuario_jefe = db(id_jefe_dependencia == db.auth_user.id).select(db.auth_user.ALL)[0]

    nombre_jefe = usuario_jefe.first_name
    apellido_jefe = usuario_jefe.last_name
    email_jefe = usuario_jefe.email

    nombre_responsable = personal_usuario.f_nombre
    email_responsable = personal_usuario.f_email

    datos_solicitud = [nombre_dependencia, nombre_jefe, apellido_jefe, email_jefe, nombre_responsable, email_responsable, num_registro]


    # Solicitante: Usuario solicita cambiar la pagina
    if request.vars.pagina:
        listado_de_solicitudes.cambiar_pagina(int(request.vars.pagina))

    # Solicitante: Usuario solicita ordenar los servicios
    if request.vars.columna:
        listado_de_solicitudes.cambiar_columna(request.vars.columna)

    # Solicitante: Se ordenan y se filtran los servicios dependiendo de lo que el usuario solicito
    listado_de_solicitudes.orden_y_filtrado()

    # Solicitante: Se recuperan las paginas calculadas en base a lo solicitado
    firstpage=listado_de_solicitudes.boton_principio
    lastpage=listado_de_solicitudes.boton_fin
    nextpage=listado_de_solicitudes.boton_siguiente
    prevpage=listado_de_solicitudes.boton_anterior


    # Ejecutante: Usuario solicita cambiar la pagina
    if request.vars.pagina_ejecutante:
        listado_de_ejecutante.cambiar_pagina(int(request.vars.pagina_ejecutante))

    # Ejecutante: Usuario solicita ordenar los servicios
    if request.vars.columna_ejecutante:
        listado_de_ejecutante.cambiar_columna(request.vars.columna_ejecutante)

    # Solicitante: Se ordenan y se filtran los servicios dependiendo de lo que el usuario solicito
    listado_de_ejecutante.orden_y_filtrado()

    # Solicitante: Se recuperan las paginas calculadas en base a lo solicitado
    firstpage_ejecutante=listado_de_ejecutante.boton_principio
    lastpage_ejecutante=listado_de_ejecutante.boton_fin
    nextpage_ejecutante=listado_de_ejecutante.boton_siguiente
    prevpage_ejecutante=listado_de_ejecutante.boton_anterior

    return dict(grid=listado_de_solicitudes.solicitudes_a_mostrar, 
        pages=listado_de_solicitudes.rango_paginas,
        actualpage=listado_de_solicitudes.pagina_central,
        nextpage=nextpage, prevpage=prevpage,
        firstpage=firstpage, lastpage=lastpage, 
        grid_ejecutante=listado_de_ejecutante.solicitudes_a_mostrar, 
        pages_ejecutante=listado_de_ejecutante.rango_paginas,
        actualpage_ejecutante=listado_de_ejecutante.pagina_central,
        nextpage_ejecutante=nextpage_ejecutante, prevpage_ejecutante=prevpage_ejecutante,
        firstpage_ejecutante=firstpage_ejecutante, lastpage_ejecutante=lastpage_ejecutante,
        datos_solicitud=datos_solicitud, categorias=listar_categorias(db), tipos=listar_tipos(db),
        servicio_solicitud=servicio_solicitud)

# ---- GESTIONAR CERTIFICACIONES ---- #
@auth.requires_login(otherwise=URL('modulos', 'login'))
def certificaciones():

    # ---- ACCION DE CERTIFICACION DEL SERVICIO ----
    if request.post_vars.registro:
        registro = request.post_vars.registro
        proyecto = request.post_vars.proyecto
        elaborado_por = request.post_vars.usuarioid
        dependencia = request.post_vars.dependenciaid
        solicitud = request.post_vars.solicitudid

        solicitud_a_actualizar = Solicitud(db,auth)
        solicitud_a_actualizar.instanciar(solicitud)
        solicitud_a_actualizar.certificar()

        fecha = request.post_vars.fecha

        certificado = Certificacion(db, registro, proyecto, elaborado_por, dependencia, solicitud, fecha)
        certificado.insertar()
    #-------------------FIN------------------------

    #------ ACCION LISTAR SOLICITUDES DE SERV -----
    listado_de_solicitudes = ListaSolicitudes(db, auth, "Certificante")

    if request.vars.pagina:
        listado_de_solicitudes.cambiar_pagina(int(request.vars.pagina))

    if request.vars.columna:
        listado_de_solicitudes.cambiar_columna(request.vars.columna)

    listado_de_solicitudes.orden_y_filtrado()
    firstpage = listado_de_solicitudes.boton_principio
    lastpage = listado_de_solicitudes.boton_fin
    nextpage = listado_de_solicitudes.boton_siguiente
    prevpage = listado_de_solicitudes.boton_anterior

    # ----- FIN LISTAR SOLICITUDES -----#

    return dict(grid=listado_de_solicitudes.solicitudes_a_mostrar,
                pages=listado_de_solicitudes.rango_paginas,
                actualpage=listado_de_solicitudes.pagina_central,
                nextpage=nextpage, prevpage=prevpage,
                firstpage=firstpage, lastpage=lastpage,
                categorias=listar_categorias(db), tipos=listar_tipos(db),
                sedes=listar_sedes(db))


#------------------------------------------------------------------------------
#
# Controladores de los Ajax del modulo de Servicios
#
#------------------------------------------------------------------------------


@auth.requires_login(otherwise=URL('modulos', 'login'))
def ajax_ficha_servicio():
    session.forget(response)

    # Servicio
    entrada = db(db.servicios.id == int(request.vars.serv)).select(db.servicios.ALL)


    # Funciones
    funcion = []
    if entrada[0].gestion:
        funcion.append("Gestión  ")
    else:
        funcion.append("")

    if entrada[0].docencia:
        funcion.append("Docencia  ")
    else:
        funcion.append("")

    if entrada[0].investigacion:
        funcion.append("Investigación  ")
    else:
        funcion.append("")

    if entrada[0].extension:
        funcion.append("Extensión  ")
    else:
        funcion.append("")

    valores_de_ficha = query_ficha(db, int(request.vars.serv))
    valores_de_ficha['funcion'] = funcion

    return dict(ficha=valores_de_ficha)

@auth.requires_login(otherwise=URL('modulos', 'login'))
def ajax_ficha_solicitud():
    session.forget(response)
    # Solicitud
    solicitud = Solicitud(db, auth)

    solicitud.instanciar(int(request.vars.solicitud))

    return dict(ficha = solicitud, tipo_solicitud = request.vars.tipoSolicitud)

@auth.requires_login(otherwise=URL('modulos', 'login'))
def ajax_ficha_certificacion():
    session.forget(response)
    # Solicitud
    solicitud = Solicitud(db, auth)

    solicitud.instanciar(int(request.vars.solicitud))

    return dict(ficha = solicitud, tipo_solicitud = request.vars.tipoSolicitud)

@auth.requires_login(otherwise=URL('modulos', 'login'))
def ajax_obtener_adscripcion():
    session.forget(response)
    adscripcion_query = db((db.dependencias.id_sede == int(request.vars.sede))).select(db.dependencias.ALL)
    dependencias_a_mostrar = []

    for l in adscripcion_query:
        if re.match( r'Laboratorio\s[A-G]', l.nombre) or (l.id == 1):
            dependencias_a_mostrar.append(l)
    return dict(dependencias=dependencias_a_mostrar)

@auth.requires_login(otherwise=URL('modulos', 'login'))
def ajax_obtener_dependencia():
    session.forget(response)
    dependencia_query = db((db.dependencias.unidad_de_adscripcion == int(request.vars.adscripcion))).select(db.dependencias.ALL)
    dependencias_a_mostrar = []

    for l in dependencia_query:
        if (re.match( r'Laboratorio\s[A-G]', l.nombre)) == None:
            dependencias_a_mostrar.append(l)
    return dict(dependencias=dependencias_a_mostrar)

@auth.requires_login(otherwise=URL('modulos', 'login'))
def ajax_obtener_ubicacion():
    session.forget(response)
    ubicacion_query = db((db.espacios_fisicos.dependencia_adscrita == int(request.vars.dependencia))).select(db.espacios_fisicos.ALL)
    ubicaciones_a_mostrar = []

    for l in ubicacion_query:
        ubicaciones_a_mostrar.append(l)
    return dict(ubicaciones=ubicaciones_a_mostrar)

@auth.requires_login(otherwise=URL('modulos', 'login'))
def ajax_obtener_responsable():
    session.forget(response)
    responsable_query = db((db.t_Personal.f_dependencia == int(request.vars.dependencia))).select(db.t_Personal.ALL)
    responsables_a_mostrar = []

    for l in responsable_query:
        responsables_a_mostrar.append(l)
    return dict(responsables=responsables_a_mostrar)

@auth.requires_login(otherwise=URL('modulos', 'login'))
def ajax_obtener_adscripcion_editar():
    session.forget(response)
    adscripcion_query = db((db.dependencias.id_sede == int(request.vars.sede))).select(db.dependencias.ALL)
    dependencias_a_mostrar = []

    for l in adscripcion_query:
        if re.match( r'Laboratorio\s[A-G]', l.nombre) or (l.id == 1):
            dependencias_a_mostrar.append(l)
    return dict(dependencias=dependencias_a_mostrar)

@auth.requires_login(otherwise=URL('modulos', 'login'))
def ajax_obtener_dependencia_editar():
    session.forget(response)
    dependencia_query = db((db.dependencias.unidad_de_adscripcion == int(request.vars.adscripcion))).select(db.dependencias.ALL)
    dependencias_a_mostrar = []

    for l in dependencia_query:
        if (re.match( r'Laboratorio\s[A-G]', l.nombre)) == None:
            dependencias_a_mostrar.append(l)
    return dict(dependencias=dependencias_a_mostrar)

@auth.requires_login(otherwise=URL('modulos', 'login'))
def ajax_obtener_ubicacion_editar():
    session.forget(response)
    ubicacion_query = db((db.espacios_fisicos.dependencia_adscrita == int(request.vars.dependencia))).select(db.espacios_fisicos.ALL)
    ubicaciones_a_mostrar = []
    for l in ubicacion_query:
        ubicaciones_a_mostrar.append(l)
    return dict(ubicaciones=ubicaciones_a_mostrar)

@auth.requires_login(otherwise=URL('modulos', 'login'))
def ajax_obtener_responsable_editar():
    session.forget(response)
    responsable_query = db((db.t_Personal.f_dependencia == int(request.vars.dependencia))).select(db.t_Personal.ALL)
    responsables_a_mostrar = []

    for l in responsable_query:
        responsables_a_mostrar.append(l)
    return dict(responsables=responsables_a_mostrar)

@auth.requires_login(otherwise=URL('modulos', 'login'))
def ajax_obtener_nombre_servicio():
    session.forget(response)
    servicio_query = db(db.servicios.tipo == int(request.vars.tipo) and db.servicios.categoria == int(request.vars.categoria)).select(db.servicios.ALL)

    servicios_a_mostrar = []
    for servicio in servicio_query:
        servicios_a_mostrar.append(servicio)

    return dict(servicios=servicios_a_mostrar)

@auth.requires_login(otherwise=URL('modulos', 'login'))
def ajax_obtener_proposito_servicio():
    session.forget(response)

    servicio = db(db.servicios.id == int(request.vars.idServicio)).select(db.servicios.ALL)[0]

    propositos_a_mostrar = []

    if servicio.docencia == True:
        propositoServicio = db("Docencia" == db.propositos.tipo).select(db.propositos.ALL)[0] 
        propositos_a_mostrar.append(propositoServicio)

    if servicio.investigacion == True:
        propositoServicio = db("Investigación" == db.propositos.tipo).select(db.propositos.ALL)[0]
        propositos_a_mostrar.append(propositoServicio)

    if servicio.extension == True:
        propositoServicio = db("Extensión" == db.propositos.tipo).select(db.propositos.ALL)[0]
        propositos_a_mostrar.append(propositoServicio)    

    if servicio.gestion == True:
        propositoServicio = db("Gestión" == db.propositos.tipo).select(db.propositos.ALL)[0]
        propositos_a_mostrar.append(propositoServicio)

    return dict(propositos=propositos_a_mostrar)

@auth.requires_login(otherwise=URL('modulos', 'login'))
def ajax_obtener_datos_depen_ejecutora():
    session.forget(response)

    servicio = db(db.servicios.id == int(request.vars.idServicio2)).select(db.servicios.ALL)[0]
    dependencia_ejecutora = db(db.dependencias.id == servicio.dependencia).select(db.dependencias.ALL)[0]

    jefe_dependencia_ejecutora = db(db.auth_user.id == dependencia_ejecutora.id_jefe_dependencia).select(db.auth_user.ALL)[0]

    datos_jefe_depen_ejecutora = [jefe_dependencia_ejecutora.first_name, jefe_dependencia_ejecutora.last_name, jefe_dependencia_ejecutora.email]

    return dict(nombreDepenEjecutora= dependencia_ejecutora.nombre, jefeDepenEjecutora = datos_jefe_depen_ejecutora)


# Funcion para enviar un correo de notificacion 

def __enviar_correo(destinatario, asunto, cuerpo):
    mail = auth.settings.mailer

    mail.send(destinatario, asunto, cuerpo)


def __queries_enviar_correo():

    # OJO: QUITAR EL TRY EXCEPT 

    idDependencia = db(auth.user_id == db.t_Personal.f_usuario).select(db.t_Personal.ALL)[0].f_dependencia

    dependencia = db(idDependencia == db.dependencias.id).select(db.dependencias.ALL)[0]

    jefe_dependencia = db(dependencia.id_jefe_dependencia == db.auth_user.id).select(db.auth_user.ALL)[0]
        
    nombre_y_apellido = "%s %s" % (jefe_dependencia.first_name, jefe_dependencia.last_name)

    nombre_anade = "%s %s" % (auth.user.first_name, auth.user.last_name)

    return [nombre_y_apellido, nombre_anade, dependencia, jefe_dependencia]


@auth.requires_login(otherwise=URL('modulos', 'login'))
def ajax_certificar_servicio():
    solicitudesid = request.post_vars.solicitud
    solicitud_info = db(db.solicitudes.id == solicitudesid).select()[0]
    usuario = db(db.t_Personal.f_usuario == auth.user_id).select()[0]
    servicio = db(db.servicios.id == solicitud_info.id_servicio_solicitud).select()[0]
    responsable = db(db.t_Personal.id == servicio.responsable).select()[0]
    fecha = request.now
    dependencia = db(auth.user_id == db.auth_membership.user_id).select()[0].dependencia_asociada
    if not(dependencia is None):
        dependencianombre = db(db.dependencias.id == dependencia).select()[0].nombre
    else:
        dependencianombre = "Laboratorio A"
        dependencia = db(db.dependencias.id > 0).select()[0].id

    registro = validador_registro_certificaciones(request, db)

    return dict(solicitud=solicitud_info,
                usuario=usuario,
                servicio=servicio,
                responsable=responsable,
                fecha=fecha,
                registro=registro,
                dependenciaid=dependencia,
                dependencia=dependencianombre,
                proyecto='Proyecto ' + registro)


@auth.requires_login(otherwise=URL('modulos', 'login'))
def ajax_listado_servicios():

    #----- LISTAR SERVICIOS -----#
    listado_de_servicios = ListaServicios(db)

    order_by_asc = eval(request.post_vars.ordenarAlfabeticamente.title())
    order_by_col = request.post_vars.ordenarPor

    listado_de_servicios.cambiar_ordenamiento(order_by_asc)
    listado_de_servicios.cambiar_columna(order_by_col)

    if request.post_vars.cambiarPagina:
        listado_de_servicios.cambiar_pagina(int(request.post_vars.cambiarPagina))

    listado_de_servicios.orden_y_filtrado()
    firstpage=listado_de_servicios.boton_principio
    lastpage=listado_de_servicios.boton_fin
    nextpage=listado_de_servicios.boton_siguiente
    prevpage=listado_de_servicios.boton_anterior

    #----- FIN LISTAR SERVICIOS -----#
    return dict(grid=listado_de_servicios.servicios_a_mostrar,
                pages=listado_de_servicios.rango_paginas,
                actualpage=listado_de_servicios.pagina_central,
                nextpage=nextpage, prevpage=prevpage,
                firstpage=firstpage, lastpage=lastpage)

# Funcion para enviar un correo de notificacion 

def __enviar_correo(destinatario, asunto, cuerpo):
    mail = auth.settings.mailer

    mail.send(destinatario, asunto, cuerpo)
