#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

"""
 @file loadmodel.py
 @brief ModuleDescription
 @date $Date$


"""
import sys
import time
sys.path.append(".")

# Import RTM module
import RTC
import OpenRTM_aist
import Img

import cv2
import keras
from keras.models import load_model
import numpy as np
import pandas as pd
# Import Service implementation class
# <rtc-template block="service_impl">

# </rtc-template>

# Import Service stub modules
# <rtc-template block="consumer_import">
# </rtc-template>


# This module's spesification
# <rtc-template block="module_spec">
loadmodel_spec = ["implementation_id", "loadmodel",
		 "type_name",         "loadmodel",
		 "description",       "ModuleDescription",
		 "version",           "1.0.0",
		 "vendor",            "masato",
		 "category",          "Category",
		 "activity_type",     "STATIC",
		 "max_instance",      "0",
		 "language",          "Python",
		 "lang_type",         "SCRIPT",
		 "conf.default.modelname", "applebanana",

		 "conf.__widget__.modelname", "text",

         "conf.__type__.modelname", "string",

		 ""]
# </rtc-template>

##
# @class loadmodel
# @brief ModuleDescription
#
#
class loadmodel(OpenRTM_aist.DataFlowComponentBase):

	##
	# @brief constructor
	# @param manager Maneger Object
	#
	def __init__(self, manager):
		OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

		#self._d_cam_in = OpenRTM_aist.instantiateDataType(Img.CameraImage)
		self._d_cam_in = RTC.CameraImage(RTC.Time(0,0),0,0,0,"", 0.0,[])
		"""
		"""
		self._cam_inIn = OpenRTM_aist.InPort("cam_in", self._d_cam_in)
		self._d_result = OpenRTM_aist.instantiateDataType(RTC.TimedLong)
		"""
		"""
		self._resultOut = OpenRTM_aist.OutPort("result", self._d_result)





		# initialize of configuration-data.
		# <rtc-template block="init_conf_param">
		"""
		
		 - Name:  modelname
		 - DefaultValue: None
		"""
		self._modelname = ['applebanana']

		# </rtc-template>



	##
	#
	# The initialize action (on CREATED->ALIVE transition)
	# formaer rtc_init_entry()
	#
	# @return RTC::ReturnCode_t
	#
	#
	def onInitialize(self):

		
		# Bind variables and configuration variable
		self.bindParameter("modelname", self._modelname, "None")

		# Set InPort buffers
		self.addInPort("cam_in",self._cam_inIn)

		# Set OutPort buffers
		self.addOutPort("result",self._resultOut)

		# Set service provider to Ports

		# Set service consumers to Ports

		# Set CORBA Service Ports

		return RTC.RTC_OK

	###
	##
	## The finalize action (on ALIVE->END transition)
	## formaer rtc_exiting_entry()
	##
	## @return RTC::ReturnCode_t
	#
	##
	#def onFinalize(self):
	#
	#	return RTC.RTC_OK

	###
	##
	## The startup action when ExecutionContext startup
	## former rtc_starting_entry()
	##
	## @param ec_id target ExecutionContext Id
	##
	## @return RTC::ReturnCode_t
	##
	##
	#def onStartup(self, ec_id):
	#
	#	return RTC.RTC_OK

	###
	##
	## The shutdown action when ExecutionContext stop
	## former rtc_stopping_entry()
	##
	## @param ec_id target ExecutionContext Id
	##
	## @return RTC::ReturnCode_t
	##
	##
	#def onShutdown(self, ec_id):
	#
	#	return RTC.RTC_OK

	##
	#
	# The activated action (Active state entry action)
	# former rtc_active_entry()
	#
	# @param ec_id target ExecutionContext Id
	#
	# @return RTC::ReturnCode_t
	#
	#
	def onActivated(self, ec_id):
		modelname = "model/" + self._modelname[0]+"/"+ self._modelname[0]+ ".hdf5"
		csvpass = "model/" +self._modelname[0]+"/"+ self._modelname[0]+".csv"
		
		self.model = keras.models.load_model(modelname)
		self.answer = pd.read_csv(csvpass, encoding="shift-jis")
		
		print(ec_id)
		print(self._modelname[0])

		return RTC.RTC_OK

	##
	#
	# The deactivated action (Active state exit action)
	# former rtc_active_exit()
	#
	# @param ec_id target ExecutionContext Id
	#
	# @return RTC::ReturnCode_t
	#
	#
	def onDeactivated(self, ec_id):
		cv2.destroyAllWindows()
		
		return RTC.RTC_OK

	##
	#
	# The execution action that is invoked periodically
	# former rtc_active_do()
	#
	# @param ec_id target ExecutionContext Id
	#
	# @return RTC::ReturnCode_t
	#
	#
	def onExecute(self, ec_id):
		X = []
		
		if self._cam_inIn.isNew():
			data = self._cam_inIn.read()

			image = np.frombuffer(data.pixels, dtype= np.uint8)
			image = image.reshape(data.height, data.width, 3)

			image_a = cv2.resize(image, (50, 50))
			image_a = np.asarray(image_a)
			image_a = image_a.flatten()
			X.append(image_a)
			X = np.array(X) / 255

			result = self.model.predict(X)
			possible = np.argmax(result[0,]) #一番可能性があるもの
			possible_value = result[0, possible] #一番可能性があるものの正解確率

			if possible_value < 0.85:
				cv2.putText(image, "no found", (2,50), cv2.FONT_HERSHEY_PLAIN, 4, (255, 0, 0), 5, cv2.LINE_AA )
				cv2.imshow("frame", image)
			
			else:
				cv2.putText(image,self.answer.answer[possible]+":"+str(possible_value), (2,50), cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 255/(possible + 1)), 5, cv2.LINE_AA )

		
			cv2.imshow("frame", image)
			k = cv2.waitKey(1) & 0xFF

		return RTC.RTC_OK

	###
	##
	## The aborting action when main logic error occurred.
	## former rtc_aborting_entry()
	##
	## @param ec_id target ExecutionContext Id
	##
	## @return RTC::ReturnCode_t
	##
	##
	#def onAborting(self, ec_id):
	#
	#	return RTC.RTC_OK

	###
	##
	## The error action in ERROR state
	## former rtc_error_do()
	##
	## @param ec_id target ExecutionContext Id
	##
	## @return RTC::ReturnCode_t
	##
	##
	#def onError(self, ec_id):
	#
	#	return RTC.RTC_OK

	###
	##
	## The reset action that is invoked resetting
	## This is same but different the former rtc_init_entry()
	##
	## @param ec_id target ExecutionContext Id
	##
	## @return RTC::ReturnCode_t
	##
	##
	#def onReset(self, ec_id):
	#
	#	return RTC.RTC_OK

	###
	##
	## The state update action that is invoked after onExecute() action
	## no corresponding operation exists in OpenRTm-aist-0.2.0
	##
	## @param ec_id target ExecutionContext Id
	##
	## @return RTC::ReturnCode_t
	##

	##
	#def onStateUpdate(self, ec_id):
	#
	#	return RTC.RTC_OK

	###
	##
	## The action that is invoked when execution context's rate is changed
	## no corresponding operation exists in OpenRTm-aist-0.2.0
	##
	## @param ec_id target ExecutionContext Id
	##
	## @return RTC::ReturnCode_t
	##
	##
	#def onRateChanged(self, ec_id):
	#
	#	return RTC.RTC_OK




def loadmodelInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=loadmodel_spec)
    manager.registerFactory(profile,
                            loadmodel,
                            OpenRTM_aist.Delete)

def MyModuleInit(manager):
    loadmodelInit(manager)

    # Create a component
    comp = manager.createComponent("loadmodel")

def main():
	mgr = OpenRTM_aist.Manager.init(sys.argv)
	mgr.setModuleInitProc(MyModuleInit)
	mgr.activateManager()
	mgr.runManager()

if __name__ == "__main__":
	main()

