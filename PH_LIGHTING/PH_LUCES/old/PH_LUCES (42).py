import json
import maya.cmds as cmds
from functools import partial
from operator import itemgetter
global grupoVG,grupoVCreacion,dock,dockLuces
global orden,ultimoOrden
global ultimoGrupoCreadoPorUsuario
global aiColorTemperatureSlider
import winsound
import maya.mel as mel
deactivateSUB = False
global buscarPor_Grupo_Luz
buscarPor_Grupo_Luz = "luz"
global copiarValor
global isolate
deactivateSSS = False
deactivateDisplacement = False
myLights = cmds.ls(type='light')
myLightsOn = cmds.ls(type='light', visible=True)
mySelection = cmds.ls (selection = True)
global seleccionLista1
global version
version = "1.8.3"

def add_light(kind):
	global contSpot
	global contDir
	global contPoint
	global contArea
	global contAmb
	global grupoVCreacion,dock

	primerGrupoCreado = ""
	descripcionDelRootOK=""
	if(not cmds.ls('ROOT_*_LGRP')):
		descripcionDelRootOK = cmds.promptDialog(
		title='DESCRIPCION ROOT',
		message='INGRESA DESCRIPCION DEL ROOT NUEVO:',
		button=['OK', 'Cancelar'],
		defaultButton='OK',
		cancelButton='Cancelar',
		dismissString='Cancelar')
	else:
	    descripcionDelRootOK='YA HAY ROOT'

	if descripcionDelRootOK=='OK':
		root = cmds.group(name='ROOT_'+ cmds.promptDialog(query=True, text=True) +'_LGRP', em=True, w=True)
		rootAts = cmds.listAttr (root , k=1 )
		for at in rootAts:
			cmds.setAttr (root+"."+at,lock=1,k=0,channelBox=0)
	else:
	    descripcionDelRootOK='YA HAY ROOT'

	grupos_LGRP = cmds.ls ('*_LGRP')
	if  ( descripcionDelRootOK=='OK' and len(grupos_LGRP)==1  ) or ( descripcionDelRootOK=='YA HAY ROOT' and len(grupos_LGRP)==1 ) :# or len(cmds.ls('ROOT*_LGRP'))==1
		cmds.confirmDialog ( title='AVISO', message='NO HAY GRUPOS DE LUCES EN LA ESCENA. CREEMOS UNO.', button=['OKI'], defaultButton='OKI' )
		primerGrupoCreado = crearGrupo()

	roots_LGRP = cmds.ls ('ROOT_*_LGRP')

	if ((len(grupos_LGRP)>=1 and len(roots_LGRP)==1) and primerGrupoCreado != "") or descripcionDelRootOK=='YA HAY ROOT' and len(grupos_LGRP)>1 :
		if cmds.window('crearLuzV',exists=True):
			cmds.deleteUI ('crearLuzV')
		ventanaCreacionLuz = cmds.window ('crearLuzV' , menuBar=0,w=250,title = "CREAR LUZ" )
		col_ventanaCrearLuz = cmds.columnLayout( adjustableColumn = True , p = ventanaCreacionLuz )
		cmds.textField ('nombreLuzCreacion' , pht='NOMBRE' ,  p=col_ventanaCrearLuz )
		grupoVCreacion = cmds.optionMenu ( 'oM_grupoVCreacion',    bgc = [0.1,0.1,0.1] , p = col_ventanaCrearLuz)
		clearOptionMenu ( grupoVCreacion )
		gruposDeLuces = cmds.ls ( '*_LGRP' , type='transform',referencedNodes=0 )
		rootDeLaEscena = cmds.ls ( 'ROOT_*_LGRP' , type='transform' ,referencedNodes=0)
		gruposDeLuces = list ( set ( gruposDeLuces ) - set ( rootDeLaEscena  ) )
		for grp in gruposDeLuces:
			cmds.menuItem(parent=grupoVCreacion, label=grp[:-5] )
		try:
			cmds.optionMenu ( grupoVCreacion, e=1 , v = ultimoGrupoCreadoPorUsuario.split ("_LGRP")[0] )
		except :
			pass
		cmds.radioCollection('coleccionTodo')
		rowDeColumnas=cmds.rowLayout (nc=3,co3=[25,0,0],ct3=["left", "both","both"], p=col_ventanaCrearLuz)
		row_ventanaCrearLuz = cmds.columnLayout( p = rowDeColumnas )
		cmds.radioCollection()
		cmds.radioButton( 'K',label='KEY', sl=1,cl='coleccionTodo')
		row_ventanaCrearLuz = cmds.columnLayout( p = rowDeColumnas )
		cmds.radioCollection()
		cmds.radioButton('F', label='FILL', cl='coleccionTodo')
		row_ventanaCrearLuz = cmds.columnLayout( p = rowDeColumnas )
		cmds.radioCollection()
		cmds.radioButton( 'R',label='RIM', cl='coleccionTodo')
		cmds.button ('b_crearLuz' , l='CREAR', c=  partial(crearLuz,kind,primerGrupoCreado) , p=col_ventanaCrearLuz)
		cmds.button ('b_cancelarCrearLuz' , l='CANCELAR' , c="cmds.deleteUI('crearLuzV')" , p=col_ventanaCrearLuz)
		cmds.showWindow ('crearLuzV')

def duplicarLuz(*args):
    lucesSeleccionadas = cmds.textScrollList('listaLuces1',q=1, si=1)
    copiasDeLuces = []
    for luz in lucesSeleccionadas:
        if luz.split("_")[-2].isdigit()==True:
            nombreLuzTRF = luz[:-8]+ str(int(luz[-8:-5])+1).zfill(3)  + luz[-5:]
            while cmds.objExists (nombreLuzTRF)==1:
                nombreLuzTRF = luz[:-8]+ str(int(nombreLuzTRF[-8:-5])+1).zfill(3)  + luz[-5:]
        else:
            nombreLuzTRF = luz

        confirma = cmds.promptDialog(title='NOMBRE DE DUPLICADO:',text=nombreLuzTRF[:-5],
        button=['OKILOKI', 'Cancelar'],defaultButton='OKILOKI',cancelButton='Cancelar',
        dismissString='Cancelar')

        if confirma == 'OKILOKI' :
            nombreLuzTRF = cmds.promptDialog(query=True, text=True) + luz[-5:]
            while cmds.objExists (nombreLuzTRF)==1 and confirma!="Cancelar":
                if luz.split("_")[-2].isdigit()==True:
                    nombreLuzTRF = luz[:-8]+ str(int(luz[-8:-5])+1).zfill(3)  + luz[-5:]
                    while cmds.objExists (nombreLuzTRF)==1:
                        nombreLuzTRF = luz[:-8]+ str(int(nombreLuzTRF[-8:-5])+1).zfill(3)  + luz[-5:]
                else:
                    nombreLuzTRF = "Duplicado_"+ nombreLuzTRF
                confirma = cmds.promptDialog(title='NOMBRE DE DUPLICADO:',text=nombreLuzTRF[:-5],
                button=['OKILOKI', 'Cancelar'],defaultButton='OKILOKI',cancelButton='Cancelar',dismissString='Cancelar')
            if confirma == 'OKILOKI' :
                nombreLuzTRF = cmds.promptDialog(query=True, text=True) + luz[-5:]
                cmds.duplicate ( luz , rr=1 , ic=1 , n=nombreLuzTRF )
                copiasDeLuces.append(nombreLuzTRF)
                if cmds.referenceQuery( luz ,isNodeReferenced=1 ) == True:
                    esReferencia_cambiaDeGrupo(luz=nombreLuzTRF,original=luz)

            else:
                cmds.warning (" - - - CANCELADO 2 - - - ")
        else:
            cmds.warning (" - - - CANCELADO 1 - - - ")

    if copiasDeLuces:
        try:
            ordenarLuz()
            ordenarLuz()
            cmds.textScrollList('listaLuces1',e=1, da=1)
            cmds.textScrollList('listaLuces2',e=1, da=1)
            cmds.textScrollList('listaLuces3',e=1, da=1)
            cmds.textScrollList('listaLuces1',e=1, si=copiasDeLuces)
            indexSeleccionLista1 = cmds.textScrollList('listaLuces1',q=1, sii=1)
            cmds.textScrollList('listaLuces2',e=1, sii=indexSeleccionLista1)
            cmds.textScrollList('listaLuces3',e=1, sii=indexSeleccionLista1)
            cmds.warning (" - - - LUCES: SE HAN SELECCIONADO LAS LUCES NUEVAS - - - ")
        except:
            pass

def cierraVentanaDup ( luz , *args ):
    grupoDeseado = cmds.optionMenu ( 'om_dup', q=1 , v = 1)
    cmds.parent ( luz , grupoDeseado+'_LGRP' )
    cmds.deleteUI ('duplicarLuzV')
    refrescar()

def esReferencia_cambiaDeGrupo(luz, original , *args):
    if cmds.window( 'duplicarLuzV' ,exists=True):
        cmds.deleteUI ( 'duplicarLuzV' )
    vDuplicado = cmds.window ( 'duplicarLuzV' ,tb=0,menuBar=0,w=250,h=150, resizeToFitChildren=1,s=0,title = "DUPLICA LUZ" )
    col_ventanaduplicarLuz = cmds.columnLayout( adjustableColumn = True , p = vDuplicado )
    cmds.text (l="LA LUZ QUE QUERES DUPLICAR ESTA REFERENCIADA:\n"+ original + "\nELEGI EL GRUPO EN EL QUE QUERES QUE QUEDE EL DUPLICADO." , p = col_ventanaduplicarLuz)
    om_dup = cmds.optionMenu('om_dup',bgc = [0.1,0.1,0.1] , p = col_ventanaduplicarLuz)
    ok_dup = cmds.button ('ok_dup' , l = "OK"  , p = col_ventanaduplicarLuz , c = partial(cierraVentanaDup,luz ) )
    clearOptionMenu ( om_dup )
    gruposDeLuces = cmds.ls ( '*_LGRP' , type='transform',referencedNodes=0 )
    rootDeLaEscena = cmds.ls ( 'ROOT_*_LGRP' , type='transform' ,referencedNodes=0)
    gruposDeLuces = list ( set ( gruposDeLuces ) - set ( rootDeLaEscena  ) )
    for grp in gruposDeLuces:
    	cmds.menuItem(parent=om_dup, label=grp[:-5] )
    if ultimoGrupoCreadoPorUsuario:
        cmds.optionMenu ( om_dup, e=1 , v = ultimoGrupoCreadoPorUsuario.split ("_LGRP")[0] )
    cmds.showWindow ('duplicarLuzV')
    refrescar()

def renombrarLuz (*args):
    lucesSeleccionadas = cmds.textScrollList('listaLuces1',q=1, si=1)
    lucesRenombradas = []
    for luz in lucesSeleccionadas:
        if luz.split("_")[-2].isdigit()==True:
            nombreLuzTRF = luz[:-8]+ str(int(luz[-8:-5])+1).zfill(3)  + luz[-5:]
            while cmds.objExists (nombreLuzTRF) == 1:
                nombreLuzTRF = luz[:-8]+ str(int(nombreLuzTRF[-8:-5])+1).zfill(3)  + luz[-5:]
        else:
            nombreLuzTRF = luz

        confirma = cmds.promptDialog(
		title='NOMBRE DE DUPLICADO:',text=nombreLuzTRF[:-5],button=['OKILOKI', 'Cancelar'],
		defaultButton='OKILOKI',cancelButton='Cancelar',dismissString='Cancelar')

        if confirma == 'OKILOKI' :
            nombreLuzTRF = cmds.promptDialog(query=True, text=True) + luz[-5:]
            while cmds.objExists (nombreLuzTRF)==1 and confirma!="Cancelar":
                nombreLuzTRF = luz[:-8]+ str(int(luz[-8:-5])+1).zfill(3)  + luz[-5:]
                while cmds.objExists (nombreLuzTRF)==1:
                    nombreLuzTRF = luz[:-8]+ str(int(nombreLuzTRF[-8:-5])+1).zfill(3)  + luz[-5:]
                confirma = cmds.promptDialog(title='NOMBRE DE DUPLICADO:',text=nombreLuzTRF[:-5],
                button=['OKILOKI', 'Cancelar'],defaultButton='OKILOKI',cancelButton='Cancelar',dismissString='Cancelar')
            if confirma == 'OKILOKI' :
                nombreLuzTRF = cmds.promptDialog(query=True, text=True) + luz[-5:]
                cmds.rename ( luz ,  nombreLuzTRF )
                lucesRenombradas.append(nombreLuzTRF)
            else:
                cmds.warning (" - - - CANCELADO - - - ")
        else:
            cmds.warning (" - - - CANCELADO - - - ")

    if lucesRenombradas:
        try:
            ordenarLuz()
            ordenarLuz()
            cmds.textScrollList('listaLuces1',e=1, da=1)
            cmds.textScrollList('listaLuces2',e=1, da=1)
            cmds.textScrollList('listaLuces3',e=1, da=1)
            cmds.textScrollList('listaLuces1',e=1, si=lucesRenombradas)
            indexSeleccionLista1 = cmds.textScrollList('listaLuces1',q=1, sii=1)
            cmds.textScrollList('listaLuces2',e=1, sii=indexSeleccionLista1)
            cmds.textScrollList('listaLuces3',e=1, sii=indexSeleccionLista1)
            cmds.warning (" - - - LUCES: SE HAN SELECCIONADO LAS LUCES NUEVAS - - - ")
        except:
            pass

def ordenarLuz(seleccionar=1):
	global orden
	lucesTodas = cmds.ls(['*_LPNTSH','*_LDIRSH','*_LARESH','*_LAMBSH','*_LSPTSH','*_DOMESH'],r=1)
	if len(lucesTodas)!=0:
		datosOrdenados =  ordenarDatos(ordenarPor='luz' , filtrado='')
		if orden["luz"]%2 == 1:
			datosOrdenados[0].reverse()
			datosOrdenados[1].reverse()
			datosOrdenados[2].reverse()
		listas = ['listaLuces1','listaLuces2','listaLuces3']
		seleccionar = cmds.textScrollList ('listaLuces1' , q=1 , si=1 )
		for lista in listas:
			cmds.textScrollList (lista, e=1 ,ra=1)
		cmds.textScrollList ('listaLuces1' , e=1  ,  a=datosOrdenados[0] , numberOfRows = len(datosOrdenados[0])+2 , si=seleccionar)
		cmds.textScrollList ('listaLuces2' , e=1  ,  a=datosOrdenados[1] , numberOfRows = len(datosOrdenados[0])+2)
		cmds.textScrollList ('listaLuces3' , e=1  ,  a=datosOrdenados[2] , numberOfRows = len(datosOrdenados[0])+2)
		orden["luz"] +=1
		boldOblique()
		cmds.textScrollList ('listaLuces1' , e=1  ,  da=1)
		cmds.textScrollList ('listaLuces1' , e=1 , si=seleccionar )
		cmds.textScrollList ('listaLuces2' , e=1  ,  da=1)
		try:
			cmds.textScrollList ('listaLuces2' , e=1  ,  sii= cmds.textScrollList ('listaLuces1' , q=1 , sii=1 ))
			cmds.textScrollList ('listaLuces3' , e=1  ,  da=1)
			cmds.textScrollList ('listaLuces3' , e=1  ,  sii= cmds.textScrollList ('listaLuces1' , q=1 , sii=1 ))
		except:
			pass
	else:
		cmds.textScrollList('listaLuces1',e=1,ra=1)
		cmds.textScrollList('listaLuces2',e=1,ra=1)
		cmds.textScrollList('listaLuces3',e=1,ra=1)
		cmds.warning ("---- NO SE DETECTARON LUCES ADMITIDAS ----")


