from __future__ import print_function

import os
import re
import string

import awkward1 as ak
import boost_histogram as bh

def MaskQuantity(currentTree, currentQuantity, cut, condition):
	cut = cut.replace(" ", "").replace("\t", "")
	if re.search("||", cut):
		orStrings = cut.split("||")
		if re.search("&&", orStrings[0]):
			andStrings = orStrings[0].split("&&")
			currentCut = currentTree[re.sub("_[0-9]", "", andStrings[0])].array(library="ak")
			for andCut in andStrings[1:]:
				currentCut = currentCut and currentTree[re.sub("_[0-9]", "", andCut)].array(library="ak")
		else:
			currentCut = currentTree[re.sub("_[0-9]", "", orStrings[0])].array(library="ak")
		for orCut in orStrings[1:]:
			if re.search("&&", orCut):
				andStrings = orCut.split("&&")
				currentCut = currentTree[re.sub("_[0-9]", "", andStrings[0])].array(library="ak")
				for andCut in andStrings[1:]:
					currentCut = currentCut and currentTree[re.sub("_[0-9]", "", andCut)].array(library="ak")
			currentCut = currentCut or currentTree[re.sub("_[0-9]", "", orCut)].array(library="ak")
	elif re.search("&&", cut):
		andStrings = cut.split("&&")
		currentCut = currentTree[re.sub("_[0-9]", "", andStrings[0])].array(library="ak")
		for andCut in andStrings[1:]:
			currentCut = currentCut and currentTree[re.sub("_[0-9]", "", andCut)].array(library="ak")
	else:
		currentCut = currentTree[re.sub("_[0-9]", "", cut)].array(library="ak")

	if re.search("_[1-9]", cut):
		indexOfInterest = int(cut[-1]) - 1
		currentCut = currentCut.mask[ak.num(currentCut) > indexOfInterest][:,indexOfInterest]
	if (condition == "True"):
		return currentQuantity.mask[currentCut]
	elif (condition == "False"):
		return currentQuantity.mask[~currentCut]
	elif (condition[0:2] == ">="):
		return currentQuantity.mask[currentCut >= int(condition[2:])]
	elif (condition[0:2] == "<="):
		return currentQuantity.mask[currentCut <= int(condition[2:])]
	elif (condition[0] == ">"):
		return currentQuantity.mask[currentCut > int(condition[1:])]
	elif (condition[0] == "<"):
		return currentQuantity.mask[currentCut > int(condition[1:])]
	elif (condition[0:2] == "!="):
		return currentQuantity.mask[currentCut != int(condition[2:])]
	elif (condition[0:2] == "=="):
		return currentQuantity.mask[currentCut == int(condition[2:])]
	else:
		print("Check your plotConfig.json! The cut condition is improperly defined!")
		exit(-1)

def ConstructHistogram(plotConfig, quantity):
	if plotConfig[quantity]["isRegular"] == "True":
		return bh.axis.Regular(plotConfig[quantity]["nBins"], plotConfig[quantity]["x_min"], plotConfig[quantity]["x_max"])
	else:
		return bh.axis.Variable(plotConfig[quantity]["binning"])

def GetLuminosity(fileName): #[fb^-1]
		if re.search("2016", fileName) or re.search("RunIISummer16", fileName):
			return 35.90
		elif re.search("2017", fileName):
			return 41.90
		elif re.search("2018", fileName):
			return 59.74
		else:
			print("Luminosity not defined for %s!!" % fileName)
			return 0

