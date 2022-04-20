"""SANItf2_algorithmSANIsharedModulesNonContiguousFullConnectivity.py

# Author:
Richard Bruce Baxter - Copyright (c) 2020-2022 Baxter AI (baxterai.com)

# License:
MIT License

# Installation:
see SANItf2.py

# Usage:
see SANItf2.py

# Description:
SANItf algorithm SANI shared modules non-contiguous full connectivity - define Sequentially Activated Neuronal Input neural network with shared modules non-contiguous full connectivity

See shared modules
SANItf2_algorithmSANIsharedModulesNonContiguousFullConnectivity has been developed with the following features:
	!useTcontiguity:enforceTcontiguityConstraints: no time/word index contiguity requirements (only sequentiality of neuronal inputs are enforced)
	supportFullConnectivity: supports full connectivity between layers (including supportSkipLayers)
	supportFeedback: supports feedback (higher to lower layer connectivity)
	SANIsharedModules: supports either sliding window input (True) or full contextual input (False) 
	#useHebbianLearningRuleApply: supports hebbian learning algorithm
	
"""

#start common SANItf2_algorithmSANI.py code:

import tensorflow as tf
import numpy as np
from ANNtf2_operations import * #generateParameterNameSeq, generateParameterName
import SANItf2_algorithmSANIoperations
from SANItf2_algorithmSANIglobalDefs import *
import ANNtf2_globalDefs


#parameters
#static parameters (convert from tf.variable to tf.constant?):
Cseq = {}
CseqLayer = {}	
n_h_cumulative = {}
#variable parameters:
WRseq = {}	#weights matrix
WR = {}	#weights matrix
BR = {}	#biases vector
Wseq = {}	#weights matrix
Bseq = {}	#biases vector
W = {}	#weights matrix
B = {}	#biases vector
if(useLearningRuleBackpropagation):
	Whead = [] #final linear layer weights matrix

#parameters
#static parameters (convert from tf.variable to tf.constant?):
#if(not supportFullConnectivity):
#	if(useSparseTensors):
#		Cseq = {}	#connectivity vector
#		if(supportSkipLayers):	
#			CseqLayer = {}	
#			n_h_cumulative = {}
##variable parameters:	
#if((algorithmSANI == "sharedModulesNonContiguousFullConnectivity") or (algorithmSANI == "sharedModulesBinary") or (algorithmSANI == "sharedModules")):
#	if(recordNetworkWeights):
#		if(recordSubInputsWeighted):
#			AseqInputVerified = {}
#			WRseq = {}	#weights matrix
#		if(recordSequentialInputsWeighted):
#			WR = {}	#weights matrix
#		if(recordNeuronsWeighted):
#			BR = {}	#biases vector
#if((algorithmSANI == "sharedModulesNonContiguousFullConnectivity") or (algorithmSANI == "sharedModules") or (algorithmSANI == "repeatedModules")):
#	#variable parameters (tf.variable): 
#	if(allowMultipleSubinputsPerSequentialInput):
#		if(performSummationOfSubInputsWeighted):
#			Wseq = {}	#weights matrix
#			Bseq = {}	#biases vector
#	if(performSummationOfSequentialInputsWeighted):
#		W = {}	#weights matrix
#		B = {}	#biases vector
	
			
#Network parameters
n_h = []
numberOfLayers = 0

#if((algorithmSANI == "sharedModulesNonContiguousFullConnectivity") or (algorithmSANI == "sharedModulesBinary") or (algorithmSANI == "sharedModules")):	#only code to currently use these variables
numberOfFeaturesPerWord = -1
paddingTagIndex = -1
def defineTrainingParametersSANIsharedModules(numberOfFeaturesPerWordNew, paddingTagIndexNew):
	#if((algorithmSANI == "sharedModulesNonContiguousFullConnectivity") or (algorithmSANI == "sharedModulesBinary") or (algorithmSANI == "sharedModules")):	#only code to currently use these variables
	global numberOfFeaturesPerWord
	global paddingTagIndex
	numberOfFeaturesPerWord = numberOfFeaturesPerWordNew
	paddingTagIndex = paddingTagIndexNew