def crearLuz(kind="",primerGrupoCreado='' , nombre=''):
    global grupoVG
    global grupoVCreacion,dock,dockLuces
    if nombre=="" or nombre==False:
        nombreLuz = cmds.textField('nombreLuzCreacion',q=1,text=1)+"_"+cmds.radioCollection('coleccionTodo',q=1,select=1)+"_"
        grupoDeLaLuzCreada = cmds.optionMenu (grupoVCreacion,q=1,value=1)
        if nombreLuz=="_"+cmds.radioCollection('coleccionTodo',q=1,select=1)+"_" or nombreLuz[0] in "0123456789": #si no puso ningun nombre
            nombreLuz = 'RENAMEMEPLEASE'+"_"+cmds.radioCollection('coleccionTodo',q=1,select=1)+"_"
    else:
        nombreLuz=nombre
        grupoDeLaLuzCreada = (cmds.listRelatives (nombreLuz,parent=1))[0][:-5]
        nombreLuz=nombre[:-8]

    if kind == 'spot':
        nameLight = cmds.spotLight(name=nombreLuz)
        nameLight = cmds.rename (nameLight, nameLight.split("Shape")[0]+"SH")
        nombreSinSuff = cmds.listRelatives(nameLight, shapes=True, children= True, allParents=True)[0]
        nroLuz=1
        if cmds.objExists (nombreSinSuff+str(nroLuz).zfill(3)+'_LSPT'):
            while cmds.objExists (nombreSinSuff+str(nroLuz).zfill(3)+'_LSPT'):
                nroLuz +=1
            nombreSinSuff = cmds.rename(  nombreSinSuff , nombreSinSuff + str(nroLuz).zfill(3) )
            nombreConSuff = cmds.rename(  nombreSinSuff , nombreSinSuff + '_LSPT' )
        else:
            nombreConSuff=cmds.rename(  nombreSinSuff , nombreSinSuff + str(nroLuz).zfill(3) + '_LSPT')
        cmds.select(nombreConSuff)
        cmds.parent(nombreConSuff, grupoDeLaLuzCreada+'_LGRP')

    elif kind == 'dir':
        nameLight = cmds.directionalLight(name=nombreLuz)
        nameLight = cmds.rename (nameLight, nameLight.split("Shape")[0]+"SH")
        nombreSinSuff = cmds.listRelatives(nameLight, shapes=True, children= True, allParents=True)[0]
        nroLuz=1
        if cmds.objExists (nombreSinSuff+str(nroLuz).zfill(3)+'_LDIR'):
            while cmds.objExists (nombreSinSuff+str(nroLuz).zfill(3)+'_LDIR'):
                nroLuz +=1
            nombreSinSuff = cmds.rename(  nombreSinSuff , nombreSinSuff + str(nroLuz).zfill(3) )
            nombreConSuff = cmds.rename(  nombreSinSuff , nombreSinSuff + '_LDIR' )
        else:
            nombreConSuff=cmds.rename(  nombreSinSuff , nombreSinSuff + str(nroLuz).zfill(3) + '_LDIR')
        cmds.select(nombreConSuff)
        cmds.parent(nombreConSuff, grupoDeLaLuzCreada+'_LGRP')

    elif kind == 'point':
        nameLight = cmds.pointLight(name=nombreLuz)
        nameLight = cmds.rename (nameLight, nameLight.split("Shape")[0]+"SH")
        nombreSinSuff = cmds.listRelatives(nameLight, shapes=True, children= True, allParents=True)[0]
        nroLuz=1
        if cmds.objExists (nombreSinSuff+str(nroLuz).zfill(3)+'_LPNT'):
            while cmds.objExists (nombreSinSuff+str(nroLuz).zfill(3)+'_LPNT'):
                nroLuz +=1
            nombreSinSuff = cmds.rename(  nombreSinSuff , nombreSinSuff + str(nroLuz).zfill(3) )
            nombreConSuff = cmds.rename(  nombreSinSuff , nombreSinSuff + '_LPNT' )
        else:
            nombreConSuff=cmds.rename(  nombreSinSuff , nombreSinSuff + str(nroLuz).zfill(3) + '_LPNT')
        cmds.select(nombreConSuff)
        cmds.parent(nombreConSuff, grupoDeLaLuzCreada+'_LGRP')

    elif kind == 'area':
        nombreLuz = cmds.group(name = nombreLuz, em=True, w=True)
        nameLight = cmds.shadingNode('areaLight',name=nombreLuz+"SH",p=nombreLuz,asLight=True).encode("utf-8")
        nameLightSH = nombreLuz
        nombreSinSuff = cmds.listRelatives(nameLight, shapes=True, children= True)[0]
        nroLuz=1
        if cmds.objExists (nombreLuz+str(nroLuz).zfill(3)+'_LARE'):
            while cmds.objExists (nombreLuz+str(nroLuz).zfill(3)+'_LARE'):
                nroLuz +=1
            nombreLuz = cmds.rename(  nombreLuz , nombreLuz + str(nroLuz).zfill(3) )
            nombreConSuff = cmds.rename(  nombreLuz , nombreLuz + '_LARE' )
        else:
            nombreConSuff=cmds.rename(  nombreLuz , nombreLuz + str(nroLuz).zfill(3) + '_LARE')
        cmds.select(nombreConSuff)
        cmds.parent(nombreConSuff, grupoDeLaLuzCreada+'_LGRP')

    ordenarLuz()
    rutaOM = clearOptionMenu (grupoVG)
    gruposDeLuces = cmds.ls ( '*_LGRP' , type='transform' )
    rootDeLaEscena = ""
    roots = cmds.ls('ROOT_*_LGRP',r=1)
    listaDeRootsNoReferenciados=[]

    for root in roots:
        if cmds.referenceQuery( root ,isNodeReferenced=1 ) == False:
            listaDeRootsNoReferenciados.append (root)
    if len(listaDeRootsNoReferenciados)==1:
        rootDeLaEscena = listaDeRootsNoReferenciados[0]
    for grp in gruposDeLuces:
        if grp !=rootDeLaEscena and cmds.referenceQuery( grp ,isNodeReferenced=1 ) == False :
            cmds.menuItem( parent = dock +  grupoVG.split("winMLuces")[1] , label = grp[:-5] )
    if cmds.window('crearLuzV',q=1,ex=1):
        cmds.deleteUI ('crearLuzV')
    cmds.textScrollList ('listaLuces1',e=1,da=1)
    cmds.textScrollList ('listaLuces1',e=1,si=nombreConSuff)
    ordenarLuz()
    #ordenarLuz()
    refreshui()
    return nombreConSuff

def clearOptionMenu (optionMenu):
	optionMenuFullName = None
	try:
		menuItems = cmds.optionMenu ( optionMenu , q=1 , ill=1 )
		if menuItems != None and menuItems !=[]:
			cmds.deleteUI ( menuItems )
		firstItem = menuItems[0]
		optionMenuFullName = firstItem [:-len(firstItem.split ("|")[1])-1]
	except:
		pass
	return optionMenuFullName

def verAtraves(*args):
	if cmds.window ('v_Ver',ex=1):
		cmds.deleteUI ('v_Ver')
	if cmds.modelPanel ('mp_ver',ex=1):
		cmds.deleteUI ('mp_ver', panel=1)
	luzSeleccionada = cmds.textScrollList ('listaLuces1', q=1 , si=1 )[0]
	cmds.window( 'v_Ver' , title='VIENDO: '+luzSeleccionada)
	frameLayout_1 = cmds.frameLayout( lv=0 ,w=500 , h=500 , p='v_Ver' , collapsable=1 )
	cmds.modelPanel( 'mp_ver' , l='' ,menuBarVisible=0 , p=frameLayout_1)
	nombreEditor = cmds.modelPanel( 'mp_ver' , q=1 , modelEditor=1)
	cmds.modelEditor (nombreEditor  , e =1 ,displayAppearance="smoothShaded",
	 	polymeshes=1,nurbsSurfaces=1,planes=1,lights=1,cameras=0,controlVertices=0,
	 	grid=0,hulls=0,joints=0,ikHandles=0,nurbsCurves=0,deformers=0,dynamics=1,
	 	fluids=0,hairSystems=0,follicles=0,nCloths=1,nParticles=1,nRigids=1,
	 	dynamicConstraints=0,locators=0,manipulators=0,dimensions=0,handles=0,
	 	pivots=1,textures=0,strokes=0,pluginShapes=1,queryPluginObjects=1,)
	cmds.lookThru( luzSeleccionada , 'mp_ver' )
	domosEscondidos = cmds.hide ( cmds.ls (type='aiSkyDomeLight') )
	cmds.showWindow()

def borrarBuscador(args):
	cmds.textField ('buscador' , e=1 , text="")
	cmds.warning ("~~~~~~~~~ borrarBuscador() ~~~~~~~~~")

def seleccionarLuces():
    shapesSeleccionado = cmds.listRelatives (cmds.textScrollList ('listaLuces1',q=1, si=1) , shapes=1)
    cmds.select ( shapesSeleccionado )

def tglTodos():
	botonesFiltros = ['LDIR','LSPT','LPNT','LARE',]
	imagenEstado = int(cmds.iconTextButton ('b_filtroLSPT',q=1, i1=1)[-5])
	for boton in botonesFiltros:
		cmds.iconTextButton ("b_filtro"+boton,e=1,i1="M:\PH_SCRIPTS\ICONS\\"+boton+"_"+str(int(not(imagenEstado)))+".png")
	filtradoRefresh()

def deseleccionarListas(*args):
    cmds.textScrollList ( 'listaLuces1' , e = 1 ,  da = 1 )
    cmds.textScrollList ( 'listaLuces2' , e = 1 ,  da = 1 )
    cmds.textScrollList ( 'listaLuces3' , e = 1 ,  da = 1 )

def mantenerSeleccion (*args):
    global seleccion
    listas = ['listaLuces1','listaLuces2','listaLuces3']
    deseleccionarListas()
    it1 = cmds.textScrollList('listaLuces1',q=1,ai=1) # items de la lista 1
    if it1:
        for s in seleccion:
            if s in it1:
                try:
                    cmds.textScrollList ( 'listaLuces1' , e = 1 ,  si = s )
                    indexSeleccion = cmds.textScrollList ( 'listaLuces1' , q = 1 ,  sii = 1 )
                    cmds.textScrollList ( 'listaLuces2' , e = 1 ,  sii = indexSeleccion )
                    cmds.textScrollList ( 'listaLuces3' , e = 1 ,  sii = indexSeleccion )
                except:
                    print ""

def filtrado(luzTipo):
	imagen = cmds.iconTextButton ('b_filtro'+luzTipo,q=1, i1=1)
	if int(imagen[-5])==1:
		cmds.iconTextButton ('b_filtro'+luzTipo , e=1 , i1 = "M:\PH_SCRIPTS\ICONS\\"+luzTipo+"_0.png" )
	if int(imagen[-5]) == 0 :
		cmds.iconTextButton ('b_filtro'+luzTipo , e=1 , i1 = "M:\PH_SCRIPTS\ICONS\\"+luzTipo+"_1.png" )
	filtradoRefresh()

def filtradoRefresh():
    filtros = ['b_filtroLPNT','b_filtroLDIR','b_filtroLSPT','b_filtroLARE']
    filtrosActivos=[]
    for filtro in filtros:
        estadoFiltro = int  ((cmds.iconTextButton (filtro , q = 1 , i1=1))[-5])
        if estadoFiltro==1:
            filtrosActivos.append ( "*"+ filtro[-4:] + "SH" )
    try:
        ordenarTipo( arraySufijos = filtrosActivos )
        boldOblique()
        enableDropParent()
    except:
        pass
    mantenerSeleccion()

def ordenarTipo( arraySufijos =[],seleccionar=1):
    global seleccion
    global orden
    if arraySufijos =='':
        datosOrdenados =  ordenarDatos(ordenarPor='tipo' , filtrado='')
    else:
        datosOrdenados = ordenarDatos(ordenarPor='tipo' , filtrado=arraySufijos)
    if orden["tipo"]%2 == 1:
        datosOrdenados[0].reverse()
        datosOrdenados[1].reverse()
        datosOrdenados[2].reverse()
    listas = ['listaLuces1','listaLuces2','listaLuces3']
    for lista in listas:#limpio listas
        cmds.textScrollList (lista, e=1 ,ra=1)
    if datosOrdenados:
        try:
            cmds.textScrollList ('listaLuces1' , e=1  ,  a=datosOrdenados[0] , numberOfRows = len(datosOrdenados[0])+2) #lleno lista1
            cmds.textScrollList ('listaLuces2' , e=1  ,  a=datosOrdenados[1] , numberOfRows = len(datosOrdenados[0])+2)
            cmds.textScrollList ('listaLuces3' , e=1  ,  a=datosOrdenados[2] , numberOfRows = len(datosOrdenados[0])+2)
            indiceSeleccionLista1 = cmds.textScrollList ('listaLuces1' , q=1 , sii=1 ) # obtengo indices de items1
            boldOblique()
        except:
            pass
        orden["tipo"] +=1
        ultimoOrden="tipo"

def qVisibilidadAbsoluta(luz,*args):
    visibilidadAbsoluta =1
    shapeDeObj = cmds.listRelatives ( luz , p=1 )[0]
    if cmds.objExists(shapeDeObj):
        luzFullPath = cmds.ls (shapeDeObj,long=1)[0]
        luzFullPathSPLIT = luzFullPath.split("|")[1:]
        for p in luzFullPathSPLIT:
            if visibilidadAbsoluta:
                visibilidad=cmds.getAttr(p+".visibility")
                if not visibilidad:
                    visibilidadAbsoluta=0
    return visibilidadAbsoluta

def visibilidadDeRuta( *args):
    global outliner
    global filtroLuces
    if cmds.window('visibilidad' , q=1 , ex=1):
        cmds.deleteUI ( 'visibilidad' )
        try:
            cmds.deleteUI (filtroLuces)
        except:
            pass

    seleccionLista1 = cmds.textScrollList ('listaLuces1' , q=1 , si=1)[0]
    pV=[]# visibilidad de parents
    if seleccionLista1:
        ruta = cmds.ls(seleccionLista1,long=1)[0]
        parents = ruta.split("|")[1:]
    for p in parents:
        if cmds.getAttr(p+".visibility"):
            pV.append(1)
        else:
            pV.append(0)





    cmds.select (parents)

    cmds.window('visibilidad' , t='VISIBILIDAD')
    cmds.frameLayout( labelVisible=False )
    panel = cmds.outlinerPanel()
    outliner = cmds.outlinerPanel(panel, query=True,outlinerEditor=True)
    cmds.outlinerEditor( outliner, edit=1, mainListConnection='worldList', selectionConnection='modelList', showShapes=0, showReferenceNodes=0, showReferenceMembers=0, showAttributes=0, showConnected=0, showAnimCurvesOnly=0, autoExpand=1, expandObjects=1,showDagOnly=1, ignoreDagHierarchy=0, expandConnections=0, showNamespace=1, showCompounds=1, showNumericAttrsOnly=0, highlightActive=1, autoSelectNewObjects=0, doNotSelectNewObjects=0, transmitFilters=0, showSetMembers=1, setFilter='defaultSetFilter', ignoreHiddenAttribute=0 )

    inputList =cmds.selectionConnection (worldList=1)
    selecCon = cmds.selectionConnection()
    filtroLuces = cmds.itemFilter ( byType= ("spotLight" , "directionalLight" , "pointLight" , "areaLight") )
    cmds.outlinerEditor ( outliner , e=1 , mainListConnection=inputList)
    cmds.outlinerEditor ( outliner , e=1 , selectionConnection = selecCon , filter = filtroLuces )
    cmds.showWindow()

def cierraOutliner (*args):# en desuso
    global outliner
    global filtroLuces
    cmds.delete ( filtroLuces )
    cmds.deleteUI ('visibilidad')