def GetXSection(fileName): #[pb]
	if   fileName.find("DYJetsToLL_M-50_HT-70to100"             ) != -1 : return 169.9# ± 0.5
	elif fileName.find("DYJetsToLL_M-50_HT-100to200"            ) != -1 : return 147.40# ± 0.09
	elif fileName.find("DYJetsToLL_M-50_HT-200to400"            ) != -1 : return 40.99# ± 0.04
	elif fileName.find("DYJetsToLL_M-50_HT-400to600"            ) != -1 : return 5.678# ± 0.005
	elif fileName.find("DYJetsToLL_M-50_HT-600toInf"            ) != -1 : return 2.198# ± 0.002
	elif fileName.find("DYJetsToLL_M-50_HT-600to800"            ) != -1 : return 1.367
	elif fileName.find("DYJetsToLL_M-50_HT-800to1200"           ) != -1 : return 0.6304
	elif fileName.find("DYJetsToLL_M-50_HT-1200to2500"          ) != -1 : return 0.1514
	elif fileName.find("DYJetsToLL_M-50_HT-2500toInf"           ) != -1 : return 0.003565
	elif fileName.find("WJetsToQQ_HT"                           ) !=-1 : return 95.14;
	elif fileName.find("ZJetsToQQ_HT600toInf"                   ) !=-1 : return 41.34;
	elif fileName.find("QCD_HT100to200_TuneCUETP8M1"            ) != -1 : return 27990000#± 4073
	elif fileName.find("QCD_HT200to300_TuneCUETP8M1"            ) != -1 : return 1712000#± 376.3
	elif fileName.find("QCD_HT300to500_TuneCUETP8M1"            ) != -1 : return 347700#± 74.81
	elif fileName.find("QCD_HT500to700_TuneCUETP8M1"            ) != -1 : return 32100#± 7
	elif fileName.find("QCD_HT700to1000_TuneCUETP8M1"           ) != -1 : return 6831#± 1.7
	elif fileName.find("QCD_HT1000to1500_TuneCUETP8M1"          ) != -1 : return 1207#± 0.5
	elif fileName.find("QCD_HT1500to2000_TuneCUETP8M1"          ) != -1 : return 119.9#± 0.06
	elif fileName.find("QCD_HT2000toInf_TuneCUETP8M1"           ) != -1 : return 25.24#± 0.02
	#elif fileName.find("TT_TuneCUETP8M2T4"                      ) !=-1 : return  831.76      ;
	#elif fileName.find("TT_TuneEE5C_13TeV-powheg-herwigpp"      ) !=-1 : return  831.76      ;
	#elif fileName.find("TTTo2L2Nu_13TeV") != -1 : return 87.31#+2.08-3.07+3.68-3.68pb
	#elif fileName.find("TTJets_"                                ) !=-1 : return  831.76      ;
	elif fileName.find("TTTo2L2Nu_13TeV") != -1 : return 87.31#+2.08-3.07+3.68-3.68pb
	elif fileName.find("TT_TuneCUETP8M1") != -1 : return 831.76#+19.77-29.20+35.06-35.06pb
	elif fileName.find("TT_TuneZ2star_13TeV") != -1 : return 831.76#+19.77-29.20+35.06-35.06pb
	elif fileName.find("TTJets_HT-2500toInf_TuneCUETP8M1") != -1 : return 0.001430#±0.000017
	elif fileName.find("TTJets_") != -1 : return 831.76#+19.77-29.20+35.06-35.06pb
	#elif fileName.find("TTJets_SingleLeptFromT_TuneCUETP8M1") != -1 : return #filler
	elif fileName.find("WJetsToLNu_TuneCUETP8M1_13TeV") != -1 : return 61526.7#+497.1-264.6±2312.7pb
	#elif fileName.find("WJetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8") != -1 : return 61526.7#+497.1-264.6±2312.7pb
	elif fileName.find("WJetsToLNu_HT-100To200"                 ) != -1 : return 1345#±1.2
	elif fileName.find("WJetsToLNu_HT-200To400"                 ) != -1 : return 359.7#±0.20
	elif fileName.find("WJetsToLNu_HT-400To600"                 ) != -1 : return 48.91#±0.072
	elif fileName.find("WJetsToLNu_HT-600ToInf"                 ) != -1 : return 18.77#±0.10
	elif fileName.find("WJetsToLNu_HT-600To800"                 ) != -1 : return 12.05#±0.0073
	elif fileName.find("WJetsToLNu_HT-800To1200"                ) != -1 : return 5.501#±0.017
	elif fileName.find("WJetsToLNu_HT-1200To2500"               ) != -1 : return 1.329#±0.0025
	elif fileName.find("WJetsToLNu_HT-2500ToInf"                ) != -1 : return 0.03216#±0.000104
	elif fileName.find("WJetsToQQ_HT-600ToInf"                  ) != -1 : return 95.14#±3.57
	elif fileName.find("W1JetsToLNu_TuneCUETP8M1"               ) !=-1 : return 9644.5*1.22 ;
	elif fileName.find("W2JetsToLNu_TuneCUETP8M1"               ) !=-1 : return 3144.5*1.22 ;
	elif fileName.find("W3JetsToLNu_TuneCUETP8M1"               ) !=-1 : return  954.8*1.22 ;
	elif fileName.find("W4JetsToLNu_TuneCUETP8M1"               ) !=-1 : return  485.6*1.22 ;
	elif fileName.find("WW_TuneCUETP8M1"                        ) !=-1 : return 118.7        ;
	elif fileName.find("WZ_TuneCUETP8M1"                        ) !=-1 : return 47.13        ;
	elif fileName.find("ZZ_TuneCUETP8M1"                        ) !=-1 : return 16.5         ;
	elif fileName.find("ST_s-channel_4f_leptonDecays"           ) !=-1 : return 11.36*0.3272 ;
	elif fileName.find("ST_t-channel_top_4f_leptonDecays"       ) !=-1 : return 136.02*0.322 ;
	elif fileName.find("ST_t-channel_antitop_4f_leptonDecays"   ) !=-1 : return 80.95*0.322  ;
	elif fileName.find("ST_t-channel_antitop_4f_inclusiveDecays") !=-1 : return 136.02      ;
	elif fileName.find("ST_t-channel_top_4f_inclusiveDecays"    ) !=-1 : return 80.95        ;
	elif fileName.find("ST_tW_antitop_5f_inclusiveDecays"       ) !=-1 : return 35.6         ;
	elif fileName.find("ST_tW_top_5f_inclusiveDecays_"          ) !=-1 : return 35.6         ;
	elif fileName.find("SMS-T1tttt_mGluino-1200_mLSP-800"       ) !=-1 : return 0.04129   ;
	elif fileName.find("SMS-T1tttt_mGluino-1500_mLSP-100"       ) !=-1 : return 0.006889  ;
	elif fileName.find("SMS-T1tttt_mGluino-2000_mLSP-100"       ) !=-1 : return 0.0004488	;
	elif fileName.find("TTZToQQ_TuneCUETP8M1_13TeV-amcatnlo-pythia8") != -1 : return 0.5297#±0.0008
	elif fileName.find("TTZToLLNuNu_M-10_TuneCUETP8M1_13TeV-amcatnlo-pythia8") != -1 : return 0.2529#±0.0004
	elif fileName.find("TTWJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8") != -1 : return 0.2043#±0.0020
	elif fileName.find("TTWJetsToQQ_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8") != -1 : return 0.4062#±0.0021
	elif fileName.find("TTGJets_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8") != -1 : return 3.697#±0.0013
	elif fileName.find("TTGG_0Jets_TuneCUETP8M1_13TeV_amcatnlo_madspin_pythia8") != -1 : return 0.017
	elif fileName.find("TTTT_TuneCUETP8M1_13TeV-amcatnlo-pythia8") != -1 : return 0.009103
	elif fileName.find("ZZ_TuneCUETP8M1_13TeV-pythia8") != -1 : return 16.523
	#elif fileName.find("ZZTo4Q_13TeV_amcatnloFXFX_madspin_pythia8") != -1 : return XS
	elif fileName.find("ZZTo2Q2Nu_13TeV_amcatnloFXFX_madspin_pythia8") != -1 : return 4.04
	elif fileName.find("ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8") != -1 : return 3.22
	elif fileName.find("ZZTo4L_13TeV-amcatnloFXFX-pythia8") != -1 : return 1.212
	elif fileName.find("ZZTo2L2Nu_13TeV_powheg_pythia8") != -1 : return 0.564
	elif fileName.find("WWTo2L2Nu_13TeV-powheg") != -1 : return 12.178
	elif fileName.find("WWToLNuQQ_13TeV-powheg") != -1 : return 49.997
	elif fileName.find("WWTo4Q_13TeV-powheg") != -1 : return 51.723
	elif fileName.find("GluGluWWTo2L2Nu_MCFM_13TeV") != -1 : return 0.84365
	elif fileName.find("GluGluWWTo2L2Nu_HInt_MCFM_13TeV") != -1 : return 1.36
	elif fileName.find("WZ_TuneCUETP8M1_13TeV-pythia8") != -1 : return 47.13
	elif fileName.find("WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8") != -1 : return 10.71
	elif fileName.find("WZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8") != -1 : return 5.595
	elif fileName.find("WZTo3LNu_TuneCUETP8M1_13TeV-powheg-pythia8") != -1 : return 4.42965
	elif fileName.find("WZJets_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8") != -1 : return 5.26
	elif fileName.find("WZTo1L3Nu_13TeV_amcatnloFXFX_madspin_pythia8") != -1 : return 3.033e+00#+-2.060e-02
	elif fileName.find("ZZTo4L_13TeV_powheg_pythia8") != -1 : return 1.256
	elif fileName.find("GluGluToZZTo4e_BackgroundOnly_13TeV_MCFM") != -1 : return 0.001586
	elif fileName.find("GluGluToZZTo4mu_BackgroundOnly_13TeV_MCFM") != -1 : return 0.001586
	elif fileName.find("GluGluToZZTo4tau_BackgroundOnly_13TeV_MCFM") != -1 : return 0.001586
	elif fileName.find("GluGluToZZTo2e2mu_BackgroundOnly_13TeV_MCFM") != -1 : return 0.003194
	elif fileName.find("GluGluToZZTo2e2tau_BackgroundOnly_13TeV_MCFM") != -1 : return 0.003194
	elif fileName.find("GluGluToZZTo2mu2tau_BackgroundOnly_13TeV_MCFM") != -1 : return 0.003194
	elif fileName.find("WpWpJJ_QCD_TuneCUETP8M1_13TeV-madgraph-pythia8") != -1 : return 0.01538
	#elif fileName.find("comingsoon") != -1 : return 0.03711 #W+W+jj QCD +EWK
	elif fileName.find("WpWpJJ_EWK_TuneCUETP8M1_13TeV-madgraph-pythia8") != -1 : return 0.02064
	elif fileName.find("VVTo2L2Nu_13TeV_amcatnloFXFX_madspin_pythia8") != -1 : return 11.95
	elif fileName.find("WW_DoubleScattering_13TeV-pythia8") != -1 : return 1.64
	elif fileName.find("WGToLNuG_TuneCUETP8M1_13TeV-madgraphMLM-pythia8") != -1 : return 405.271
	elif fileName.find("WGToLNuG_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8") != -1 : return 489
	elif fileName.find("ZGTo2LG_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8") != -1 : return 117.864
	elif fileName.find("TGJets") != -1 : return 2.967#+- 0.01052 	NLO
	elif fileName.find("tZq_ll_") != -1 : return 0.0758
	elif fileName.find("tZq_nunu_4f") != -1 : return 0.1379
	elif fileName.find("SingleMuon")!=-1  or fileName.find("SingleElectron") !=-1 or fileName.find("JetHT")  !=-1 or fileName.find("MET") !=-1 or fileName.find("MTHT") !=-1: return 1.
	else:
		print("Cross section not defined. Skipping the %s sample." % fileName)
		return 0

