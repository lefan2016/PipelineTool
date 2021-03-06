import maya.cmds as mc
import maya.mel as mel
import sys
import os
global intro
intro = " -- CACO BAKER v1.0.2 -- "
def filtrar(lista=[],tags=[]):
	for obj in lista:
		for tag in tags:
			if tag in obj:
				lista.remove(obj)
	return lista

def eligeCamaras(*args):
	global intro
	mc.warning (intro)

	listaDeCamsShapes= mc.ls (ca=1  )

	listaDeCamsTRF=[]
	for shape in listaDeCamsShapes:
		if not 'top' in shape and not 'side' in shape and not 'persp' in shape and not 'front' in shape:
			listaDeCamsTRF.append( mc.listRelatives (shape,p=1)[0] )
			listaDeCamsTRF=filtrar(listaDeCamsTRF,['SCAM'])

	if len ( listaDeCamsTRF ) != 0:
		if mc.window ('listaCamaras',ex=1):
			mc.deleteUI ('listaCamaras')
		mc.window('listaCamaras', title=  intro + 'CAMARAS DE LA ESCENA')
		lay_cams = mc.columnLayout ( 'column1' , p='listaCamaras',adjustableColumn=1 )
		mc.text(label='''-SELECCIONA LAS CAMARAS QUE DESEAS CAQUEAR''',p=lay_cams)
		listaCams=mc.textScrollList ('listaCamarasCaquear',p=lay_cams , numberOfRows=40 , w=50 , h=400 , allowMultiSelection = True,append=listaDeCamsTRF)
		mc.button ('b_OK' , l='OK' , c=setResolution ,p=lay_cams)
		mc.showWindow ('listaCamaras')
	else:
		mc.warning ("!!!! NO SE HAN ENCONTRADO CAMARAS !!!!")

def setResolution(width=None, height=None, pixelAspect=None):
	global camarasSeleccionadas
	global listaLayer
	global intro

	if mc.textScrollList ('listaCamarasCaquear',q=1,si=1)!=None:
		camarasSeleccionadas = mc.textScrollList ('listaCamarasCaquear',q=1,si=1)
		mc.deleteUI ('listaCamaras')
		try:
			del renderLayers
		except:
			pass

		anchoActual = mc.getAttr("defaultResolution.width")
		height = mc.getAttr("defaultResolution.height")
		rlayers = []
		renderlayersSinRef =[]
		rlayers = mc.ls (type="renderLayer")

		for layer in rlayers:
			print layer, mc.referenceQuery( layer, isNodeReferenced=True )
			if mc.referenceQuery( layer, isNodeReferenced=True )!=1:
				renderlayersSinRef.append(layer)
		rlayers = []
		#renderlayersSinRef.remove("defaultRenderLayer")
		rlayers = renderlayersSinRef

		if mc.window ('listaLayers',ex=1):
			mc.deleteUI ('listaLayers')
		if len (rlayers) > 0:
			print rlayers,len(rlayers)
			confirma = mc.promptDialog(title=intro,
					message= 'ANCHO ACTUAL: ' + str(anchoActual) + '\nINGRESA CUANTOS PIXELS QUERES SUMAR:',
					button=['OK', 'Cancel'],
					defaultButton='OK',
					cancelButton='Cancel',
					dismissString='Cancel')
			if confirma=='OK':
				if str(mc.promptDialog(q=1, text=1)).isdigit():
					mc.window('listaLayers', title=intro + 'RENDER LAYERS')
					lay_lista = mc.columnLayout ( 'column1' , p='listaLayers',adjustableColumn=1 )
					mc.text(label='''-SELECCIONA RENDER LAYERS PARA OVERRIDE\n''')
					listaLayer=mc.textScrollList (p=lay_lista , numberOfRows=40 , h=150 , allowMultiSelection = True,append=rlayers)
					mc.button ('b_OK' , l='OK' , c=OverrideLayers )
					mc.showWindow ('listaLayers')
				else:
					mc.warning ("INGRESO INVALIDO. CANCELADO.")
			else:
				mc.warning ("CANCELADO POR EL USUARIO.")
		else:
			mc.warning('NO SE DETECTARON RENDER LAYERS AMEEEOOOO')
	else:
		mc.warning ("NO SE HAN ELEGIDO CAMARAS.")