def refreshui(refrescarPor="",*args):
	global aiColorTemperatureSlider
	global haySeleccionEnLista
	global grupoVG
	global win
	global seleccion
	seleccion=[]
	seleccion = cmds.textScrollList('listaLuces1' ,q=1, si=1)
	refreshOverride()
	if refrescarPor=='luz':
		lucesSeleccionadasIndices = cmds.textScrollList('listaLuces1' ,q=1, sii=1)
		cmds.textScrollList ('listaLuces2' , e=1 ,da=1)
		cmds.textScrollList ('listaLuces3' , e=1 ,da=1)
		try:
			cmds.textScrollList ('listaLuces2' , e=1 ,sii=lucesSeleccionadasIndices)
			cmds.textScrollList ('listaLuces3' , e=1 ,sii=lucesSeleccionadasIndices)
		except:
			pass
	if refrescarPor=='tipo':
		lucesSeleccionadasIndices = cmds.textScrollList('listaLuces2' ,q=1, sii=1)
		cmds.textScrollList ('listaLuces1' , e=1 ,da=1)
		cmds.textScrollList ('listaLuces3' , e=1 ,da=1)
		try:
			cmds.textScrollList ('listaLuces1' , e=1 ,sii=lucesSeleccionadasIndices)
			cmds.textScrollList ('listaLuces3' , e=1 ,sii=lucesSeleccionadasIndices)
		except:
			pass
	if refrescarPor=='grupo':
		lucesSeleccionadasIndices = cmds.textScrollList('listaLuces3' ,q=1, sii=1)
		cmds.textScrollList ('listaLuces1' , e=1 ,da=1)
		cmds.textScrollList ('listaLuces2' , e=1 ,da=1)
		try:
			cmds.textScrollList ('listaLuces1' , e=1 ,sii=lucesSeleccionadasIndices)
			cmds.textScrollList ('listaLuces2' , e=1 ,sii=lucesSeleccionadasIndices)
		except:
			pass
	rootDeLaEscena = ""
	roots = cmds.ls('ROOT_*_LGRP',r=1)
	listaDeRootsNoReferenciados=[]
	for root in roots:
		if cmds.referenceQuery( root ,isNodeReferenced=1 ) == False:
			listaDeRootsNoReferenciados.append (root)

	if len(listaDeRootsNoReferenciados)==1:
		rootDeLaEscena = listaDeRootsNoReferenciados[0]
	clearOptionMenu (grupoVG)
	gruposDeLuces = cmds.ls ( '*_LGRP' , type='transform' )
	for grp in gruposDeLuces:
		if grp !=rootDeLaEscena and cmds.referenceQuery( grp ,isNodeReferenced=1 ) == False :
			cmds.menuItem(parent=grupoVG , label=grp[:-5] )
	clearOptionMenu (grupoCParent)
	for grp in gruposDeLuces:
		if grp != rootDeLaEscena and cmds.referenceQuery( grp ,isNodeReferenced=1 ) == False:
			cmds.menuItem(parent=dock +  grupoCParent.split("winMLuces")[1] , label=grp[:-5] )
	# REFRESH DE ATRIBUTOS.
	lucesSeleccionadas = cmds.textScrollList('listaLuces1' ,q=1, si=1)
	if lucesSeleccionadas!=None:
	    haySeleccionEnLista=True
	else:
	    haySeleccionEnLista=False
	if lucesSeleccionadas != None:
		camposAtributos       = { "on_off":0, "aiExposure":0 , "aiRadius":0, "aiColorTemperature":0, "color":0, "intensity":0, "aiAngle":0, "aiSamples":0,"emitDiffuse":0,"emitSpecular":0,"coneAngle":0 ,"penumbraAngle":0 ,"dropoff":0 , "aiShadowDensity":0 }
		camposAtributosV      = { "on_off":0, "aiExposure":0 , "aiRadius":0, "aiColorTemperature":0, "color":None, "intensity":0, "aiAngle":0, "aiSamples":0,"emitDiffuse":0,"emitSpecular":0 ,"coneAngle":0  ,"penumbraAngle":0 ,"dropoff":0 , "aiShadowDensity":0 }
		camposAtributosDif    = { "on_off":0, "aiExposure":0 , "aiRadius":0, "aiColorTemperature":0, "color":0, "intensity":0, "aiAngle":0, "aiSamples":0,"emitDiffuse":0,"emitSpecular":0 , "coneAngle":0  ,"penumbraAngle":0 ,"dropoff":0 , "aiShadowDensity":0 }
		# hide / unhide
		for luz in lucesSeleccionadas: #VALORES
			if qVisibilidadAbsoluta(luz):
				camposAtributosV["on_off"] = qVisibilidadAbsoluta(luz)

		for luz in lucesSeleccionadas: # TIENEN EL MISMO VALOR TODOS?
			if qVisibilidadAbsoluta(luz) != camposAtributosV["on_off"] :
				camposAtributosDif["on_off"]=1
		# todos los atts menos el hide / unhide
		for luz in lucesSeleccionadas:
			for key in camposAtributos.keys(): # CAPTURO VALORES
				if (cmds.attributeQuery (key , node=luz+"SH" , ex=1)):
					camposAtributosV[key]=cmds.getAttr ( luz+"SH."+key )
			for key in camposAtributos.keys(): # TIENEN EL ATRIBUTO TODOS?
				if (cmds.attributeQuery (key , node=luz+"SH" , ex=1)):
					camposAtributos[key] += 1
		for luz in lucesSeleccionadas:
			for key in camposAtributos.keys(): # TIENEN EL MISMO VALOR TODOS?
				if (cmds.attributeQuery (key , node=luz+"SH" , ex=1)):
					if cmds.getAttr ( luz+"SH."+key ) != camposAtributosV[key]:
						camposAtributosDif[key]=1
		# VALORES
		for campo in camposAtributosV.keys():
			if camposAtributos[campo] == len (lucesSeleccionadas) and camposAtributosDif[campo]!=1:
				try:
					cmds.floatField ( campo , e=1 , v = camposAtributosV[campo] )
				except:
					pass
				try:
					cmds.checkBox ( campo , e=1 , v = camposAtributosV[campo] )
				except:
					pass
				if campo=="color" :
					try:
						cmds.colorSliderGrp( campo , e=1 , rgbValue = camposAtributosV[campo][0] )
					except:
						pass
	    # PINTAR BEIGE
		for campo in camposAtributos.keys():
			if camposAtributosDif [campo] ==0 and len(lucesSeleccionadas)==camposAtributos[campo]: #tienen valores iguales
				try:
					cmds.floatField ( campo , e=1 , en=1 , bgc=[0.3,0.3,0.3])
				except:
					pass
				try:
					cmds.checkBox ( campo , e=1 , en=1  , bgc=[0.3,0.3,0.3] )
				except:
					pass
				try:
					cmds.colorSliderGrp( campo , e = 1 , en = 1  , ebg=0)
				except:
					pass
			elif camposAtributosDif [campo] !=0 and len(lucesSeleccionadas)== camposAtributos[campo]:#tienen valores diferentes
				try:
					cmds.floatField ( campo , e=1 , en=1, bgc=[0.863,0.808,0.529] )
				except:
					pass
				try:
					cmds.checkBox ( campo , e=1 ,  en=1 , bgc=[0.863,0.808,0.529])
				except:
					pass
				if campo=="color" :
					cmds.colorSliderGrp( campo , e=1 , en=1  , bgc = [0.863,0.808,0.529])

		maxmin()
		enableCampos(camposAtributos)
		if camposAtributosDif ["on_off"] ==0 : #tienen valores iguales
			try:
				cmds.checkBox ( "on_off" , e=1 , en=1  , v=camposAtributosV["on_off"] ,  bgc=[0.3,0.3,0.3] )
			except:
				pass
		elif camposAtributosDif ["on_off"] !=0 :#tienen valores diferentes
			try:
				cmds.checkBox ( "on_off" , e=1 ,  en=1 , bgc=[0.863,0.808,0.529])
			except:
				pass
		dropListas()
		boldOblique()
		enableDropParent()
		enableTempColor ()
		enableAbsRel()
		refreshDomo()


def enableAbsRel(*args):
    global abs
    global rel
    global haySeleccionEnLista
    if haySeleccionEnLista:
        cmds.radioButton( abs,e=1,en=1 )
        cmds.radioButton( rel,e=1,en=1 )

def deseleccionar(*args):
    global abs
    global rel
    cmds.textScrollList ('listaLuces1' , e=1  ,da=1)
    cmds.textScrollList ('listaLuces2' , e=1  ,da=1)
    cmds.textScrollList ('listaLuces3' , e=1  ,da=1)
    cmds.select(cl=True)
    cmds.radioButton( abs,e=1,en=0 )
    cmds.radioButton( rel,e=1,en=0 )
    enableDropParent()
    cmds.warning('AHORA PODES EDITAR LOS GRUPOS.')
    refreshui()

def enableDropParent():
	global grupoCParent
	global grupo_borrar
	global grupo_renombrar
	if cmds.textScrollList('listaLuces1',q=1,si=1)==None:
		cmds.optionMenu (grupoCParent,e=1,en=1,ann="ACA ELEGIS EL PARENT DEL GRUPO ELEGIDO A LA IZQUIERDA.")
		cmds.iconTextButton(grupo_borrar,e=1,en=1)
		cmds.iconTextButton(grupo_renombrar,e=1,en=1)
	else:
		cmds.optionMenu (grupoCParent,e=1,en=0,ann="DESELECCIONA LAS LUCES DE LA LISTA PARA HABILITAR ESTA OPCION.")
		cmds.iconTextButton(grupo_borrar,e=1,en=0)
		cmds.iconTextButton(grupo_renombrar,e=1,en=0)

def boldOblique():
	luces = cmds.textScrollList('listaLuces1' ,q=1, ai=1)
	seleccionLista1 = cmds.textScrollList ("listaLuces1",q=1,sii=1)

	if luces!=None:
		for luz in luces:
			cmds.textScrollList ("listaLuces1",e=1,da=1)
			cmds.textScrollList ("listaLuces2",e=1,da=1)
			cmds.textScrollList ("listaLuces3",e=1,da=1)
			if qVisibilidadAbsoluta(luz) and cmds.referenceQuery( luz ,isNodeReferenced=1 )==True: #referenciada y activa
				cmds.textScrollList ("listaLuces1",e=1,si=luz)
				index= cmds.textScrollList ("listaLuces1",q=1,sii=1)[0]
				cmds.textScrollList ("listaLuces1", e=1, lf=[index,"smallObliqueLabelFont"])
				cmds.textScrollList ("listaLuces2", e=1, lf=[index,"smallObliqueLabelFont"])
				cmds.textScrollList ("listaLuces3", e=1, lf=[index,"smallObliqueLabelFont"])
			elif qVisibilidadAbsoluta(luz)==False and cmds.referenceQuery( luz ,isNodeReferenced=1 )==True: #referenciada e inactiva
				cmds.textScrollList ("listaLuces1",e=1,si=luz)
				index= cmds.textScrollList ("listaLuces1",q=1,sii=1)[0]
				cmds.textScrollList ("listaLuces1", e=1, lf=[index,"tinyBoldLabelFont"])
				cmds.textScrollList ("listaLuces2", e=1, lf=[index,"tinyBoldLabelFont"])
				cmds.textScrollList ("listaLuces3", e=1, lf=[index,"tinyBoldLabelFont"])
			elif qVisibilidadAbsoluta(luz)==False and cmds.referenceQuery( luz ,isNodeReferenced=1 )==False: #referenciada e inactiva
				cmds.textScrollList ("listaLuces1",e=1,si=luz)
				index= cmds.textScrollList ("listaLuces1",q=1,sii=1)[0]
				cmds.textScrollList ("listaLuces1", e=1, lf=[index,"boldLabelFont"])
				cmds.textScrollList ("listaLuces2", e=1, lf=[index,"boldLabelFont"])
				cmds.textScrollList ("listaLuces3", e=1, lf=[index,"boldLabelFont"])
			elif qVisibilidadAbsoluta(luz)==True and cmds.referenceQuery( luz ,isNodeReferenced=1 )==False: #referenciada e inactiva
				cmds.textScrollList ("listaLuces1",e=1,si=luz)
				index= cmds.textScrollList ("listaLuces1",q=1,sii=1)[0]
				cmds.textScrollList ("listaLuces1", e=1, lf=[index,"plainLabelFont"])
				cmds.textScrollList ("listaLuces2", e=1, lf=[index,"plainLabelFont"])
				cmds.textScrollList ("listaLuces3", e=1, lf=[index,"plainLabelFont"])
			cmds.textScrollList ("listaLuces1",e=1,da=1)
			cmds.textScrollList ("listaLuces2",e=1,da=1)
			cmds.textScrollList ("listaLuces3",e=1,da=1)
	try:
		cmds.textScrollList ("listaLuces1",e=1,sii=seleccionLista1)
		cmds.textScrollList ("listaLuces2",e=1,sii=seleccionLista1)
		cmds.textScrollList ("listaLuces3",e=1,sii=seleccionLista1)
	except:
		pass

def enableCampos(camposAtributos={}):
	# HABILITAR DESHABILITAR
	lucesSeleccionadas=cmds.textScrollList ('listaLuces1',q=1,si=1)
	if len(lucesSeleccionadas)!=0:
		for campo in camposAtributos.keys():
			if camposAtributos[campo] != len(lucesSeleccionadas) and camposAtributos!="aiColorTemperature":
				try:
					cmds.floatField ( campo , e=1 , en=0)
				except:
					pass
				try:
					cmds.checkBox ( campo , e=1  , en=0 )
				except:
					pass
				if campo=="color":
					try:
						cmds.colorSliderGrp( campo , e=1 , en=0 )
					except:
						pass
			else:
				try:
					cmds.floatField ( campo , e=1 , en=1)
				except:
					pass
				try:
					cmds.checkBox ( campo , e=1  , en=1 )
				except:
					pass
				if campo=="color":
					try:
						cmds.colorSliderGrp( campo , e=1 , en=1 )
					except:
						pass

def enableTempColor (*args):
	lucesSeleccionadas = cmds.textScrollList ('listaLuces1',q=1,si=1)
	tienenTempColorOn=[]
	tienenTempColorOff=[]
	if lucesSeleccionadas!=None:
		for l in lucesSeleccionadas:
			if cmds.getAttr( l+"SH.aiUseColorTemperature")==0:
				tienenTempColorOff.append(l)
			elif cmds.getAttr( l+"SH.aiUseColorTemperature")==1:
				tienenTempColorOn.append(l)
		if len(tienenTempColorOn) == len(lucesSeleccionadas) :
			cmds.floatField ("aiColorTemperature" , e=1 , en=1 )
		elif len(tienenTempColorOff) == len(lucesSeleccionadas) :
			cmds.floatField ("aiColorTemperature" , e=1 , en=0 , v=0 , bgc=[0.1,0.1,0.1])
		elif tienenTempColorOff==[] and tienenTempColorOn==[] and lucesSeleccionadas==None:
			cmds.floatField ("aiColorTemperature" , e=1 , en=0 , v=0 , bgc=[0.1,0.1,0.1])
		else:
			cmds.floatField ("aiColorTemperature" , e=1 , en=1)

		cmds.iconTextButton('b_masCalido',e=1 , en=1)
		cmds.iconTextButton('b_masFrio',  e=1 , en=1)
	else:
		cmds.iconTextButton('b_masCalido',e=1 , en=0)
		cmds.iconTextButton('b_masFrio',  e=1 , en=0)

def maxmin():
	#variables
	lucesSeleccionadas = cmds.textScrollList('listaLuces1' ,q=1, si=1)
	camposAtributosMin   = {"aiExposure":0 , "aiRadius":0, "intensity":0, "aiAngle":0, "aiSamples":0, "aiColorTemperature":0, "aiShadowDensity":0 }
	camposAtributosMax   = {"aiExposure":0 , "aiRadius":0, "intensity":0, "aiAngle":0, "aiSamples":0, "aiColorTemperature":0, "aiShadowDensity":0  }
	for luz in lucesSeleccionadas:
		for key in camposAtributosMin.keys(): # CAPTURO VALORES
			if (cmds.attributeQuery (key , node=luz+"SH" , ex=1)):
				camposAtributosMin[key]= [luz, cmds.getAttr ( luz+"SH."+key ) ]
				camposAtributosMax[key]= [luz, cmds.getAttr ( luz+"SH."+key ) ]
	for luz in lucesSeleccionadas:
		for key in camposAtributosMin.keys():
			if (cmds.attributeQuery ( key , node = luz+"SH" , ex=1)):
				try:
					if cmds.getAttr(luz+"."+key)<camposAtributosMin[key][1]:
						camposAtributosMin[key][1]=cmds.getAttr(luz+"."+key)
						camposAtributosMin[key][0]=luz
				except:
					pass
	for luz in lucesSeleccionadas:
		for key in camposAtributosMax.keys():
			if (cmds.attributeQuery ( key , node = luz+"SH" , ex=1)):
				try:
					if cmds.getAttr(luz+"."+key)>camposAtributosMax[key][1]:
						camposAtributosMax[key][1]=cmds.getAttr(luz+"."+key)
						camposAtributosMax[key][0]=luz
				except:
					pass
	if len(lucesSeleccionadas)>1 :
		for campo in camposAtributosMin.keys():
			try:
				cmds.floatField (campo  , e=1 , ann= "MIN: " + camposAtributosMin[campo][0]+"  "+ str(camposAtributosMin[campo][1]) +"\n"+"MAX: " + camposAtributosMax[campo][0]+ "  " + str(camposAtributosMax[campo][1])+"\n"+"PROMEDIO: "+ str( (camposAtributosMax[campo][1]- camposAtributosMin[campo][1])/2+camposAtributosMin[campo][1] ))
			except:
				pass
	else:
		cmds.floatField ('intensity'  , e=1 , ann= "")
		cmds.floatField ('aiExposure' , e=1 , ann= "")
		cmds.floatField ('aiRadius'   , e=1 , ann= "")
		cmds.floatField ('aiAngle'    , e=1 , ann= "")
		cmds.floatField ('aiSamples'  , e=1 , ann= "")
		cmds.floatField ('aiColorTemperature'  , e=1 , ann= "")