def GetOSVariable(Var):
	try:
		variable = os.environ[Var]
	except KeyError:
		print("Please set the environment variable " + Var)
		sys.exit(1)
	return variable

def progressBar(nSamples, nFiles, nQuantities, sampleIndex, fileIndex, quantityIndex, quantity, barSize = 20):
	sampleRatio = float(sampleIndex) / nSamples
	fileRatio = float(fileIndex) / nFiles
	quantityRatio = float(quantityIndex) / nQuantities

	if nFiles < barSize:
		barSize = nFiles

	print("[" + "S" * sampleIndex   + "s" * (nSamples - sampleIndex) + "] " +
		"[" + "F" * int(fileRatio * barSize) + "f" * int((1 - fileRatio) * barSize) + "] " +
		"[" + "Q" * quantityIndex + "q" * (nQuantities - quantityIndex) + "] " + quantity,
		end="\r"
	)
	return 0

def getOutputs(outputdir, **kwargs):
	fileTypes = kwargs.get("fileTypes", ["png", "jpg", "pdf", "svg", "eps"])

	outputdirContent = os.listdir(outputdir)

	plotFiles = {}
	subdirs = []
	for OutputObject in outputdirContent:
		fullOutputObject = os.path.join(outputdir, OutputObject)

		if os.path.isfile(fullOutputObject):
			splitOutputObject = os.path.splitext(OutputObject)
			extension = splitOutputObject[-1].replace(".", "").lower()

			if extension in fileTypes:
				plotFiles.setdefault(splitOutputObject[0], []).append(extension)

		else:
			subdirs.append(fullOutputObject)

	for filename, extensions in plotFiles.items():
		extensions.sort(key=lambda extension: fileTypes.index(extension))
	subdirs.sort()

	return plotFiles, subdirs