def defineNetworkParametersSANIwrapper(num_input_neurons, num_output_neurons, datasetNumFeatures, dataset, useSmallSentenceLengths, numberOfFeaturesPerWord):
	global n_h
	global numberOfLayers
	n_h, numberOfLayers = SANItf2_algorithmSANIoperations.defineNetworkParametersSANI(num_input_neurons, num_output_neurons, datasetNumFeatures, dataset, useSmallSentenceLengths, numberOfFeaturesPerWord)
	return numberOfLayers
	
def defineTrainingParametersSANIwrapper(dataset, trainMultipleFiles):
	return SANItf2_algorithmSANIoperations.defineTrainingParametersSANI(dataset, trainMultipleFiles)
	

def defineNeuralNetworkParameters():
	global n_h_cumulative
	if(useLearningRuleBackpropagation):
		global Whead
		randomNormal = tf.initializers.RandomNormal()
		Whead = tf.Variable(randomNormal([n_h[numberOfLayers], numberOfFeaturesPerWord], dtype=tf.float32))
	SANItf2_algorithmSANIoperations.defineNeuralNetworkParametersSANI(n_h, numberOfLayers, Cseq, CseqLayer, n_h_cumulative, WRseq, WR, BR, Wseq, Bseq, W, B)
			

#temporary variables for neuralNetworkPropagationSANI:
if(algorithmSANI == "sharedModulesNonContiguousFullConnectivity"):
	Vseq = {}
	Zseq = {}
	Aseq = {}
	Z = {}
	A = {}
	sequentialActivationFound = {}	#CHECKTHIS: is this required?
	#if(useHebbianLearningRuleApply):
	#	WseqDelta = {}	#prospective weights update

#end common SANItf2_algorithmSANI.py code


def neuralNetworkPropagation(x, networkIndex=None):
	return neuralNetworkPropagationSANI(x)