def dropListas():
	pop = cmds.popupMenu(p='listaLuces1')
	cmds.menuItem(l="DUPLICAR" , c=duplicarLuz , p=pop)
	cmds.menuItem( divider=1, dividerLabel= " " , p=pop)
	cmds.menuItem(l="VER A TRAVES DE ESTA LUZ     || DOBLE CLICK || " , c= verAtraves,  en=1 ,p=pop)
	cmds.menuItem( divider=1, dividerLabel= " " , p=pop)
	cmds.menuItem(l="RENOMBRAR" , c=renombrarLuz, en=1 , p=pop)
	cmds.menuItem( divider=1, dividerLabel= " " , p=pop)
	cmds.menuItem(l="CREAR PRESET" , c='print "crearPreset()"', en=0 , p=pop)
	pop = cmds.popupMenu(p='listaLuces2')#|textScrollList
	cmds.menuItem(l="DUPLICAR" , c=duplicarLuz , p=pop)
	cmds.menuItem( divider=1, dividerLabel= " " , p=pop)
	cmds.menuItem(l="CREAR PRESET" , c='print "crearPreset()"', en=0 , p=pop)
	cmds.menuItem( divider=1, dividerLabel= " " , p=pop)
	cmds.menuItem(l="VER A TRAVES DE ESTA LUZ" , c=verAtraves,  en=0 ,p=pop)
	pop = cmds.popupMenu(p='listaLuces3')#|textScrollList
	cmds.menuItem(l="RENOMBRAR GRUPO" , c=renombrarGrupo, p=pop)
	cmds.menuItem( divider=1, dividerLabel= " " , p=pop)
	cmds.menuItem(l="VISIBILIDAD" , ann="PODES VER LA RUTA COMPLETA DE LA LUZ PARA ADMINISTRAR SU VISIBILIDAD Y LA DE LOS GRUPOS A LOS QUE PERTENECE.", c=visibilidadDeRuta, p=pop)

def mirarPorLuz(*args):
	try:
		cmds.lookThru(cmds.textScrollList ( 'listaLuces1' , q=1 , si=1 )[0] )
	except:
		pass

def setInt(*args):
    try:
        lucesSeleccionadas = cmds.textScrollList ('listaLuces1', q=1 , si=1)
        for luz in lucesSeleccionadas:
            try:
                if cmds.radioCollection('radioAbsRel',q=1,sl=1)=='A':
                    cmds.setAttr (luz+'SH.intensity', cmds.floatField ('intensity',q=1,v=1) )
                else:
                    cmds.setAttr (luz+'SH.intensity',  cmds.getAttr ( luz+'SH.intensity' ) +   cmds.floatField ('intensity',q=1,v=1) )
            except:
                pass
        cmds.textScrollList ('listaLuces1',e=1,si=lucesSeleccionadas)
    except:
        pass
    refreshui()

def setExp(*args):
    try:
        lucesSeleccionadas = cmds.textScrollList ('listaLuces1', q=1 , si=1)
        for luz in lucesSeleccionadas:
            try:
                if cmds.radioCollection('radioAbsRel',q=1,sl=1)=='A':
                    cmds.setAttr (luz+'SH.aiExposure', cmds.floatField ('aiExposure',q=1,v=1) )
                else:
                    cmds.setAttr (luz+'SH.aiExposure',  cmds.getAttr ( luz+'SH.aiExposure' ) +   cmds.floatField ('aiExposure',q=1,v=1) )
            except:
                pass
        cmds.textScrollList ('listaLuces1',e=1,si=lucesSeleccionadas)
    except:
        pass
    refreshui()

def setRad(*args):
    try:
        lucesSeleccionadas = cmds.textScrollList ('listaLuces1', q=1 , si=1)
        for luz in lucesSeleccionadas:
            try:
                if cmds.radioCollection('radioAbsRel',q=1,sl=1)=='A':
                    cmds.setAttr (luz+'SH.aiRadius', cmds.floatField ('aiRadius',q=1,v=1) )
                else:
                    cmds.setAttr (luz+'SH.aiRadius',  cmds.getAttr ( luz+'SH.aiRadius' ) +   cmds.floatField ('aiRadius',q=1,v=1) )
            except:
                pass
    except:
        pass
    refreshui()

def setAng(*args):
    try:
        lucesSeleccionadas = cmds.textScrollList ('listaLuces1', q=1 , si=1)
        for luz in lucesSeleccionadas:
            try:
                if cmds.radioCollection('radioAbsRel',q=1,sl=1)=='A':
                    cmds.setAttr (luz+'SH.aiAngle', cmds.floatField ('aiAngle',q=1,v=1) )
                else:
                    cmds.setAttr (luz+'SH.aiAngle',  cmds.getAttr ( luz+'SH.aiAngle' ) +   cmds.floatField ('aiAngle',q=1,v=1) )
            except:
                pass
    except:
        pass
    refreshui()

def setShadowDensity(*args):
    try:
        lucesSeleccionadas = cmds.textScrollList ('listaLuces1', q=1 , si=1)
        for luz in lucesSeleccionadas:
            try:
                if cmds.radioCollection('radioAbsRel',q=1,sl=1)=='A':
                    cmds.setAttr (luz+'SH.aiShadowDensity', cmds.floatField ('aiShadowDensity',q=1,v=1) )
                else:
                    cmds.setAttr (luz+'SH.aiShadowDensity',  cmds.getAttr ( luz+'SH.aiShadowDensity' ) +   cmds.floatField ('aiShadowDensity',q=1,v=1) )
            except:
                pass
    except:
        pass
    refreshui()

def setSamp(*args):
    try:
        lucesSeleccionadas = cmds.textScrollList ('listaLuces1', q=1 , si=1)
        for luz in lucesSeleccionadas:
            try:
                if cmds.radioCollection('radioAbsRel',q=1,sl=1)=='A':
                    cmds.setAttr (luz+'SH.aiSamples', cmds.floatField ('aiSamples',q=1,v=1) )
                else:
                    cmds.setAttr (luz+'SH.aiSamples',  cmds.getAttr ( luz+'SH.aiSamples' ) +   cmds.floatField ('aiSamples',q=1,v=1) )
            except:
                pass
    except:
        pass
    refreshui()

def setColor(*args):
	try:
		lucesSeleccionadas = cmds.textScrollList ('listaLuces1', q=1 , si=1)
		rgbSet=cmds.colorSliderGrp ('color',q=1,rgb=1)
		for luz in lucesSeleccionadas:
			try:
				cmds.setAttr (luz+".aiUseColorTemperature",0)
				cmds.setAttr (luz+'SH.color',rgbSet[0],rgbSet[1],rgbSet[2],type='double3' )
			except:
				pass
	except:
		pass
	refreshui()

def setTempColor(*args):
	try:
		lucesSeleccionadas = cmds.textScrollList ('listaLuces1', q=1 , si=1)
		for luz in lucesSeleccionadas:
			try:
				cmds.setAttr (luz+".aiUseColorTemperature",1)
				if cmds.radioCollection('radioAbsRel',q=1,sl=1)=='A':
					cmds.setAttr (luz+'SH.aiColorTemperature', cmds.floatField ('aiColorTemperature',q=1,v=1) )
				else:
					cmds.setAttr (luz+'SH.aiColorTemperature',  cmds.getAttr ( luz+'SH.aiColorTemperature' ) +   cmds.floatField ('aiColorTemperature',q=1,v=1) )
			except:
				pass
	except:
		pass
	refreshui()

def setilumDef(*args):
	cmds.warning ("-")

def setDif(*args):
    try:
        lucesSeleccionadas = cmds.textScrollList ('listaLuces1', q=1 , si=1)
        for luz in lucesSeleccionadas:
            try:
                cmds.setAttr (luz+'SH.emitDiffuse', cmds.checkBox ('emitDiffuse',q=1,v=1) )
            except:
                pass
    except:
        pass
    refreshui()

def setSpec(*args):
    try:
        lucesSeleccionadas = cmds.textScrollList ('listaLuces1', q=1 , si=1)
        for luz in lucesSeleccionadas:
            try:
                cmds.setAttr (luz+'SH.emitSpecular', cmds.checkBox ('emitSpecular',q=1,v=1) )
            except:
                pass
    except:
        pass
    refreshui()

def setconeangle(*args):
    try:
        lucesSeleccionadas = cmds.textScrollList ('listaLuces1', q=1 , si=1)
        for luz in lucesSeleccionadas:
            try:
                if cmds.radioCollection('radioAbsRel',q=1,sl=1)=='A':
                    cmds.setAttr (luz+'SH.coneAngle', cmds.floatField ('coneAngle',q=1,v=1) )
                else:
                    cmds.setAttr (luz+'SH.coneAngle',  cmds.getAttr ( luz+'SH.coneAngle' ) +   cmds.floatField ('coneAngle',q=1,v=1) )
            except:
                pass
    except:
        pass
    refreshui()

def setpenumbraAngle(*args):
	try:
	    lucesSeleccionadas = cmds.textScrollList ('listaLuces1', q=1 , si=1)
	    for luz in lucesSeleccionadas:
	        try:
	            if cmds.radioCollection('radioAbsRel',q=1,sl=1)=='A':
	                cmds.setAttr (luz+'SH.penumbraAngle', cmds.floatField ('penumbraAngle',q=1,v=1) )
	            else:
	                cmds.setAttr (luz+'SH.penumbraAngle',  cmds.getAttr ( luz+'SH.penumbraAngle' ) +   cmds.floatField ('penumbraAngle',q=1,v=1) )
	        except:
	            pass
	except:
	    pass
	refreshui()

def setdropoff(*args):
    try:
        lucesSeleccionadas = cmds.textScrollList ('listaLuces1', q=1 , si=1)
        for luz in lucesSeleccionadas:
            try:
                if cmds.radioCollection('radioAbsRel',q=1,sl=1)=='A':
                    cmds.setAttr (luz+'SH.dropoff', cmds.floatField ('dropoff',q=1,v=1) )
                else:
                    cmds.setAttr (luz+'SH.dropoff',  cmds.getAttr ( luz+'SH.dropoff' ) +   cmds.floatField ('dropoff',q=1,v=1) )
            except:
                pass
    except:
        pass
    refreshui()

def borrarSeleccion():
	try:
		lucesSeleccionadas = cmds.textScrollList ( 'listaLuces1' , q=1 , si=1 )
		for luz in lucesSeleccionadas:
			cmds.delete(luz)
		cmds.textScrollList ( 'listaLuces1' , e=1 , da=1 )
		ordenarLuz()
	except:
		pass

def ordenarTipo2(*args):
	global orden
	lucesShapes=[]
	tipos_de_Luces=[]
	filtro_tipos=[]
	tipo_de_Luz=""
	lucesTodas = cmds.ls(['*_LPNTSH','*_LDIRSH','*_LARESH','*_LAMBSH','*_LSPTSH','*_DOMESH'],r=1)
	try:
		items= cmds.textScrollList ('listaLuces1' , q=1, allItems=1) #items en la lista
		seleccionar = cmds.textScrollList ('listaLuces1' , q=1 , si=1 ) # seleccion de la lista
	except:
		seleccionar=1
		pass
	if len(lucesTodas)!=0:
		if len(items)!=0:
			for item in items:
				tipo_de_Luz=  cmds.nodeType( cmds.listRelatives(item)[0] )
				tipos_de_Luces.append (tipo_de_Luz)
			if "spotLight" in tipos_de_Luces:
			    filtro_tipos.append("*_LSPTSH")
			if "pointLight" in tipos_de_Luces:
			    filtro_tipos.append("*_LPNTSH")
			if "areaLight" in tipos_de_Luces:
			    filtro_tipos.append("*_LARESH")
			if "directionalLight" in tipos_de_Luces:
			    filtro_tipos.append("*_LDIRSH")
			if "aiSkyDomeLight" in tipos_de_Luces:
			    filtro_tipos.append("*_DOMESH")
			datosOrdenados = ordenarDatos(ordenarPor='tipo', filtrado=filtro_tipos )
			listas = ['listaLuces1','listaLuces2','listaLuces3']
			if orden["tipo"]%2 == 1:
				datosOrdenados[0].reverse()
				datosOrdenados[1].reverse()
				datosOrdenados[2].reverse()
			for lista in listas:
				cmds.textScrollList (lista, e=1 ,ra=1)
			cmds.textScrollList ('listaLuces1' , e=1  ,  a= datosOrdenados[0] , numberOfRows = len(datosOrdenados[0])+2, si=seleccionar)
			indiceSeleccionLista1 = cmds.textScrollList ('listaLuces1' , q=1 , sii=1 )
			cmds.textScrollList ('listaLuces2' , e=1  ,  a=datosOrdenados[1] , numberOfRows = len(datosOrdenados[0])+2, sii=indiceSeleccionLista1)
			cmds.textScrollList ('listaLuces3' , e=1  ,  a=datosOrdenados[2] , numberOfRows = len(datosOrdenados[0])+2, sii=indiceSeleccionLista1)
			boldOblique()
			cmds.textScrollList ('listaLuces1' , e=1  ,  da=1)
			cmds.textScrollList ('listaLuces1' , e=1 , si=seleccionar )
			cmds.textScrollList ('listaLuces2' , e=1  ,  da=1)
			cmds.textScrollList ('listaLuces2' , e=1  ,  sii= cmds.textScrollList ('listaLuces1' , q=1 , sii=1 ))
			cmds.textScrollList ('listaLuces3' , e=1  ,  da=1)
			cmds.textScrollList ('listaLuces3' , e=1  ,  sii= cmds.textScrollList ('listaLuces1' , q=1 , sii=1 ))
			orden["tipo"]+=1
			ultimoOrden="tipo"
	else:
		cmds.textScrollList('listaLuces1',e=1,ra=1)
		cmds.textScrollList('listaLuces2',e=1,ra=1)
		cmds.textScrollList('listaLuces3',e=1,ra=1)
		cmds.warning ("---- NO SE DETECTARON LUCES ADMITIDAS ----")

def ordenarDatos(ordenarPor , filtrado=''):
    if filtrado=='':
	    luces = cmds.ls(['*_LPNTSH','*_LDIRSH','*_LARESH','*_LAMBSH','*_LSPTSH','*_DOMESH'],r=1)
    else:
    	luces = cmds.ls( filtrado ,r=1)
    datos_Dic={}
    for l in luces:
        name = cmds.listRelatives(l,type='transform',p=True)[0]
        grupo = cmds.listRelatives(name,type='transform',p=True)[0]
        lightType = cmds.nodeType(l)
        datos_Dic[name] = [lightType,l,grupo]
    lucesOrdenadas_=[]
    tiposOrdenados_=[]
    gruposOrdenados_=[]
    lucesTuplas=[]
    dicLuces_xTipo={}
    dicLuces_xGrupo={}
    # ORDENA POR NOMBRE
    if ordenarPor=='luz':
        lucesTuplas = sorted(datos_Dic.items(), key=itemgetter(0))
        for tupla in lucesTuplas:
            lucesOrdenadas_.append (tupla[0])
            tiposOrdenados_.append (tupla[1][0])
            gruposOrdenados_.append ( tupla[1][2].split('_LGRP')[0] )
    # ORDENA POR TIPO
    elif ordenarPor=='tipo':
        for key in datos_Dic.keys():
            dicLuces_xTipo[key] = datos_Dic [key][0]
            dicLuces_xGrupo[key] = datos_Dic [key][2]
        tuplas = sorted(dicLuces_xTipo.items(), key=itemgetter(1))
        for tupla in tuplas:
            lucesOrdenadas_.append (tupla[0])
            tiposOrdenados_.append (tupla[1])
            gruposOrdenados_.append (dicLuces_xGrupo [ tupla[0] ].split('_LGRP')[0] )
    # ORDENA POR GRUPO
    elif ordenarPor=='grupo':
        for key in datos_Dic.keys():
            dicLuces_xTipo[key] = datos_Dic [key][0]
            dicLuces_xGrupo[key] = datos_Dic [key][2]
        tuplas = sorted(dicLuces_xGrupo.items(), key=itemgetter(1))
        for tupla in tuplas:
            lucesOrdenadas_.append (tupla[0])
            gruposOrdenados_.append (tupla[1].split('_LGRP')[0] )
            tiposOrdenados_.append (dicLuces_xTipo [ tupla[0] ] )
    return [lucesOrdenadas_,tiposOrdenados_,gruposOrdenados_]