def CreateIndexHtml(templateDir, outputDir, **kwargs):
	plotFiles, subdirs = getOutputs(outputDir, **kwargs)
	htmlTexts = {}
	for var in ["overview", "description", "subdir", "plot", "link"]:
		with open(os.path.expandvars(templateDir + "/template_webplot_{}.html".format(var))) as htmlFile:
			htmlTexts[var] = string.Template(htmlFile.read())
	#with open(os.path.expandvars("templateDir/template_webplotting_{}.html".format("plot"))) as htmlFile:
		#htmlTexts["plotjson"] = string.Template(htmlFile.read())

	# create remote dir
	print("Creating directory " + outputDir + "...")
	mkdirCommand = os.path.expandvars("$WEB_PLOTTING_MKDIR_COMMAND").format(subdir=outputDir)
	os.system(mkdirCommand)

	# treat subdirs recursively
	htmlDesciption = ""
	htmlSubdirs = ""
	for subdir in subdirs:
		CreateIndexHtml(templateDir, subdir, **kwargs)
		htmlSubdirs += htmlTexts["subdir"].substitute(subdir=os.path.relpath(subdir, outputDir))
	htmlDesciption = htmlTexts["description"].substitute(subdirs=htmlSubdirs)

	htmlPlots = ""
	for filename, extensions in sorted(plotFiles.items()):
		htmlPlots += htmlTexts["plot"].substitute(
				image=filename+"."+extensions[0],
				title=filename,
				links=" ".join([htmlTexts["link"].substitute(
						plot=filename+"."+extension,
						title=filename,
						extension=extension
				) for extension in extensions])
		)

	if not plotFiles == {}:
		htmlIndexFilename = os.path.join(outputDir, "index.html")
		with open(htmlIndexFilename, "w") as htmlIndexFile:
			htmlIndexFile.write(htmlTexts["overview"].substitute(
					title=kwargs.get("title", outputDir),
					description=htmlDesciption,
					plots=htmlPlots
				)
			)

	# copy files
	fullOutputDir = os.path.abspath(outputDir)
	outputDirContent = os.listdir(fullOutputDir)
	for OutputObject in outputDirContent:
		fullOutputObject = os.path.join(fullOutputDir, OutputObject)
		if os.path.isfile(fullOutputObject):
			print("Copying " + OutputObject + " into " + outputDir + "...")
			copyCommand = os.path.expandvars("$WEB_PLOTTING_COPY_COMMAND").format(source=fullOutputObject, subdir=outputDir)
			os.system(copyCommand)