def OverrideLayers(*args):
	global camarasSeleccionadas
	global listaLayer
	global layers

	if mc.textScrollList(listaLayer,q=1,si=1)!=None:
		anchoActual = mc.getAttr("defaultResolution.width")
		height = mc.getAttr("defaultResolution.height")
		layers = mc.textScrollList(listaLayer,q=1,si=1)
		pixelsMas = int(mc.promptDialog(q=1, text=1))
		device_aspect = float( ( anchoActual+pixelsMas )* 1.0)/float(height)
		cameraAperture = float( anchoActual+pixelsMas ) * 0.98 / 2048
		wit  = anchoActual+pixelsMas
		cams = camarasSeleccionadas
		cams.sort()

		for layer in layers:
			for cam in cams:
				print layer, cam
				camSH = mc.listRelatives(cam,s=1)[0]
				atts=mc.listAttr(camSH)

				for at in atts:
					try:
						mc.setAttr(camSH+'.'+at,l=0)
					except:
						pass
				mc.editRenderLayerAdjustment ( camSH+'.cameraAperture',remove=True )
				mc.editRenderLayerAdjustment ( camSH+'.horizontalFilmAperture',remove=True )
				mc.editRenderLayerGlobals ( currentRenderLayer=layer )
				mc.editRenderLayerMembers ( layer , camSH )
				mc.editRenderLayerAdjustment ('defaultResolution.lockDeviceAspectRatio', layer=layer)
				mc.editRenderLayerAdjustment ( camSH+".cameraAperture", layer=layer)
				mc.editRenderLayerAdjustment ('defaultResolution.width', layer=layer)
				mc.editRenderLayerAdjustment ('defaultResolution.height', layer=layer)
				mc.editRenderLayerAdjustment ('defaultResolution.deviceAspectRatio', layer=layer)
				mc.setAttr('defaultResolution.lockDeviceAspectRatio', 1)
				mc.setAttr('defaultResolution.width', wit)
				mc.setAttr("defaultResolution.height", height)
				mc.setAttr("defaultResolution.deviceAspectRatio", device_aspect)
				mc.setAttr(camSH+".horizontalFilmAperture", cameraAperture)

				atts=mc.listAttr(camSH)
				for at in atts:
					try:
						mc.setAttr(camSH+'.'+at,l=0)
					except:
						pass
		bakerCams()
	else:
		mc.warning ("NO HAY SELECCION EN LA LISTA DE RENDER LAYERS. RECATATEEE !!")

def bakerCams(*args):
	global intro
	global camarasSeleccionadas
	global carpetaExportacion
	global listaLayer

	camsDuplicadas=[]
	confirmYes=str(mc.confirmDialog( title=intro + 'CAMARAS', message='¿QUIERES QUE TE EXPORTE LAS CAMARAS?', button=['SIPI','NOOOOO'], defaultButton='Yes', cancelButton='No', dismissString='No' ))
	if  confirmYes == 'SIPI':
		mel.eval("FBXExportSmoothingGroups -v false")
		mel.eval("FBXExportHardEdges -v false")
		mel.eval("FBXExportTangents -v false")
		mel.eval("FBXExportSmoothMesh -v false")
		mel.eval("FBXExportInstances -v false")
		mel.eval("FBXExportBakeComplexAnimation -v false")
		mel.eval("FBXExportUseSceneName -v false")
		mel.eval("FBXExportQuaternion -v euler")
		mel.eval("FBXExportShapes -v true")
		mel.eval("FBXExportSkins -v false")
		mel.eval("FBXExportConstraints -v false")
		mel.eval("FBXExportCameras -v true")
		mel.eval("FBXExportLights -v false")
		mel.eval("FBXExportEmbeddedTextures -v false")
		mel.eval("FBXExportInputConnections -v true")
		mel.eval("FBXExportUpAxis y")
		carpetaExportacion = None
		carpetaExportacion = mc.fileDialog2(fileMode=2, caption=intro+"ELEGI CARPETA DE EXPORTACION" , startingDirectory="Q:\MAYA\06_SHOT_RESULT")
		global layers
		cams = camarasSeleccionadas
		for layer in layers:
			for cam in cams:
				print cam
				#camDuplicada = mc.duplicate ( mc.listRelatives(cam,p=1)[0] , name= "EXPORT_"+mc.listRelatives(cam,p=1)[0])[0]
				if '_cam' in cam:
					camSplit=cam.split('_cam')[0]
				elif '_CAM' in cam:
					camSplit=cam.split('_CAM')[0]
				else:
					camSplit=cam

				camDuplicada = mc.duplicate ( cam, name= camSplit + "_CAM_COMPO")[0]
				camsDuplicadas.append (camDuplicada)


			for camDupl in camsDuplicadas:
				try:
					mc.select ( camDupl )
				except :
					print ("ERROR: NO SE PUDO SELECCIONAR LA CAMARA: "+camDupl)
				mel.eval ( ('FBXExport -f "' + str(carpetaExportacion[0]) + '\\' + str(camDupl) + '.fbx" -s;').replace("\\","/")  )

		os.system ('explorer "'+ carpetaExportacion[0]+'"')
		mc.delete(camsDuplicadas)
		print camsDuplicadas
		mc.deleteUI ('listaLayers')