def ordenarGrupo(seleccionar=1):
	global orden
	lucesTodas = cmds.ls(['*_LPNTSH','*_LDIRSH','*_LARESH','*_LAMBSH','*_LSPTSH','*_DOMESH'],r=1)
	if len(lucesTodas)!=0:
		datosOrdenados = ordenarDatos(ordenarPor='grupo', filtrado='' )
		listas = ['listaLuces1','listaLuces2','listaLuces3']
		if orden["grupo"]%2 == 1:
			datosOrdenados[0].reverse()
			datosOrdenados[1].reverse()
			datosOrdenados[2].reverse()
		try:
			seleccionar = cmds.textScrollList ('listaLuces1' , q=1 , si=1 )
		except:
			pass
		for lista in listas:
			cmds.textScrollList (lista, e=1 ,ra=1)
		cmds.textScrollList ('listaLuces1' , e=1  ,  a= datosOrdenados[0] , numberOfRows = len(datosOrdenados[0])+2, si=seleccionar)
		indiceSeleccionLista1 = cmds.textScrollList ('listaLuces1' , q=1 , sii=1 )
		cmds.textScrollList ('listaLuces2' , e=1  ,  a=datosOrdenados[1] , numberOfRows = len(datosOrdenados[0])+2, sii=indiceSeleccionLista1)
		cmds.textScrollList ('listaLuces3' , e=1  ,  a=datosOrdenados[2] , numberOfRows = len(datosOrdenados[0])+2, sii=indiceSeleccionLista1)
		boldOblique()
		cmds.textScrollList ('listaLuces1' , e=1  ,  da=1)
		cmds.textScrollList ('listaLuces1' , e=1 , si=seleccionar )
		cmds.textScrollList ('listaLuces2' , e=1  ,  da=1)
		cmds.textScrollList ('listaLuces2' , e=1  ,  sii= cmds.textScrollList ('listaLuces1' , q=1 , sii=1 ))
		cmds.textScrollList ('listaLuces3' , e=1  ,  da=1)
		cmds.textScrollList ('listaLuces3' , e=1  ,  sii= cmds.textScrollList ('listaLuces1' , q=1 , sii=1 ))
		orden["grupo"]+=1
		ultimoOrden="grupo"
	else:
		cmds.textScrollList('listaLuces1',e=1,ra=1)
		cmds.textScrollList('listaLuces2',e=1,ra=1)
		cmds.textScrollList('listaLuces3',e=1,ra=1)
		cmds.warning ("---- NO SE DETECTARON LUCES ADMITIDAS ----")

def cambiarGrupo(grupoParaMoverA=""):
    global seleccionLista1
    global orden
    seleccion1=cmds.textScrollList('listaLuces1',q=1,si=1)
    seleccion2=cmds.textScrollList('listaLuces2',q=1,si=1)
    lucesSeleccionadas = cmds.textScrollList('listaLuces1',q=1,si=1)
    if lucesSeleccionadas !=None:
        if len(cmds.textScrollList('listaLuces1',q=1,si=1))!=0:
            lucesSeleccionadas = cmds.textScrollList('listaLuces1' ,q=1, si=1)
            lucesSeleccionadasInd = cmds.textScrollList('listaLuces1' ,q=1, sii=1)
            if grupoParaMoverA=="":
                grupoSeleccionado = cmds.optionMenu ( (grupoVG +'|OptionMenu')  , q=1 , value=1)
            else:
                grupoSeleccionado = grupoParaMoverA[:-5]

            if "_LGRP" in grupoParaMoverA:
                for luz in lucesSeleccionadas:
                    try:
                        cmds.parent ( luz ,grupoParaMoverA )
                    except:
                        pass
                refrescar()
            else:
                for luz in lucesSeleccionadas:
                    try:
                        if cmds.listRelatives ( luz ,p=1 )[0]!= grupoParaMoverA+'_LGRP':
                            cmds.parent ( luz ,grupoParaMoverA  + '_LGRP' )
                    except:
                        pass
            seleccion3=cmds.textScrollList('listaLuces3',q=1,si=1)
            cmds.textScrollList('listaLuces1',e=1,si=seleccion1)
            cmds.textScrollList('listaLuces2',e=1,si=seleccion2)
            cmds.textScrollList('listaLuces3',e=1,si=seleccion3)
            ordenarLuz()
            refreshui()
    else:
        cmds.warning(' - - - AHORA PODES EDITAR LOS GRUPOS - - - ')

def crearGrupo(*args):
	global ultimoGrupoCreadoPorUsuario
	global seleccionLista1
	global grupoVG
	global dock
	seleccionLista1 = cmds.textScrollList ('listaLuces1',q=1,si=1)

	pideNombreGrupo = 'OK'
	arrancaConNumero=1
	rootDeEscena = ""
	roots = cmds.ls('ROOT_*_LGRP',r=1)
	listaDeRootsNoReferenciados=[]
	if len( roots ) == 1:
		rootDeEscena = roots [0]
	elif len( roots ) > 1:
		for root in roots:
			if cmds.referenceQuery( root ,isNodeReferenced=1 ) == False:
				listaDeRootsNoReferenciados.append (root)
	else:
		rootDeEscena = ""
	if rootDeEscena != "" or len(listaDeRootsNoReferenciados)==1:
		while pideNombreGrupo=='OK' and arrancaConNumero==1:
			pideNombreGrupo = cmds.promptDialog(title='NOMBRAR',message='NOMBRE DE GRUPO:',button=['OK', 'CANCELAR'],defaultButton='OK',cancelButton='CANCELAR',dismissString='Cancel')
			if cmds.promptDialog(query=True, text=True)!="" and pideNombreGrupo != "CANCELAR":
				if pideNombreGrupo == 'OK' and str(cmds.promptDialog(query=True, text=True))[0].isdigit()==False:
					arrancaConNumero=0
					qNombreGrupo = cmds.promptDialog(query=True, text=True)
					nombreDelGrupoCreado=cmds.group(name = qNombreGrupo.upper() + '_LGRP', em=True, w=True)
					cmds.parent ( qNombreGrupo.upper() + '_LGRP' , cmds.ls('ROOT_*_LGRP')[0] )
					rootAts = cmds.listAttr (qNombreGrupo.upper() + '_LGRP' , k=1 )
					for at in rootAts:
					    if at != "visibility":
						    cmds.setAttr (qNombreGrupo.upper() + '_LGRP'+"."+at,lock=1,k=0,channelBox=0)
					    else:
						    cmds.setAttr (qNombreGrupo.upper() + '_LGRP'+"."+at,lock=0,k=0,channelBox=1)
					#ACTUALIZO GRUPOS
					clearOptionMenu (grupoVG)
					gruposDeLuces = cmds.ls ( '*_LGRP' , type='transform' )
					rootDeLaEscena= cmds.ls ( 'ROOT_*_LGRP' , type='transform' )
					for grp in gruposDeLuces:
						if grp != rootDeLaEscena[0]:
						    cmds.menuItem(parent=( dock +  grupoVG.split("winMLuces")[1] ), label=grp[:-5] ) #########################
					clearOptionMenu (grupoCParent)
					gruposDeLuces = cmds.ls ( '*_LGRP' , type='transform' )
					for grp in gruposDeLuces:
						if grp != rootDeLaEscena[0]:
							cmds.menuItem ( parent= dock +  grupoCParent.split("winMLuces")[1] , label=grp[:-5] )

				elif pideNombreGrupo == 'OK' and str(cmds.promptDialog(query=True, text=True))[0].isdigit()==True:
					cmds.warning ( "EL NOMBRE NO PUEDE COMENZAR CON UN NUMERO." )
				else:
					cmds.warning ( "USUARIO CANCELA" )
					return ""
			else:
				cmds.warning (" - - - CANCELADO - - - ")

				return ""
		if pideNombreGrupo=='OK':
			ultimoGrupoCreadoPorUsuario=nombreDelGrupoCreado
			cambiarGrupo(grupoParaMoverA=nombreDelGrupoCreado)
			return nombreDelGrupoCreado
	else:
		cmds.warning ("NO HAY UN ROOT UNICO.")

def tipoSel():
	cmds.textScrollList ('listaLuces2',e=1,si= cmds.textScrollList ('listaLuces2',q=1,si=1  ) )
	cmds.textScrollList ('listaLuces1',e=1,sii=cmds.textScrollList ('listaLuces2',q=1,sii=1  ) )
	cmds.textScrollList ('listaLuces3',e=1,sii=cmds.textScrollList ('listaLuces2',q=1,sii=1  ) )

def grpSel():
	cmds.textScrollList ('listaLuces3',e=1,si= cmds.textScrollList ('listaLuces3',q=1,si=1  ) )
	cmds.textScrollList ('listaLuces1',e=1,sii=cmds.textScrollList ('listaLuces3',q=1,sii=1  ) )
	cmds.textScrollList ('listaLuces2',e=1,sii=cmds.textScrollList ('listaLuces3',q=1,sii=1  ) )

def construirScrollsConBotones( emparentarA='') :
	lightList = cmds.ls(['*_LPNTSH','*_LDIRSH','*_LARESH','*_LAMBSH','*_LSPTSH','*_DOMESH'],r=1)
	dicLuces={}
	for l in lightList:
		name = cmds.listRelatives(l,type='transform',p=True)[0]
		grupo = cmds.listRelatives(name,type='transform',p=True)[0]
		lightType = cmds.nodeType(l)
		dicLuces[name]= [lightType,l,grupo]
	r_00 = cmds.rowLayout ('r_00', nc = 5 , p = 'row1' ,bgc=(0.27,0.27,0.27), h = 30 , cw5= [ 50 , 250 , 85 , 100 , 25 ] , ct5= ["both", "both", "both", "both" , "both"])
	cmds.iconTextButton  (ann='REFRESCAR GUI',  style='iconOnly',image1='refresh.png', c = refrescar ,width=15,height=20,p=r_00 )

	cmds.iconTextButton  (l ='LUZ',ann='LUZ',style='textOnly',image1='M:\PH_SCRIPTS\ICONS\LSPT_1.png', c = ordenarLuz     ,p=r_00 ,bgc=(0.27,0.27,0.27) ,font= "plainLabelFont")
	cmds.iconTextButton (l ='TIPO',ann='TIPO',style='textOnly',image1='M:\PH_SCRIPTS\ICONS\LPNT_1.png', c = ordenarTipo2    ,p=r_00 ,bgc=(0.27,0.27,0.27) ,font= "plainLabelFont")
	cmds.iconTextButton  (l ='GRUPO',ann='GRUPO',style='textOnly',image1='M:\PH_SCRIPTS\ICONS\LARE_1.png', c = ordenarGrupo ,p=r_00 ,bgc=(0.27,0.27,0.27) ,font= "plainLabelFont")

	b_isolate = cmds.iconTextButton  ('b_isolate',label='A',ann='AISLAR',en=1, style='iconOnly' ,image1='M:\PH_SCRIPTS\ICONS\PH_LUCES_ISOLATE_OFF.png' , c = isolateLuz ,width=15,height=25,p=r_00 )
	if 'isolate' in globals():
	    if isolate == True:
	        cmds.iconTextButton  ('b_isolate' , e = 1 ,  image1 = 'M:\PH_SCRIPTS\ICONS\PH_LUCES_ISOLATE.png' )
	r_01 = cmds.rowLayout ( nc = 3 , cw3 = [ 305 , 80 , 100 ] ,  p = emparentarA )
	c_01 = cmds.columnLayout ('c_01', p = r_01 , adjustableColumn=1)
	c_02 = cmds.columnLayout (        p = r_01 , adjustableColumn=1)
	c_03 = cmds.columnLayout (        p = r_01 , adjustableColumn=1)
	cmds.textScrollList('listaLuces1' , w = 300 , allowMultiSelection=1, p = c_01 , dcc=verAtraves , deleteKeyCommand=borrarSeleccion)
	cmds.textScrollList('listaLuces2' , w = 100 , allowMultiSelection = 1 , p = c_02 , bgc = [0.24,0.24,0.24] , dcc=tipoSel ,deleteKeyCommand=borrarSeleccion )
	cmds.textScrollList('listaLuces3' , w = 100 , allowMultiSelection = 1 , p = c_03 , bgc = [0.24,0.24,0.24] , dcc=grpSel ,deleteKeyCommand=borrarSeleccion)
	datosOrdenados = ordenarDatos(ordenarPor='luz' , filtrado='')
	cmds.textScrollList ('listaLuces1' , e=1 ,allowMultiSelection=1, a=datosOrdenados[0] , sc=partial(refreshui,'luz') ,  enable=1 ,h = (len(datosOrdenados[0])+2)*100)
	cmds.textScrollList ('listaLuces2' , e=1 ,allowMultiSelection=1, a=datosOrdenados[1] , sc=partial(refreshui,'tipo')  , enable=1 , h = (len(datosOrdenados[0])+2)*100 )
	cmds.textScrollList ('listaLuces3' , e=1 ,allowMultiSelection=1, a=datosOrdenados[2] , sc=partial(refreshui,'grupo')   , enable=1 ,h = (len(datosOrdenados[0])+2)*100 )
	cmds.textField ( 'buscador' , e=1 , aie= 1 , changeCommand = buscar,  pht="Buscar luces" )
	boldOblique()

def buscar(*args):
	global buscarPor_Grupo_Luz
	global seleccion
	recolectorBusqueda=[]
	try:
		textoBuscador = cmds.textField ( 'buscador' , q=1 , text=True)
		if len(textoBuscador)!=0:
			if buscarPor_Grupo_Luz=='luz':
				if str(textoBuscador[0]).isdigit() ==1:
					recolectorBusqueda= cmds.ls("*"+textoBuscador,"*"+textoBuscador+"*", type='light')
				else:
					recolectorBusqueda= cmds.ls(textoBuscador+"*","*"+textoBuscador,"*"+textoBuscador+"*",textoBuscador , textoBuscador.upper()+"*","*"+textoBuscador.upper(),"*"+textoBuscador.upper()+"*",textoBuscador.upper() , type='light')
					recolectorBusqueda = recolectorBusqueda + cmds.ls (type="aiSkyDomeLight")
			elif buscarPor_Grupo_Luz=='grupo':
				if str(textoBuscador[0]).isdigit() ==1:
					gruposRecolectados= cmds.ls("*"+textoBuscador,"*"+textoBuscador+"*", type='transform')
					gruposRecolectados=list(set(gruposRecolectados))
				else:
					gruposRecolectados= cmds.ls(textoBuscador+"*","*"+textoBuscador,"*"+textoBuscador+"*",textoBuscador , textoBuscador.upper()+"*","*"+textoBuscador.upper(),"*"+textoBuscador.upper()+"*",textoBuscador.upper() , type='transform')
					gruposRecolectados=list(set(gruposRecolectados))
					for trf in gruposRecolectados:
						if 'ROOT' in trf:
							gruposRecolectados.remove(trf)
					luces = cmds.ls(type='light')
					for l in luces:
						if cmds.listRelatives(cmds.listRelatives(l,p=1)[0] ,p=1)[0]  in gruposRecolectados:
							recolectorBusqueda.append (l)
			recolectorBusqueda=list(set(recolectorBusqueda))
			datos_Dic={}
			for l in recolectorBusqueda:
				name = cmds.listRelatives(l,type='transform',p=True)[0]
				grupo = cmds.listRelatives(name,type='transform',p=True)[0]
				lightType = cmds.nodeType(l)
				datos_Dic[name] = [lightType,l,grupo]
			lucesOrdenadas_=[]
			tiposOrdenados_=[]
			gruposOrdenados_=[]
			lucesTuplas=[]
			lucesTuplas = sorted(datos_Dic.items(), key=itemgetter(0))

			for tupla in lucesTuplas:
				lucesOrdenadas_.append (tupla[0])
				tiposOrdenados_.append (tupla[1][0])
				gruposOrdenados_.append (tupla[1][2][:-5])
			cmds.textScrollList ('listaLuces1' , e=1 , ra= 1)
			cmds.textScrollList ('listaLuces2' , e=1 , ra= 1)
			cmds.textScrollList ('listaLuces3' , e=1 , ra= 1)
			cmds.textScrollList ('listaLuces1' , e=1 , a= lucesOrdenadas_)
			cmds.textScrollList ('listaLuces2' , e=1 , a= tiposOrdenados_)
			cmds.textScrollList ('listaLuces3' , e=1 , a= gruposOrdenados_)
			mantenerSeleccion()

		else:
			refrescar()
	except:
		print " - - - NO SE HA PODIDO BUSCAR. REPORTAR ESTE ERROR - - - "

def onoff(*args):
	try:
		lucesSeleccionadas = cmds.textScrollList ('listaLuces1', q=1 , si=1)
		for luz in lucesSeleccionadas:
			if cmds.checkBox ('on_off',q=1,v=1):
				cmds.showHidden ( luz )
			else:
				cmds.hide ( luz )
	except:
	    pass
	refreshui()

def cambiarGrupoParent(*args):
	global grupoCParent
	global grupoVG
	if cmds.optionMenu (grupoVG,q=1,v=1)!=cmds.optionMenu (grupoCParent,q=1,v=1):
		try:
			cmds.parent (cmds.optionMenu (grupoVG,q=1,v=1)+"_LGRP",cmds.optionMenu (grupoCParent,q=1,v=1)+"_LGRP" )
		except:
			pass
	refreshui()

def borrarGrupo(*args):
    if cmds.optionMenu ( 'grupoVG' , q = 1 , numberOfItems= 1 ):
    	global grupoVG
    	if cmds.optionMenu (grupoVG,q=1,v=1)!="":
    		confirma=cmds.confirmDialog( title='BORRAR GRUPO', message='BORRAR '+cmds.optionMenu (grupoVG,q=1,v=1)+'?', button=['SI','NO'], defaultButton='SI', cancelButton='NO', dismissString='NO' )
    		if confirma=="SI":
    			cmds.delete (cmds.optionMenu (grupoVG,q=1,v=1)+'_LGRP')
    		else:
    			cmds.warning ("  ELIMINACION DE GRUPO CANCELADA  ")
    	refreshui()