def neuralNetworkPropagationSANI(x):
	
	#print("x = ", x)
	
	#print("x.shape = ", x.shape)	
	
	#note SANItf2_algorithmSANIsharedModulesNonContiguousFullConnectivity does not use time/contiguity checks
		
	#definitions for reference:
	
	#neuron sequential input vars;
	#x/AprevLayer	#output vector (dim: batchSize*n_h[l])
	#Wseq #weights of connections (dim: n_h[l-1]*n_h[l])
	#AseqSum	#combination variable
	#Vseq	#mutable verification vector (dim: batchSize*n_h[l] - regenerated for each sequential input index)
	#Zseq	#neuron activation function input vector (dim: batchSize*n_h[l]  - regenerated for each sequential input index)
	#Aseq	#neuron activation function output vector (dim: batchSize*n_h[l]  - regenerated for each sequential input index)
	
	#neuron vars;
	#Q
	#Z	#neuron activation function input (dim: batchSize*n_h[l])
	#A	#neuron activation function output (dim: batchSize*n_h[l])
	#if(performSummationOfSequentialInputsWeighted):	
		#W	(dim: numberOfSequentialInputs*n_h[l])
	
	#combination vars (per layer);
	#if(performSummationOfSequentialInputs):
		#these are all used for different methods of sequential input summation:
		#if(sequentialInputCombinationModeSummation == 1):
			#ZseqSum	#(dim: batchSize*n_h[l])
		#if(sequentialInputCombinationModeSummation == 2):
			#AseqSum	#(dim: batchSize*n_h[l])
		#if(sequentialInputCombinationModeSummation == 3):
			#ZseqWeightedSum	#(dim: batchSize*n_h[l])
		#if(sequentialInputCombinationModeSummation == 4):
			#AseqWeightedSum	#(dim: batchSize*n_h[l])
	
	batchSize = x.shape[0]
	
	for l in range(1, numberOfLayers+1):
		Z[generateParameterName(l, "Z")] = tf.Variable(tf.zeros([batchSize, n_h[l]]), dtype=tf.float32)
		A[generateParameterName(l, "A")] = tf.Variable(tf.zeros([batchSize, n_h[l]]), dtype=tf.float32)
		for s in range(numberOfSequentialInputs):
			Vseq[generateParameterNameSeq(l, s, "Vseq")] = tf.Variable(tf.dtypes.cast(tf.zeros([batchSize, n_h[l]]), tf.bool), dtype=tf.bool)
			Zseq[generateParameterNameSeq(l, s, "Zseq")] = tf.Variable(tf.zeros([batchSize, n_h[l]]), dtype=tf.float32)
			Aseq[generateParameterNameSeq(l, s, "Aseq")] = tf.Variable(tf.zeros([batchSize, n_h[l]]), dtype=tf.float32)
			
			#if(useHebbianLearningRuleApply):
			#	if(supportFeedback):
			#		l2Max = numberOfLayers
			#	else:
			#		l2Max = l-1
			#	for l2 in range(0, l2Max+1):
			#		WseqDelta[generateParameterNameSeqSkipLayers(l, l2, s, "WseqDelta")] = tf.Variable(tf.zeros([n_h[l2], n_h[l]]), dtype=tf.float32)	
					
	if(SANIsharedModules):
			
		#optimise feed length based on max sentence length in batch:
		#unoptimised: numberOfFeatures = x.shape[1]
		xIsNotPadding = tf.math.less(x, paddingTagIndex) #tf.math.less(tf.dtypes.cast(x, tf.int32), paddingTagIndex)
		coordinatesOfNotPadding = tf.where(xIsNotPadding)
		numberOfFeaturesCropped = tf.reduce_max(coordinatesOfNotPadding[:, 1]).numpy()+1

		if(inputNumberFeaturesForCurrentWordOnly):
			inputLength = numberOfFeaturesPerWord
		else:
			inputLength = numberOfFeaturesPerWord*numberOfWordsInConvolutionalWindowSeen
			
		maxNumberOfWordsInSentenceBatch = int(numberOfFeaturesCropped/numberOfFeaturesPerWord)

		#for w in range(maxNumberOfWordsInSentenceBatch):
		#for w in range(0, 1):
		for w in range(maxNumberOfWordsInSentenceBatch-numberOfWordsInConvolutionalWindowSeen+1):

			print("w =", w)
			
			for l in range(1, numberOfLayers+1):
				sequentialActivationFound[generateParameterName(l, "sequentialActivationFound")] = tf.Variable(tf.dtypes.cast(tf.zeros([batchSize, n_h[l]]), tf.bool), dtype=tf.bool)	#CHECKTHIS: is this required?
			
			if(inputNumberFeaturesForCurrentWordOnly):
				AfirstLayerShifted = x[:, w*numberOfFeaturesPerWord:w*numberOfFeaturesPerWord+inputLength]
			else:
				if(w == 0):
					AfirstLayerShifted = x[:, 0:inputLength]
				else:
					paddings = tf.constant([[0, 0], [w*numberOfFeaturesPerWord, 0]])	#shift input to the right by x words (such that a different input window will be presented to the network)
					#AfirstLayerShifted = x[:, w*numberOfFeaturesPerWord:min(w*numberOfFeaturesPerWord+inputLength, numberOfFeaturesCropped)]
					AfirstLayerShifted = x[:, w*numberOfFeaturesPerWord:w*numberOfFeaturesPerWord+inputLength]
					tf.pad(AfirstLayerShifted, paddings, "CONSTANT")

			#printShape(AfirstLayerShifted, "AfirstLayerShifted")

			AfirstLayerShifted = tf.dtypes.cast(AfirstLayerShifted, tf.float32)	#added 01 Sept 2021 #convert input from int to float
			A[generateParameterName(0, "A")] = AfirstLayerShifted
			
			pred = neuralNetworkPropagationSANIfeed(AfirstLayerShifted)
			
			#exit()
	else:

		AfirstLayer = x
		
		AfirstLayer = tf.dtypes.cast(AfirstLayer, tf.float32)	#added 01 Sept 2021 #convert input from int to float
		A[generateParameterName(0, "A")] = AfirstLayer
		pred = neuralNetworkPropagationSANIfeed(AfirstLayer)
			
	return pred
		