def renombrarGrupo(*args):
    if cmds.optionMenu ( 'grupoVG' , q = 1 , numberOfItems= 1 ):
    	global grupoVG
    	grupoARenombrar = cmds.optionMenu (grupoVG,q=1,v=1)
    	if cmds.optionMenu (grupoVG,q=1,v=1)!="":
    		result = cmds.promptDialog(
    				title='RENOMBRA '+cmds.optionMenu (grupoVG,q=1,v=1),
    				message='Nuevo nombre:',
    				button=['OK', 'Cancel'],text=cmds.optionMenu (grupoVG,q=1,v=1),
    				defaultButton='OK',
    				cancelButton='Cancel',
    				dismissString='Cancel')
    		if result == 'OK':
    			if cmds.promptDialog(query=True, text=True)!="":
    				nombreNuevoGrupo = cmds.promptDialog(query=True, text=True)
    				if cmds.objExists(nombreNuevoGrupo+"_LGRP" )!=True:
    					cmds.rename ( cmds.optionMenu(grupoVG, q=1 , v=1)+"_LGRP" , nombreNuevoGrupo.upper()+"_LGRP")
    				else:
    					cmds.warning("YA EXISTE UN GRUPO CON EL NOMBRE DADO.")
    			else:
    				cmds.warning("NOMBRE INVALIDO")
    		else:
    			cmds.warning("RENOMBRADO CANCELADO")
    	ordenarGrupo()
    	refreshui()

def sss(*args):
    global deactivateSSS
    verde= [0.3,1,0.3]
    rojo = [1,0.3,0.3]
    if deactivateSSS == True:
        deactivateSSS = False
        cmds.iconTextButton  ('b_sss' , e=1 , bgc=verde)
        cmds.setAttr ( 'defaultArnoldRenderOptions.ignoreSss', 0)
    else:
        deactivateSSS = True
        cmds.iconTextButton  ('b_sss' , e=1 , bgc=rojo)
        cmds.setAttr ( 'defaultArnoldRenderOptions.ignoreSss', 1)

def disp(*args):
    global deactivateDisplacement
    verde= [0.3,1,0.3]
    rojo = [1,0.3,0.3]
    if deactivateDisplacement == True:
        deactivateDisplacement = False
        cmds.iconTextButton  ('b_disp' , e=1 , bgc=verde)
        cmds.setAttr ( 'defaultArnoldRenderOptions.ignoreDisplacement', 0)
    else:
        deactivateDisplacement = True
        cmds.iconTextButton  ('b_disp' , e=1 , bgc=rojo)
        cmds.setAttr ( 'defaultArnoldRenderOptions.ignoreDisplacement', 1)

def sub(*args):
    global deactivateSUB
    verde= [0.3,1,0.3]
    rojo = [1,0.3,0.3]
    if deactivateSUB == True:
        deactivateSUB = False
        cmds.iconTextButton  ('b_sub' , e=1 , bgc=verde)
        cmds.setAttr ( 'defaultArnoldRenderOptions.ignoreSubdivision', 0)
    else:
        deactivateSUB = True
        cmds.iconTextButton  ('b_sub' , e=1 , bgc=rojo)
        cmds.setAttr ( 'defaultArnoldRenderOptions.ignoreSubdivision', 1)

def asignarFiltro(*args):
	print "asignarFiltro"

def setBusquedaPorLuz(*args):
	global buscarPor_Grupo_Luz
	buscarPor_Grupo_Luz='luz'
	cmds.textField ( 'buscador' , e=1 , aie= 1 , changeCommand = buscar,  pht="Buscar luces" )

def setBusquedaPorGrupo(*args):
	global buscarPor_Grupo_Luz
	buscarPor_Grupo_Luz='grupo'
	cmds.textField ( 'buscador' , e=1 , aie= 1 , changeCommand = buscar,  pht="Buscar grupo" )

def copiarValorGet(control_,*args):
	global copiarValor
	copiarValor = cmds.floatField ( control_ ,q=1, v=1 )

def pegarValorGet(control_,*args):
	global copiarValor
	cmds.floatField ( control_ ,e=1, v=copiarValor )

def restaurarDefault (control_,*args):
	lucesSel = cmds.textScrollList ('listaLuces1' , q=1 , si=1)
	for l in lucesSel :
		valorDefault = cmds.attributeQuery( control_ , n=l+"SH",ld=1)[0]
		cmds.setAttr( l+"SH."+control_ , valorDefault)
		cmds.floatField ( control_ ,e=1, v=valorDefault )

def crearDropCopiarPegar (parent_=''):
	pop = cmds.popupMenu(p=parent_)
	cmds.menuItem(l="COPIAR VALOR"   , c = partial (copiarValorGet,parent_)   , p=pop)
	cmds.menuItem(l="PEGAR VALOR" , c = partial (pegarValorGet,parent_) ,p=pop)
	cmds.menuItem(l="RESTAURAR DEFAULT" , c = partial (restaurarDefault,parent_) ,p=pop)

def setTemperaturaColor (temperaturaColor ,*args):
	luces = cmds.textScrollList ('listaLuces1',q=1,si=1)
	try:
		for l in luces:
			cmds.setAttr (l+".aiUseColorTemperature",1)
			cmds.setAttr (l+'.aiColorTemperature',temperaturaColor)
			cmds.floatField('aiColorTemperature',e=1, v=temperaturaColor)
	except:
		print "HUBO PROBLEMAS AL AJUSTAR LA TEMPERATURA COLOR"
	refreshui()

def masFrio (*args):
	luces = cmds.textScrollList ('listaLuces1',q=1,si=1)
	temperaturaMas= cmds.floatField('aiColorTemperature',q=1, v=1  ) +100
	cmds.floatField('aiColorTemperature',e=1, v = temperaturaMas  )
	try:
		for l in luces:
			cmds.setAttr (l+"SH.aiUseColorTemperature",1)
			cmds.setAttr (l+'SH.aiColorTemperature',temperaturaMas)
	except:
		print "HUBO PROBLEMAS AL AJUSTAR LA TEMPERATURA COLOR"
	refreshui()

def masCalido (*args):
	luces = cmds.textScrollList ('listaLuces1',q=1,si=1)
	temperaturaMenos= cmds.floatField('aiColorTemperature',q=1, v=1  ) - 100
	cmds.floatField('aiColorTemperature',e=1, v = temperaturaMenos  )
	try:
		for l in luces:
			cmds.setAttr (l+"SH.aiUseColorTemperature",1)
			cmds.setAttr (l+'SH.aiColorTemperature',temperaturaMenos)
	except:
		print "HUBO PROBLEMAS AL AJUSTAR LA TEMPERATURA COLOR"
	refreshui()

def seleccionarTempColor(on=1,*args):
    luces = cmds.textScrollList ('listaLuces1',q=1,si=1)
    lucesConTempColor=[]
    if luces!=None:
    	for l in luces:
    	    lShape = cmds.listRelatives ( l , shapes=1)[0]
    	    if cmds.getAttr (lShape+".aiUseColorTemperature")==on:
    	        lucesConTempColor.append (l)
    	if lucesConTempColor:
    		cmds.textScrollList ('listaLuces1', e=1,da=1)
    		cmds.textScrollList ('listaLuces2', e=1,da=1)
    		cmds.textScrollList ('listaLuces3', e=1,da=1)
    		cmds.textScrollList ('listaLuces1', e=1,si=lucesConTempColor)
    		indexLista1 = cmds.textScrollList ('listaLuces1', q=1,sii=1)
    		cmds.textScrollList ('listaLuces2', e=1,sii=indexLista1)
    		cmds.textScrollList ('listaLuces3', e=1,sii=indexLista1)
    	else:
    	    cmds.warning (" - - - NO EXISTEN CAMARAS CON TC ACTIVADO - - -")


def usarTcACtual(*args):
	luces = cmds.textScrollList ('listaLuces1',q=1,si=1)
	if luces != None:
		for l in luces:
			cmds.setAttr (l+"SH.aiUseColorTemperature",1)
	refreshui()

def crearPopTempColor (parent_,*args):
	popTempColor = cmds.popupMenu(p=parent_)
	cmds.menuItem(l="1K"  , p=popTempColor , c=partial (setTemperaturaColor, 1000) )
	cmds.menuItem(l="3K"  , p=popTempColor , c=partial (setTemperaturaColor, 3000) )
	cmds.menuItem(l="5K5 - NEUTRO " , p=popTempColor , c=partial (setTemperaturaColor, 5500) )
	cmds.menuItem(l="10K" , p=popTempColor , c=partial (setTemperaturaColor, 10000) )
	cmds.menuItem(l="15K" , p=popTempColor , c=partial (setTemperaturaColor, 15000) )
	cmds.menuItem (divider=1, p=popTempColor )
	cmds.menuItem(l="ACTIVAR EL USO DE TC" , p=popTempColor , c=usarTcACtual )

def refreshOverride (*args):
    global deactivateSSS
    global deactivateDisplacement
    global deactivateSUB
    verde= [0.3,1,0.3]
    rojo = [1,0.3,0.3]
    if cmds.getAttr ('defaultArnoldRenderOptions.ignoreSss') == 0:
        cmds.iconTextButton  ('b_sss' , e=1  ,bgc= verde)
        deactivateSSS = False
    else:
        cmds.iconTextButton  ('b_sss' , e=1 , bgc= rojo)
        deactivateSSS = True
    if cmds.getAttr ('defaultArnoldRenderOptions.ignoreDisplacement') == 0:
        cmds.iconTextButton  ('b_disp' , e=1 , bgc=verde)
        deactivateDisplacement = False
    else:
        cmds.iconTextButton  ('b_disp' , e=1 , bgc=rojo)
        deactivateDisplacement = True
    if cmds.getAttr ('defaultArnoldRenderOptions.ignoreSubdivision') == 0:
        cmds.iconTextButton  ('b_sub' , e=1 , bgc=verde)
        deactivateSUB = False
    else:
        cmds.iconTextButton  ('b_sub' , e=1 , bgc=rojo)
        deactivateSUB = True
    if cmds.ls (type='aiSkyDomeLight'):
        domos = cmds.ls (type='aiSkyDomeLight')
        v = qVisibilidadAbsoluta ( cmds.listRelatives(domos[0],p=1)[0]) # estado de la visibilidad
        dif = 0 # hay diferentes valores
        for d in domos[1:]:
            if qVisibilidadAbsoluta ( cmds.listRelatives(d,p=1)[0]) != v:
                dif = 1 # hay diferentes valores
        if not dif :
            if v:
                cmds.iconTextButton  ('b_domoOnOff' , e=1 , bgc=verde )
            else:
                cmds.iconTextButton  ('b_domoOnOff' , e=1 , bgc= [0.27,0.27,0.27] )
        else:
        	cmds.iconTextButton  ('b_domoOnOff' , e=1 , bgc=[0.4,0.4,0.4])
    if cmds.renderThumbnailUpdate ( q=1 ):
        cmds.iconTextButton  ('b_rendersOnOff' , e=1 , bgc=verde)
    else:
        cmds.iconTextButton  ('b_rendersOnOff' , e=1 , bgc=rojo)

def expandAt(*args):
    cmds.frameLayout ('frame_1', e=1 , height= cmds.frameLayout('frame_1', q=1 , height= 1)+105 )
    cmds.dockControl('dockLucesUI', e=1 , h=100)

def colapseAt(*args):
    cmds.frameLayout ('frame_1', e=1 , height= cmds.frameLayout('frame_1', q=1 , height= 1)-105 )
    cmds.dockControl('dockLucesUI', e=1 , h=100)


def expandExtras(*args):
    cmds.frameLayout ('frame_2', e=1 , height= cmds.frameLayout('frame_2', q=1 , height= 1)+55 )
    cmds.dockControl('dockLucesUI', e=1 , h=100)

def colapseExtras(*args):
    cmds.frameLayout ('frame_2', e=1 , height= cmds.frameLayout('frame_2', q=1 , height= 1)-55 )
    cmds.dockControl('dockLucesUI', e=1 , h=100)


def rendersSwitch(*args):
    verde= [0.3,1,0.3]
    rojo = [1,0.3,0.3]
    cmds.renderThumbnailUpdate ( not (cmds.renderThumbnailUpdate ( q=1 )) )
    if cmds.renderThumbnailUpdate ( q=1 ):
        cmds.iconTextButton  ('b_rendersOnOff' , e=1 , bgc=verde)
    else:
        cmds.iconTextButton  ('b_rendersOnOff' , e=1 , bgc=rojo)

def refrescar(*args):
    seleccionInicial= cmds.textScrollList ('listaLuces1',q=1,si=1)
    seleccionEnLaEscena = cmds.ls(sl=1)
    cmds.textScrollList ('listaLuces1',e=1,da=1)
    for s in seleccionEnLaEscena:
        try:
            esLuz = "Light" in cmds.nodeType ( cmds.listRelatives (s,s=1)[0]   )
            if esLuz:
                cmds.textScrollList ('listaLuces1',e=1,si=s)
        except:
            pass
    if not cmds.textScrollList('listaLuces1',q=1,ai=1):
        cmds.textScrollList ('listaLuces1',e=1,si=seleccionInicial)
    ordenarLuz()
    refreshui()
    refreshDomo()

def domoOnOff(*args):
    domos = cmds.ls ( type='aiSkyDomeLight' )
    if domos:
        domo = cmds.optionMenu ('domoDrop',q=1,v=1)
        domoTRF = cmds.listRelatives ( domo , p=1 )[0]
        if not qVisibilidadAbsoluta ( domoTRF ):
            cmds.hide ( domos )
            cmds.showHidden ( domo , above=1 )
            cmds.iconTextButton  ('b_domoOnOff', e=1 , bgc=(0,1,0))

        else:
            cmds.showHidden ( domo , above=1 )
            cmds.hide ( domoTRF )
            cmds.iconTextButton  ('b_domoOnOff', e=1 , bgc=(1,0,0))
        cmds.optionMenu('domoDrop',e=1,bgc=[0.27,0.27,0.27])

def domoV(item,*args):
    try:
        domos = cmds.ls ( type='aiSkyDomeLight' )
        cmds.showHidden ( domos , above=1 )
        for d in domos:
            dTRF= cmds.listRelatives ( d , p=1 )[0]
            cmds.hide (dTRF)
        cmds.showHidden ( item , above=1 )
        cmds.optionMenu('domoDrop',e=1,bgc=[0.27,0.27,0.27])
    except:
        pass
    refreshDomo()

def domosActivosInactivos(*args):
    domos = cmds.ls ( type='aiSkyDomeLight' )
    domosActivos=[]
    domosInactivos=[]
    if domos:
        for d in domos:
            domoTRF = cmds.listRelatives ( d , p=1 )[0]
            if qVisibilidadAbsoluta ( domoTRF ):
                domosActivos.append ( domoTRF )
            else:
                domosInactivos.append ( domoTRF )
        return [domosActivos,domosInactivos]

def refreshDomo(*args):
    domos_ActivosInactivos = domosActivosInactivos()
    domos = cmds.ls ( type='aiSkyDomeLight', long=1 )
    if domos_ActivosInactivos:
        if len(domos_ActivosInactivos[0])==1  :
            print "1"
            cmds.optionMenu('domoDrop',e=1,bgc=[0.27,0.27,0.27])
            clearOptionMenu ('domoDrop')
            for d in domos:
                cmds.menuItem ( parent = 'domoDrop' , label = d )
            for d in domos:
                dTRF = cmds.listRelatives(d,p=1)[0]
                if qVisibilidadAbsoluta ( dTRF ):
                    cmds.evalDeferred ("cmds.iconTextButton  ('b_domoOnOff', e=1 , bgc=(0,1,0))")
                    cmds.optionMenu ( 'domoDrop' , e=1 , value = d)
        elif ( len(domos_ActivosInactivos[0])==0 and len( domos_ActivosInactivos[1])==1 ):
            cmds.optionMenu('domoDrop',e=1,bgc=[0.27,0.27,0.27])
            clearOptionMenu ('domoDrop')
            for d in domos:
                cmds.menuItem ( parent = 'domoDrop' , label = d )
            for d in domos:
                dTRF = cmds.listRelatives(d,p=1)[0]
                if qVisibilidadAbsoluta ( dTRF ):
                    cmds.evalDeferred ("cmds.iconTextButton  ('b_domoOnOff', e=1 , bgc=(0,1,0))")
                else:
                    cmds.evalDeferred ("cmds.iconTextButton  ('b_domoOnOff', e=1 , bgc=(1,0,0))")
                    cmds.optionMenu ( 'domoDrop' , e=1 , value = d)
        else:
            cmds.optionMenu('domoDrop',e=1,bgc=[1,0,0])
            cmds.iconTextButton  ('b_domoOnOff', e=1 , bgc=(0.24,0.24,0.24))
            clearOptionMenu ('domoDrop')
            for d in domos:
                cmds.menuItem ( parent = 'domoDrop' , label = d )

def qVisibilidadAbsoluta(luz,*args):
    shape = cmds.listRelatives (luz,s=1)[0]
    if cmds.objExists(shape):
        visibilidadAbsoluta =1
        luzFullPath = cmds.ls (shape,long=1)[0]
        luzFullPathSPLIT = luzFullPath.split("|")[1:]
        for p in luzFullPathSPLIT:
            if visibilidadAbsoluta:
                visibilidad=cmds.getAttr(p+".visibility")
                if not visibilidad:
                    visibilidadAbsoluta=0
    else:
        visibilidadAbsoluta = -1
    return visibilidadAbsoluta

def tc2RGB(*args):
    dic_color2 = {
    1000: [1.0, 0.12941177189350128, 0.0],
    1100: [1.0, 0.15294118225574493, 0.0],
    1200: [1.0, 0.18039216101169586, 0.003921568859368563],
    1300: [1.0, 0.2078431397676468, 0.007843137718737125],
    1400: [1.0, 0.23529411852359772, 0.0117647061124444],
    1500: [1.0, 0.25882354378700256, 0.01568627543747425],
    1600: [1.0, 0.2862745225429535, 0.0235294122248888],
    1700: [1.0, 0.3137255012989044, 0.0313725508749485],
    1800: [1.0, 0.33725491166114807, 0.04313725605607033],
    1900: [1.0, 0.364705890417099, 0.054901961237192154],
    2000: [1.0, 0.38823530077934265, 0.06666667014360428],
    2100: [1.0, 0.4117647111415863, 0.08235294371843338],
    2200: [1.0, 0.43921568989753723, 0.09803921729326248],
    2300: [1.0, 0.4627451002597809, 0.11372549086809158],
    2400: [1.0, 0.48627451062202454, 0.13333334028720856],
    2500: [1.0, 0.5098039507865906, 0.15294118225574493],
    2600: [1.0, 0.529411792755127, 0.1725490242242813],
    2700: [1.0, 0.5529412031173706, 0.1921568661928177],
    2800: [1.0, 0.5764706134796143, 0.21568627655506134],
    2900: [1.0, 0.5960784554481506, 0.239215686917305],
    3000: [1.0, 0.6196078658103943, 0.26274511218070984],
    3100: [1.0, 0.6392157077789307, 0.29019609093666077],
    3200: [1.0, 0.6627451181411743, 0.3137255012989044],
    3300: [1.0, 0.6823529601097107, 0.34117648005485535],
    3400: [1.0, 0.7019608020782471, 0.3686274588108063],
    3500: [1.0, 0.7215686440467834, 0.3960784375667572],
    3600: [1.0, 0.7411764860153198, 0.42352941632270813],
    3700: [1.0, 0.7607843279838562, 0.45490196347236633],
    3800: [1.0, 0.7764706015586853, 0.48235294222831726],
    3900: [1.0, 0.7960784435272217, 0.5137255191802979],
    4000: [1.0, 0.8156862854957581, 0.5411764979362488],
    4100: [1.0, 0.8313725590705872, 0.572549045085907],
    4200: [1.0, 0.8509804010391235, 0.6000000238418579],
    4300: [1.0, 0.8666666746139526, 0.6313725709915161],
    4400: [1.0, 0.8823529481887817, 0.6627451181411743],
    4500: [1.0, 0.9019607901573181, 0.6941176652908325],
    4600: [1.0, 0.9176470637321472, 0.7215686440467834],
    4700: [1.0, 0.9333333373069763, 0.7529411911964417],
    4800: [1.0, 0.9490196108818054, 0.7843137383460999],
    4900: [1.0, 0.9647058844566345, 0.8156862854957581],
    5000: [1.0, 0.9803921580314636, 0.8470588326454163],
    5100: [1.0, 0.9960784316062927, 0.8745098114013672],
    5200: [0.9960784316062927, 1.0, 0.8980392217636108],
    5300: [0.9803921580314636, 1.0, 0.9176470637321472],
    5400: [0.9686274528503418, 1.0, 0.9333333373069763],
    5500: [0.9529411792755127, 1.0, 0.9490196108818054],
    5600: [0.9411764740943909, 1.0, 0.9647058844566345],
    5700: [0.929411768913269, 1.0, 0.9803921580314636],
    5800: [0.9176470637321472, 1.0, 0.9960784316062927],
    5900: [0.9019607901573181, 0.9921568632125854, 1.0],
    6000: [0.8784313797950745, 0.9764705896377563, 1.0],
    6100: [0.8549019694328308, 0.9647058844566345, 1.0],
    6200: [0.8352941274642944, 0.9529411792755127, 1.0],
    6300: [0.8156862854957581, 0.9411764740943909, 1.0],
    6400: [0.7960784435272217, 0.929411768913269, 1.0],
    6500: [0.7803921699523926, 0.9176470637321472, 1.0],
    6600: [0.7647058963775635, 0.9058823585510254, 1.0],
    6700: [0.7490196228027344, 0.8941176533699036, 1.0],
    6800: [0.7333333492279053, 0.886274516582489, 1.0],
    6900: [0.7176470756530762, 0.8784313797950745, 1.0],
    7000: [0.7058823704719543, 0.8666666746139526, 1.0],
    7100: [0.6901960968971252, 0.8588235378265381, 1.0],
    7200: [0.6784313917160034, 0.8509804010391235, 1.0],
    7300: [0.6666666865348816, 0.843137264251709, 1.0],
    7400: [0.6549019813537598, 0.8352941274642944, 1.0],
    7500: [0.6470588445663452, 0.8274509906768799, 1.0],
    7600: [0.6352941393852234, 0.8196078538894653, 1.0],
    7700: [0.6235294342041016, 0.8156862854957581, 1.0],
    7800: [0.615686297416687, 0.8078431487083435, 1.0],
    7900: [0.6078431606292725, 0.800000011920929, 1.0],
    8000: [0.5960784554481506, 0.7960784435272217, 1.0],
    8100: [0.5882353186607361, 0.7882353067398071, 1.0],
    8200: [0.5803921818733215, 0.7843137383460999, 1.0],
    8300: [0.572549045085907, 0.7764706015586853, 1.0],
    8400: [0.5647059082984924, 0.772549033164978, 1.0],
    8500: [0.5607843399047852, 0.7686274647712708, 1.0],
    8600: [0.5529412031173706, 0.7607843279838562, 1.0],
    8700: [0.545098066329956, 0.7568627595901489, 1.0],
    8800: [0.5372549295425415, 0.7529411911964417, 1.0],
    8900: [0.5333333611488342, 0.7490196228027344, 1.0],
    9000: [0.5254902243614197, 0.7450980544090271, 1.0],
    9100: [0.5215686559677124, 0.7411764860153198, 1.0],
    9200: [0.5137255191802979, 0.7333333492279053, 1.0],
    9300: [0.5098039507865906, 0.729411780834198, 1.0],
    9400: [0.5058823823928833, 0.7254902124404907, 1.0],
    9500: [0.49803921580314636, 0.7254902124404907, 1.0],
    9600: [0.4941176474094391, 0.7215686440467834, 1.0],
    9700: [0.4901960790157318, 0.7176470756530762, 1.0],
    9800: [0.48627451062202454, 0.7137255072593689, 1.0],
    9900: [0.48235294222831726, 0.7098039388656616, 1.0],
    10000:[0.4745098054409027, 0.7058823704719543, 1.0],
    10100:[0.47058823704719543, 0.7019608020782471, 1.0],
    10200:[0.46666666865348816, 0.6980392336845398, 1.0],
    10300:[0.4627451002597809, 0.6980392336845398, 1.0],
    10400:[0.4588235318660736, 0.6941176652908325, 1.0 ],
    10500:[0.45490196347236633, 0.6901960968971252, 1.0],
    10600:[0.45098039507865906, 0.686274528503418, 1.0],
    10700:[0.4470588266849518, 0.686274528503418, 1.0],
    10800:[0.4470588266849518, 0.6823529601097107, 1.0],
    10900:[0.4431372582912445, 0.6784313917160034, 1.0],
    11000:[0.43921568989753723, 0.6784313917160034, 1.0],
    11100:[0.43529412150382996, 0.6745098233222961, 1.0],
    11200:[0.4313725531101227, 0.6705882549285889, 1.0],
    11300:[0.4313725531101227, 0.6705882549285889, 1.0],
    11400:[0.4274509847164154, 0.6666666865348816, 1.0],
    11500:[0.42352941632270813, 0.6666666865348816, 1.0],
    11600:[0.41960784792900085, 0.6627451181411743, 1.0],
    11700:[0.41960784792900085, 0.6627451181411743, 1.0],
    11800:[0.4156862795352936, 0.658823549747467, 1.0],
    11900:[0.4117647111415863, 0.658823549747467, 1.0],
    12000:[0.4117647111415863, 0.6549019813537598, 1.0],
    12100:[0.40784314274787903, 0.6549019813537598, 1.0],
    12200:[0.40392157435417175, 0.6509804129600525, 1.0],
    12300:[0.40392157435417175, 0.6509804129600525, 1.0],
    12400:[0.4000000059604645, 0.6470588445663452, 1.0],
    12500:[0.4000000059604645, 0.6470588445663452, 1.0],
    12600:[0.3960784375667572, 0.6431372761726379, 1.0],
    12700:[0.3921568691730499, 0.6431372761726379, 1.0],
    12800:[0.3921568691730499, 0.6392157077789307, 1.0],
    12900:[0.38823530077934265, 0.6392157077789307, 1.0],
    13000:[0.38823530077934265, 0.6352941393852234, 1.0],
    13100:[0.3843137323856354, 0.6352941393852234, 1.0],
    13200:[0.3843137323856354, 0.6352941393852234, 1.0],
    13300:[0.3803921639919281, 0.6313725709915161, 1.0],
    13400:[0.3803921639919281, 0.6313725709915161, 1.0],
    13500:[0.3764705955982208, 0.6274510025978088, 1.0],
    13600:[0.3764705955982208, 0.6274510025978088, 1.0],
    13700:[0.3764705955982208, 0.6274510025978088, 1.0],
    13800:[0.37254902720451355, 0.6235294342041016, 1.0],
    13900:[0.37254902720451355, 0.6235294342041016, 1.0],
    14000:[0.3686274588108063, 0.6235294342041016, 1.0],
    14100:[0.3686274588108063, 0.6196078658103943, 1.0],
    14200:[0.364705890417099, 0.6196078658103943, 1.0],
    14300:[0.364705890417099, 0.6196078658103943, 1.0],
    14400:[0.364705890417099, 0.615686297416687, 1.0],
    14500:[0.3607843220233917, 0.615686297416687, 1.0],
    14600:[0.3607843220233917, 0.615686297416687, 1.0],
    14700:[0.3607843220233917, 0.6117647290229797, 1.0],
    14800:[0.35686275362968445, 0.6117647290229797, 1.0],
    14900:[0.35686275362968445, 0.6117647290229797, 1.0],
    15000:[0.35686275362968445, 0.6117647290229797, 1.0]
    }
    luces =  cmds.textScrollList ('listaLuces1',q=1,si=1)
    for luz in luces:
        luzShape = cmds.listRelatives ( luz , shapes=1 ) [0]
        k = cmds.getAttr ( luzShape + '.aiColorTemperature' )
        k = int ( k / 100 ) *100
        rgbLuz = dic_color2[k]
        cmds.setAttr ( luzShape + ".color" , rgbLuz[0] ,rgbLuz[1],rgbLuz[2] ,type='double3' )
        cmds.setAttr ( luzShape + ".aiUseColorTemperature" , 0 )

def qVisibilidadAbsoluta(luz,*args):
    shape = cmds.listRelatives (luz,s=1)[0]
    if cmds.objExists(shape):
        visibilidadAbsoluta =1
        luzFullPath = cmds.ls (shape,long=1)[0]
        luzFullPathSPLIT = luzFullPath.split("|")[1:]
        for p in luzFullPathSPLIT:
            if visibilidadAbsoluta:
                visibilidad=cmds.getAttr(p+".visibility")
                if not visibilidad:
                    visibilidadAbsoluta=0
    else:
        visibilidadAbsoluta = -1
    return visibilidadAbsoluta

def isolateLuz(*args):
    luces = cmds.ls(['*_LPNTSH','*_LDIRSH','*_LARESH','*_LAMBSH','*_LSPTSH','*_DOMESH'],r=1)
    lucesAisladas = cmds.textScrollList ( 'listaLuces1',q=1,si=1)
    dicEstadoLuces={}
    lucesTRF=[]
    if 'isolate' not in globals():
        global isolate
        isolate  = False
    if isolate == False:
        isolate = True
        for luz in luces:
            luzTRF = cmds.listRelatives ( luz , p=1 )[0]
            dicEstadoLuces[luzTRF] = qVisibilidadAbsoluta ( luzTRF )
            cmds.hide ( luzTRF )
        saveJSONFile ( dicEstadoLuces , "PH_LUCES_isolateHelper.json" )
        cmds.showHidden ( lucesAisladas , a=1 , b=1 )
    else:
        isolate = False
        dicEstadoLoad = loadJSONFile ("PH_LUCES_isolateHelper.json" )
        for luz in luces:
            luzTRF = cmds.listRelatives ( luz , p=1 )[0]
            if dicEstadoLoad [ luzTRF ]:
                cmds.showHidden ( luz , a=1  )
            else:
                cmds.hide ( luz )
    if 'isolate' not in globals():
            cmds.iconTextButton  ('b_isolate' , e = 1 ,  image1 = 'M:\PH_SCRIPTS\ICONS\PH_LUCES_ISOLATE_OFF.png' )
    else:
        if isolate == True:
            cmds.iconTextButton  ('b_isolate' , e = 1 ,  image1 = 'M:\PH_SCRIPTS\ICONS\PH_LUCES_ISOLATE.png' )
        else:
            cmds.iconTextButton  ('b_isolate' , e = 1 ,  image1 = 'M:\PH_SCRIPTS\ICONS\PH_LUCES_ISOLATE_OFF.png' )
    refreshui()

def saveJSONFile(dataBlock, filePath):
	outputFile = open(filePath, 'w')
	JSONData = json.dumps(dataBlock, sort_keys=True, indent=4)
	outputFile.write(JSONData)
	outputFile.close()
def loadJSONFile(filePath):
	inputFile = open(filePath, 'r')
	JSONData = json.load(inputFile)
	inputFile.close()
	return JSONData