def neuralNetworkPropagationSANIfeed(AfirstLayer):
	
	batchSize = AfirstLayer.shape[0]

	for l in range(1, numberOfLayers+1):
		
		print("\tl =", l)

		if(supportFeedback):
			l2Max = numberOfLayers
		else:
			l2Max = l-1
							
		#combination vars;
		if(performSummationOfSequentialInputs):
			#these are all used for different methods of sequential input summation:
			if(sequentialInputCombinationModeSummation == 1):
				ZseqSum = tf.zeros([batchSize, n_h[l]], tf.float32)
			if(sequentialInputCombinationModeSummation == 2):
				AseqSum = tf.zeros([batchSize, n_h[l]], tf.float32)
			if(sequentialInputCombinationModeSummation == 3):
				ZseqWeightedSum = tf.zeros([batchSize, n_h[l]], tf.float32)
			if(sequentialInputCombinationModeSummation == 4):
				AseqWeightedSum = tf.zeros([batchSize, n_h[l]], tf.float32)
			
		for s in range(numberOfSequentialInputs):
			
			print("\t\ts =", s)
			
			#calculate ZseqHypothetical for sequential input
			if(supportFullConnectivity):
				ZseqHypothetical = tf.zeros([batchSize, n_h[l]])	#same dimensions as Zseq
				
				for l2 in range(0, l2Max+1):
					print("\t\t\tl2 =", l2)
					
					AseqInput = A[generateParameterName(l2, "A")]
					WseqCurrent = Wseq[generateParameterNameSeqSkipLayers(l, l2, s, "Wseq")]
					#print("AseqInput = ", AseqInput)
					#print("WseqCurrent = ", WseqCurrent)	
					ZseqHypotheticalAddition = tf.matmul(AseqInput, Wseq[generateParameterNameSeqSkipLayers(l, l2, s, "Wseq")])	
					#print("ZseqHypotheticalAddition = ", ZseqHypotheticalAddition)
					
					ZseqHypothetical = tf.add(ZseqHypothetical, ZseqHypotheticalAddition)
					#print("ZseqHypotheticalAddition = ", ZseqHypotheticalAddition)
					
				ZseqHypothetical = tf.add(ZseqHypothetical, Bseq[generateParameterNameSeq(l, s, "Bseq")])
					
				#check output threshold
				ZseqPassThresold = tf.math.greater(ZseqHypothetical, sequentialInputActivationThreshold)
			else:
				print("neuralNetworkPropagationSANI error: requires supportFullConnectivity")

			#calculate validation matrix based upon sequentiality requirements
			if(s == 0):
				VseqExisting = tf.fill([batchSize, n_h[l]], True)	#all values of Vseq0_l are always set to 1 as they have no sequential dependencies		
			else:
				VseqPrevTest = VseqPrev
				#note SANItf2_algorithmSANIsharedModulesNonContiguousFullConnectivity does not use time/word index contiguity checks
				VseqExisting = VseqPrevTest	#if previous sequentiality check fails, then all future sequentiality checks must fail	
			
			VseqFloat = tf.dtypes.cast(VseqExisting, tf.float32)
						
			#apply validation matrix
			ZseqCurrent = tf.multiply(ZseqHypothetical, VseqFloat)
				
			if(performSummationOfSubInputsNonlinear):	#CHECKTHIS: should be made redundant by choice of sequentialInputCombinationModeSummation
				AseqCurrent = tf.nn.sigmoid(ZseqCurrent)	#or relu
			else:
				if(performSummationOfSubInputsBinary):
					ZseqCurrentBool = tf.math.greater(ZseqCurrent, 0.0)
					AseqCurrent = tf.dtypes.cast(ZseqCurrentBool, tf.float32)  
				else:
					AseqCurrent = ZseqCurrent
				
			#update Vseq/Zseq/Aseq
			VseqUpdated = tf.math.logical_and(ZseqPassThresold, VseqExisting)
			
			#print("VseqExisting = ", VseqExisting)	
			#print("ZseqPassThresold = ", ZseqPassThresold)
			print("VseqUpdated = ", VseqUpdated)

			Vseq[generateParameterNameSeq(l, s, "Vseq")] = VseqUpdated
			Zseq[generateParameterNameSeq(l, s, "Zseq")] = ZseqCurrent
			Aseq[generateParameterNameSeq(l, s, "Aseq")] = AseqCurrent
			
			
			#if(useHebbianLearningRuleApply):
			#	for l2 in range(0, l2Max+1):
			#		#constrain learning (weight updates) to where VseqUpdated is True:
			#		
			#		AseqInput = A[generateParameterName(l2, "A")]
			#		AseqInputSqueezed = tf.squeeze(AseqInput, axis=0)	#batchSize must equal 1
			#		AseqInputSqueezed = tf.expand_dims(AseqInputSqueezed, axis=1)
			#		multiples = tf.constant([1,n_h[l]], tf.int32)
			#		AseqInputTiled = tf.tile(AseqInputSqueezed, multiples)
			#
			#		VseqUpdatedFloat = tf.dtypes.cast(VseqUpdated, tf.float32)	
			#		VseqUpdatedFloatSqueeze = tf.squeeze(VseqUpdatedFloat, axis=0)	#batchSize must equal 1
			#		VseqUpdatedFloatSqueeze = tf.expand_dims(VseqUpdatedFloatSqueeze, axis=0)
			#		multiples = tf.constant([n_h[l2],1], tf.int32)
			#		VseqUpdatedFloatTiled = tf.tile(VseqUpdatedFloatSqueeze, multiples)
			#		
			#		AseqMod = tf.subtract(tf.multiply(AseqInputSqueezed, 2.0), 1.0)
			#		WseqDeltaSign = tf.multiply(AseqMod, VseqUpdatedFloatTiled)	
			#		WseqDeltaCurrent = tf.multiply(WseqDeltaSign, hebbianLearningRate)
			#		WseqDelta[generateParameterNameSeqSkipLayers(l, l2, s, "WseqDelta")] = WseqDeltaCurrent 
			#		
			#		#print("AseqInputTiled = ", AseqInputTiled)
			#		#print("VseqUpdatedFloatTiled = ", VseqUpdatedFloatTiled)
			#		#print("WseqDeltaSign = ", WseqDeltaSign)

								
			if(performSummationOfSequentialInputs):
				if(performSummationOfSequentialInputsWeighted):
					multiples = tf.constant([batchSize,1], tf.int32)
					Wtiled = tf.tile(tf.reshape(W[generateParameterName(l, "W")][s], [1, n_h[l]]), multiples)
						
				#these are all used for different methods of sequential input summation
				if(sequentialInputCombinationModeSummation == 1):
					ZseqSum = tf.add(ZseqSum, ZseqCurrent)
				if(sequentialInputCombinationModeSummation == 2):
					AseqSum = tf.math.add(AseqSum, AseqCurrent)
				if(sequentialInputCombinationModeSummation == 3):
					ZseqWeighted = tf.multiply(ZseqCurrent, Wtiled)
					ZseqWeightedSum = tf.math.add(ZseqWeightedSum, ZseqWeighted)
				if(sequentialInputCombinationModeSummation == 4):	
					AseqWeighted = tf.multiply(AseqCurrent, Wtiled)
					AseqWeightedSum = tf.math.add(AseqWeightedSum, AseqWeighted)	
					
			if(s == numberOfSequentialInputs-1):
				ZseqLast = Zseq[generateParameterNameSeq(l, s, "Zseq")]
				AseqLast = Aseq[generateParameterNameSeq(l, s, "Aseq")]
				VseqLast = Vseq[generateParameterNameSeq(l, s, "Vseq")]
	
			VseqPrev = VseqUpdated
			

		if(performSummationOfSequentialInputs):
			if(sequentialInputCombinationModeSummation == 1):
				Z1 = ZseqSum
				if(sequentialInputCombinationModeSummationAveraged):
					Z1 = Z1/numberOfSequentialInputs
				if(performSummationOfSequentialInputsNonlinear):
					A1 = tf.nn.sigmoid(Z1)	#no weights are applied
				else:
					A1 = Z1
			elif(sequentialInputCombinationModeSummation == 2):
				Z1 = AseqSum
				if(sequentialInputCombinationModeSummationAveraged):
					Z1 = Z1/numberOfSequentialInputs
				if(performSummationOfSequentialInputsNonlinear):
					A1 = tf.nn.sigmoid(Z1)	#no weights are applied
				else:
					A1 = Z1	
			elif(sequentialInputCombinationModeSummation == 3):
				Z1 = ZseqWeightedSum
				if(performSummationOfSequentialInputsNonlinear):
					A1 = tf.nn.sigmoid(Z1)
				else:
					A1 = Z1
			elif(sequentialInputCombinationModeSummation == 4):
				Z1 = AseqWeightedSum
				if(performSummationOfSequentialInputsNonlinear):
					A1 = tf.nn.sigmoid(Z1)
				else:
					A1 = Z1
					
			#if(performSummationOfSequentialInputsVerify):
			#	Z1 = tf.multiply(Z1, tf.dtypes.cast(VseqLast, tf.float32))
			#	A1 = tf.multiply(A1, tf.dtypes.cast(VseqLast, tf.float32))	
		else:
			#VseqLastFloat = VseqFloat
			Z1 = ZseqLast
			A1 = AseqLast

		A[generateParameterName(l, "A")] = A1
		Z[generateParameterName(l, "Z")] = Z1

		#if(useHebbianLearningRuleApply):
		#	for s2 in range(numberOfSequentialInputs):
		#		for l2 in range(0, l2Max+1):
		#
		#			#only apply weight updates to neurons that fired (all sequential inputs passed):
		#			
		#			Asqueezed = tf.squeeze(A[generateParameterName(l, "A")], axis=0)	#batchSize must equal 1
		#			Asqueezed = tf.expand_dims(Asqueezed, axis=0)
		#			multiples = tf.constant([n_h[l2],1], tf.int32)
		#			ATiled = tf.tile(Asqueezed, multiples)
		#			ATiledActiveBool = tf.math.greater(ATiled, 0.0)
		#			ATiledActive = tf.dtypes.cast(ATiledActiveBool, tf.float32)
		#			
		#			WseqDeltaApplicable = tf.multiply(ATiledActive, WseqDelta[generateParameterNameSeqSkipLayers(l, l2, s2, "WseqDelta")])
		#			
		#			WseqUpdated = tf.add(Wseq[generateParameterNameSeqSkipLayers(l, l2, s2, "Wseq")], WseqDeltaApplicable)
		#			WseqUpdated = tf.clip_by_value(WseqUpdated, minimumConnectionWeight, maximumConnectionWeight)
		#			Wseq[generateParameterNameSeqSkipLayers(l, l2, s2, "Wseq")] = WseqUpdated 

	ZlastLayer = Z[generateParameterName(numberOfLayers, "Z")]
		
	if(useLearningRuleBackpropagation):
		pred = SANItf2_algorithmSANIoperations.generatePrediction(ZlastLayer, Whead)
	else:
		pred = ZlastLayer
	
	return pred
	