def lightListPanel():
    global version
    try:
        global dicLuces,orden,grupoVG,aiColorTemperatureSlider,grupoCParent,grupo_borrar,grupo_renombrar,buscarPor_Grupo_Luz,myLights,myLightsOnShapes,myLightsOn
        global isolate,vecesEjecutado,abs,rel,win,dockLuces
        global dock,placeHolder
        lightList = cmds.ls(['*_LPNTSH','*_LDIRSH','*_LARESH','*_LAMBSH','*_LSPTSH','*_DOMESH'],r=1)
        arnoldLightList = []
        dicLuces={}
        for i in range (5):
            winsound.Beep (2000+i*100,30)
        for i in range (5):
            winsound.Beep (3000+i*250,30)
        if cmds.window('winMLuces',exists=True):
            cmds.deleteUI('winMLuces')
        if cmds.dockControl('dockLucesUI',ex=1)==True:
            cmds.deleteUI('dockLucesUI')
        win = cmds.window('winMLuces', title="PH_LUCES! v1.7 - COMPATIBLE CON ARNOLD -", menuBar=0 , w=100 , s=1, height= 100)
        col_0 = cmds.columnLayout('col_0', p=win)
        cmds.separator(h=5,w=10,hr=0,p=col_0,st="none")
        row_0 = cmds.rowLayout ('row_0',numberOfColumns = 16 , height= 30, p=col_0 )
        cmds.separator(w=3,p=row_0,st="none")
        b_sel = cmds.iconTextButton ('b_sel',ann='(.)SELECCIONAR - (..)DESELECCIONAR',style='iconOnly',image1='selectObject.png', c = seleccionarLuces , dcc= deseleccionar, width=25,height=25,p=row_0, bgc=(0.4,0.4,0.4),font= "fixedWidthFont")
        cmds.separator(w=20,p=row_0,st="none")
        b_filtroSpot = cmds.iconTextButton  ('b_filtroLSPT',ann='SPOT',style='iconOnly',image1='M:\PH_SCRIPTS\ICONS\LSPT_1.png', c = partial(filtrado,"LSPT") ,width=25,height=25,p=row_0, dcc=partial(add_light,"spot") ,bgc=(0.2,0.2,0.2),font= "fixedWidthFont")
        b_filtroPoint = cmds.iconTextButton ('b_filtroLPNT',ann='POINT',style='iconOnly',image1='M:\PH_SCRIPTS\ICONS\LPNT_1.png', c = partial(filtrado,"LPNT") , width=25,height=25,p=row_0, dcc=partial(add_light,"point") ,bgc=(0.2,0.2,0.2),font= "fixedWidthFont")
        b_filtroArea = cmds.iconTextButton  ('b_filtroLARE',ann='AREA',style='iconOnly',image1='M:\PH_SCRIPTS\ICONS\LARE_1.png', c = partial(filtrado,"LARE") ,width=25,height=25,p=row_0, dcc=partial(add_light,"area") ,bgc=(0.2,0.2,0.2),font= "fixedWidthFont")
        b_filtroDir = cmds.iconTextButton   ('b_filtroLDIR',ann='DIRECTIONAL',style='iconOnly',image1='M:\PH_SCRIPTS\ICONS\LDIR_1.png', c = partial(filtrado,"LDIR") ,width=25,height=25,p=row_0, dcc=partial(add_light,"dir") ,bgc=(0.2,0.2,0.2),font= "fixedWidthFont")
        b_all = cmds.iconTextButton         ('b_filtrotodos',ann='TOGGLE FILTROS TODOS',style='iconOnly', image1='M:\PH_SCRIPTS\ICONS\TODAS_1.png',width=25,height=25,p=row_0,c=tglTodos )
        cmds.separator ( hr=0 , w=10 , p = row_0 )
        grupo_crear = cmds.iconTextButton   (style='iconOnly', image1 = 'M:\PH_SCRIPTS\ICONS\PH_LUCES_CARPETA.png' ,width=25,height=25, c=crearGrupo , ann="CREA UN GRUPO DE LUZ CON EL NOMBRE ESPECIFICADO",  p = row_0 )
        grupo_renombrar = cmds.iconTextButton   (style='iconOnly', image1 = 'M:\PH_SCRIPTS\ICONS\PH_LUCES_CARPETA_RENOMBRAR.png',width=25,height=25, c=renombrarGrupo , ann="RENOMBRA EL GRUPO ELEGIDO EN EL DROP.\nDESELECCIONA LAS LUCES DE LA LISTA PARA HABILITAR ESTA OPCION.",  p = row_0 )
        grupo_borrar = cmds.iconTextButton   (style='iconOnly', image1 = 'M:\PH_SCRIPTS\ICONS\PH_LUCES_CARPETA_BORRAR.png' ,width=25,height=25, c=borrarGrupo , ann="BORRA EL GRUPO ELEGIDO EN EL DROP.\nDESELECCIONA LAS LUCES DE LA LISTA PARA HABILITAR ESTA OPCION.",  p = row_0 )
        grupoVG = cmds.optionMenu ( 'grupoVG',    bgc = [0.1,0.1,0.1] , w=70 , changeCommand = cambiarGrupo , p = row_0)
        grupoCParent = cmds.optionMenu ( en=0,ann="DESELECCIONA LAS LUCES DE LA LISTA PARA HABILITAR ESTA OPCION.",bgc = [0.27,0.27,0.27] , w=70 , changeCommand = cambiarGrupoParent , p = row_0)
        buscador = cmds.textField ( 'buscador' , w=100,p = row_0  )
        pop = cmds.popupMenu(p='buscador')#|textScrollList
        cmds.menuItem(l="BUSCAR POR LUZ"   , c = setBusquedaPorLuz   , p=pop)
        cmds.menuItem(l="BUSCAR POR GRUPO" , c = setBusquedaPorGrupo ,p=pop)
        col = cmds.columnLayout(p=win,h=30)
        row1 = cmds.rowLayout ( 'row1' , parent = col, numberOfColumns = 2 , columnWidth = [(1,200),(2,100)], height = 30  )
        cmds.separator ( p = col )
        scroll = cmds.scrollLayout( 'scroll',parent = win , childResizable = 1, width = 520 , h=420)
        columnScroll = cmds.rowLayout( 'columnScroll', rowAttach = [2, "top", 0]  , numberOfColumns = 4 ,p=scroll, nbg = 1)
        construirScrollsConBotones ( emparentarA=scroll )
        frame_1 = cmds.frameLayout('frame_1' , h=120, expandCommand= expandAt , collapseCommand = colapseAt , label='ATRIBUTOS', borderStyle='in',collapsable=1,p=win , w=520 )
        rootDeLaEscena = ""
        roots = cmds.ls('ROOT_*_LGRP',r=1)
        listaDeRootsNoReferenciados=[]
        for root in roots:
            if cmds.referenceQuery( root ,isNodeReferenced=1 ) == False:
                listaDeRootsNoReferenciados.append (root)
        if len(listaDeRootsNoReferenciados)==1:
            rootDeLaEscena = listaDeRootsNoReferenciados[0]
        clearOptionMenu (grupoVG)
        gruposDeLuces = cmds.ls ( '*_LGRP' , type='transform' )
        for grp in gruposDeLuces:
            if grp !=rootDeLaEscena and cmds.referenceQuery( grp ,isNodeReferenced=1 ) == False :
                cmds.menuItem(parent=grupoVG , label=grp[:-5] )
        clearOptionMenu (grupoCParent)
        for grp in gruposDeLuces:
            if grp != rootDeLaEscena and cmds.referenceQuery( grp ,isNodeReferenced=1 ) == False:
                cmds.menuItem(parent=grupoCParent , label=grp[:-5] )
        row_3 = cmds.rowLayout ( p=frame_1 , numberOfColumns=21 , h=10 )
        cmds.separator(p=row_3 ,w=11 , st= "none")
        cmds.text(label='On' , p = row_3 , ann="ON / OFF")
        cmds.text(label='         Int     ' , p = row_3 , ann="INTENSITY")
        cmds.text(label='   Exp ' , p = row_3 , ann="EXPOSURE")
        cmds.text(label='       Rad   ' , p = row_3 , ann="aiRADIUS")
        cmds.text(label='    Ang  ' , p = row_3 , ann="aiANGLE")
        cmds.text(label='   ConeA' , p = row_3 , ann="CONE ANGLE")
        cmds.separator(w=6,st= "none", p=row_3 )
        cmds.text(label='PenuA' , p = row_3 , ann="PENUMBRA ANGLE")
        cmds.separator(w=4,st= "none", p=row_3 )
        cmds.text(label='Dropoff' , p = row_3 , ann="DROPOFF")
        cmds.separator(w=5,st= "none", p=row_3 )
        cmds.text('col',label=' Col   ' , p=row_3 , ann="COLOR")
        cmds.text(label='iDef ' , p=row_3 , ann="ILLUMINATES BY DEFAULT")
        cmds.text(label='eD ' , p=row_3, ann="EMIT DIFFUSE")
        cmds.text(label=' eS' , p=row_3 , ann="EMIT SPECULAR" )
        cmds.separator(w=5,st= "none", p=row_3 )
        cmds.text(label='Samp  ' , p = row_3, ann="aiSAMPLES")
        cmds.text(label=' ShDens  ' , p = row_3, ann="SHADOW DENSITY")
        row_2 = cmds.rowLayout ( 'rowCambiaColor',p=frame_1  , numberOfColumns=25 , h=30 ,bgc=[0.5,0.5,0.5])
        cmds.separator(p=row_2 ,w=10, st= "none")
        cmds.checkBox ('on_off' ,en=0, l='' , w=13 ,h=20 , changeCommand = onoff  , p=row_2  )
        cmds.separator(p=row_2 ,w=5, st= "none")
        cmds.floatField( 'intensity' ,  en = 0 , precision = 3,  w = 50 , changeCommand = setInt  ,  p = row_2 )
        crearDropCopiarPegar ('intensity')
        cmds.floatField('aiExposure' , en=0, precision = 3, w=40 , changeCommand = setExp  , p = row_2 )
        crearDropCopiarPegar ('aiExposure')
        cmds.floatField('aiRadius' , en=0,precision = 2,  w=40 , changeCommand = setRad , p = row_2 )
        crearDropCopiarPegar ('aiRadius')
        cmds.floatField('aiAngle' , en=0,precision = 2, w=40 , changeCommand = setAng , p= row_2 )
        crearDropCopiarPegar ('aiAngle')
        cmds.floatField('coneAngle' ,en=0, w=40 ,h=20 ,pre=2, cc = setconeangle  , p=row_2 )
        crearDropCopiarPegar ('coneAngle')
        cmds.floatField('penumbraAngle' ,en=0,w=40 ,h=20 ,pre=2, cc = setpenumbraAngle , p=row_2 )
        crearDropCopiarPegar ('penumbraAngle')
        cmds.floatField('dropoff' ,en=0, w=40 ,h=20 ,pre=2, cc = setdropoff  , p=row_2 )
        crearDropCopiarPegar ('dropoff')
        cmds.separator(w=2,st= "none", p=row_2 )
        colorSwatch = cmds.colorSliderGrp( 'color' , en=0,  cw2 = (23, 0),co2=[5, 0],ct2=["both", "both"], changeCommand = setColor , p=row_2)
        popTempColor = cmds.popupMenu(p=colorSwatch)
        cmds.menuItem( label='MATCHEAR TEMPERATURA COLOR',p= popTempColor,c=tc2RGB)
        cmds.checkBox ('C_ilumDef' ,en=0, l='' , w=13 ,h=20 , changeCommand = setilumDef  , p=row_2  )
        cmds.separator(w=4,st= "none", p=row_2 )
        cmds.checkBox ('emitDiffuse' ,en=0, l='' , w=13 ,h=20 , changeCommand = setDif  , p=row_2 )
        cmds.separator(w=4,st= "none", p=row_2 )
        cmds.checkBox ('emitSpecular' ,en=0, l='' , w=13 ,h=20  , changeCommand = setSpec   , p=row_2 )
        cmds.separator(w=4,st= "none", p=row_2 )
        cmds.floatField('aiSamples' , en=0,precision = 0,  w=32 , changeCommand = setSamp  , p = row_2  )
        cmds.separator(w=4,st= "none", p=row_2 )
        cmds.floatField('aiShadowDensity' , en=0,precision = 2,  w=32 , changeCommand = setShadowDensity  , p = row_2  )
        row_5 = cmds.rowLayout ( 'rowSegundoRowAtts' , p=frame_1  , numberOfColumns=11 , h=1, cal=[1,"center"]  , rat= [1, "top", 0]	 )
        cmds.radioCollection('radioAbsRel')
        rowDeColumnas=cmds.rowLayout (nc=3,co3=[170,0,50],ct3=["left", "left", "both"], p=row_5 ,h=20)
        row_AbsRel = cmds.columnLayout( p = rowDeColumnas)
        cmds.radioCollection('absrelRadio')
        abs = cmds.radioButton( 'A',label='ABSOLUTO',en=0,sl=1,ann="ABSOLUTO",cl='radioAbsRel',onc='cmds.rowLayout("rowCambiaColor",e=1,bgc=[0.5,0.5,0.5]) ')
        row_ventanaCrearLuz = cmds.columnLayout( p = rowDeColumnas )
        cmds.radioCollection()
        rel = cmds.radioButton('R', label='RELATIVO',en=0, ann="RELATIVO",cl='radioAbsRel', onc='cmds.rowLayout("rowCambiaColor",e=1,bgc=[0.18,0.65,0.72]) ')
        row_filtros = cmds.rowLayout( p = rowDeColumnas ,nc=21)
        cmds.text(label='               CT ' , ann="COLOR TEMPERATURE", p=row_filtros)
        cmds.iconTextButton  ('b_masCalido', en=0,ann='-100',style='iconOnly',image1='arrowDown', c = masCalido ,width=15,height=15,p=row_filtros,bgc=(1,0.2,0.2))
        crearPopTempColor ('b_masCalido')
        tempColor = cmds.floatField('aiColorTemperature' ,w=40 ,  bgc=(1,0.2,0.2) , en=0 , pre=0 ,h=15 ,cc = setTempColor, p=row_filtros )
        popTempColor = cmds.popupMenu(p=tempColor)
        cmds.menuItem(l="SELECCIONAR POR TEMPERATURA COLOR ON" , p=popTempColor , c=partial(seleccionarTempColor,1) )
        cmds.menuItem(l="SELECCIONAR POR TEMPERATURA COLOR OFF" , p=popTempColor , c=partial(seleccionarTempColor,0)  )
        cmds.iconTextButton  ('b_masFrio', en=0 ,ann='+100',style='iconOnly',image1='arrowUp', c = masFrio ,width=15,height=15,p=row_filtros,bgc=(0.2,0.2,1))
        crearPopTempColor ('b_masFrio')
        #ESTO ESTA DESHABILITADO HASTA QUE ESTE FUNCIONAL
        #filtrosDropMenu = cmds.optionMenu('oM_filtros',annotation="FILTROS",bgc = [0.7,0.7,0.7],w=70,en=0,changeCommand=asignarFiltro,p=row_filtros)
        #clearOptionMenu (filtrosDropMenu)
        #filtros = cmds.ls ( type='aiLightDecay' )
        #for filtro in filtros:
        #	cmds.menuItem(parent=(filtrosDropMenu +'|OptionMenu'), label=filtro)
        cmds.textScrollList ('listaLuces1' , e=1  ,da=1)
        cmds.textScrollList ('listaLuces2' , e=1  ,da=1)
        cmds.textScrollList ('listaLuces3' , e=1  ,da=1)
        cmds.columnLayout ( 'col_frame_2' , h=5 , p=win )
        anchoBotones = 84
        frame_2 = cmds.frameLayout('frame_2', label='EXTRAS ARNOLD SETTINGS', borderStyle='in', expandCommand= expandExtras , collapseCommand = colapseExtras  , collapsable=1,p=win , h=80 , w=520 )
        row_6 = cmds.rowLayout ( p=frame_2 , numberOfColumns=21 , h=30 )
        b_sss = cmds.iconTextButton  ('b_sss',l='SSS',style='textOnly',image1='M:\PH_SCRIPTS\ICONS\PH_LUCES_SSS.png', c = sss ,width=anchoBotones,height=25,p=row_6 ,bgc=(0.2,0.2,0.2))
        b_disp = cmds.iconTextButton  ('b_disp',l='DISPLACEMENT',style='textOnly',image1='M:\PH_SCRIPTS\ICONS\PH_LUCES_DISP.png', c = disp ,width=anchoBotones,height=25,p=row_6 ,bgc=(0.2,0.2,0.2))
        b_sub = cmds.iconTextButton  ('b_sub',l='SUBDIVISION',style='textOnly',image1='M:\PH_SCRIPTS\ICONS\PH_LUCES_DISP.png', c = sub ,width=anchoBotones,height=25,p=row_6 ,bgc=(0.4,0.4,0.4))
        b_flush = cmds.iconTextButton  ('b_flush',l='FLUSH CACHE',style='textOnly',image1='M:\PH_SCRIPTS\ICONS\PH_LUCES_DISP.png', c = "cmds.arnoldFlushCache(flushall=True)\ncmds.warning('FLUSH')" ,width=anchoBotones,height=25,p=row_6 ,bgc=(0.4,0.4,0.4))
        b_rendersOnOff = cmds.iconTextButton  ('b_rendersOnOff',l='THUMBNAILS',style='textOnly', c = rendersSwitch,width=anchoBotones,height=25,p=row_6 ,bgc=(0.4,0.4,0.4))
        b_domoOnOff = cmds.iconTextButton  ('b_domoOnOff',l='DOMO',style='textOnly',image1='M:\PH_SCRIPTS\ICONS\PH_LUCES_DISP.png', c = domoOnOff,width=anchoBotones,height=25,p=row_6 ,bgc=(0.4,0.4,0.4))
        domoDrop = cmds.optionMenu ('domoDrop',bgc = [0.1,0.1,0.1],w=50, changeCommand = domoV ,p=frame_2)
        refreshDomo()
        refreshOverride()
        enableDropParent()
        cmds.window('winMLuces', e=1 , resizeToFitChildren=1 )
        allowedAreas = ['right', 'left']
        placeHolder = cmds.menuItem ( p = grupoVG , l="placeholder")
        dockLuces = cmds.dockControl( 'dockLucesUI' , label= "PH_LUCES! v"+str(version)+" - COMPATIBLE CON ARNOLD -",area='right', content=win, allowedArea=allowedAreas )
        dock = cmds.optionMenu ( grupoVG , q=1 , ill=1 )[0].split("|")[0]
        cmds.deleteUI (dock + placeHolder.split("winMLuces")[1] )
    except:
        winsound.Beep (500,1000)



ultimoOrden="luz" #VARIABLE LOCAL PARA EL SWITCH DEL ORDEN DE LAS LUCES
orden = {"luz":0,"tipo":0,"grupo":0} #DICCIONARIO PARA SABER SI LAS VECES DE TOCAR EL BOTON SON PARES O INPARES
lightListPanel()
