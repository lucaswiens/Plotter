import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import uproot4 as uproot
import boost_histogram as bh
import mplhep as hep
import pandas as pd
import awkward1 as ak

import argparse
import json
import re

def GetLuminosity(fileName): #[pb^-1]
	return 35900

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
	elif fileName.find("QCD_Pt_170to300_"                       ) !=-1 : return 117276.;
	elif fileName.find("QCD_Pt_300to470_"                       ) !=-1 : return 7823.;
	elif fileName.find("QCD_Pt_470to600_"                       ) !=-1 : return 648.2;
	elif fileName.find("QCD_Pt_600to800_"                       ) !=-1 : return 186.9;
	elif fileName.find("QCD_Pt_800to1000_"                      ) !=-1 : return 32.293;
	elif fileName.find("QCD_Pt_1000to1400_"                     ) !=-1 : return 9.4183;
	elif fileName.find("QCD_Pt_1400to1800_"                     ) !=-1 : return 0.84265;
	elif fileName.find("QCD_Pt_1800to2400_"                     ) !=-1 : return 0.114943;
	elif fileName.find("QCD_Pt_2400to3200_"                     ) !=-1 : return 0.006830;
	elif fileName.find("QCD_Pt_3200toInf_"                      ) !=-1 : return 0.000165445;
	elif fileName.find("QCD_HT100to200"                         ) !=-1 : return 27990000;
	elif fileName.find("QCD_HT200to300"                         ) !=-1 : return 1712000.;
	elif fileName.find("QCD_HT300to500"                         ) !=-1 : return 347700.;
	elif fileName.find("QCD_HT500to700"                         ) !=-1 : return 32100.;
	elif fileName.find("QCD_HT700to1000"                        ) !=-1 : return 6831.;
	elif fileName.find("QCD_HT1000to1500"                       ) !=-1 : return 1207.;
	elif fileName.find("QCD_HT1500to2000"                       ) !=-1 : return 119.9;
	elif fileName.find("QCD_HT2000toInf"                        ) !=-1 : return 25.24;
	elif fileName.find("QCD_Pt-15to7000"                        ) !=-1 or fileName.find( "QCD_Pt_15to7000" ) !=-1: return  2.022100000e+09*60.5387252324;
	elif fileName.find("TT_TuneCUETP8M2T4"                      ) !=-1 : return  831.76      ;
	elif fileName.find("TT_TuneEE5C_13TeV-powheg-herwigpp"      ) !=-1 : return  831.76      ;
	#elif fileName.find("TT_"                                    ) !=-1 : return  831.76      ; #for testing
	elif fileName.find("TTTo2L2Nu_13TeV") != -1 : return 87.31#+2.08-3.07+3.68-3.68pb
	elif fileName.find("TTJets_"                                ) !=-1 : return  831.76      ;
	## elif fileName.find("TTTo2L2Nu_13TeV") != -1 : return 87.31#+2.08-3.07+3.68-3.68pb
	## elif fileName.find("TT_TuneCUETP8M1") != -1 : return 831.76#+19.77-29.20+35.06-35.06pb
	## elif fileName.find("TT_TuneZ2star_13TeV") != -1 : return 831.76#+19.77-29.20+35.06-35.06pb
	## elif fileName.find("TTJets_TuneCUETP8M1") != -1 : return 831.76#+19.77-29.20+35.06-35.06pb
	## elif fileName.find("TTJets_TuneCUETP8M1") != -1 : return 831.76#+19.77-29.20+35.06-35.06pb
	## #elif fileName.find("TTJets_SingleLeptFromT_TuneCUETP8M1") != -1 : return #filler
	## elif fileName.find("TTJets_HT-2500toInf_TuneCUETP8M1") != -1 : return 0.001430#±0.000017

	elif fileName.find("WJetsToLNu_TuneCUETP8M1_13TeV") != -1 : return 61526.7#+497.1-264.6±2312.7pb
	elif fileName.find("WJetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8") != -1 : return 61526.7#+497.1-264.6±2312.7pb
	elif fileName.find("WJetsToLNu_HT-100To200_TuneCUETP8M1_13TeV-madgraphML") != -1 : return 1345#±1.2
	elif fileName.find("WJetsToLNu_HT-200To400_TuneCUETP8M1_13TeV-madgraphML") != -1 : return 359.7#±0.20
	elif fileName.find("WJetsToLNu_HT-400To600_TuneCUETP8M1_13TeV-madgraphML") != -1 : return 48.91#±0.072
	elif fileName.find("WJetsToLNu_HT-600ToInf_TuneCUETP8M1_13TeV-madgraphML") != -1 : return 18.77#±0.10
	elif fileName.find("WJetsToLNu_HT-600To800_TuneCUETP8M1_13TeV-madgraphML") != -1 : return 12.05#±0.0073
	elif fileName.find("WJetsToLNu_HT-800To1200_TuneCUETP8M1_13TeV-madgraphML") != -1 : return 5.501#±0.017
	elif fileName.find("WJetsToLNu_HT-1200To2500_TuneCUETP8M1_13TeV-madgraphML") != -1 : return 1.329#±0.0025
	elif fileName.find("WJetsToLNu_HT-2500ToInf_TuneCUETP8M1_13TeV-madgraphML") != -1 : return 0.03216#±0.000104
	elif fileName.find("WJetsToQQ_HT-600ToInf_TuneCUETP8M1_13TeV") != -1 : return 95.14#±3.57
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
	elif fileName.find("SingleMuon")!=-1  or fileName.find("SingleElectron") !=-1 or fileName.find("JetHT")  !=-1 or fileName.find("MET") !=-1 or fileName.find("MTHT") !=-1: return 1.
	else:
		print("Cross section not defined for %s!!" % fileName)
		return 0



if __name__ == "__main__":
	### Basic TColors as hexcode
	##kBlack   = "#000000"
	##kRed     = "#ff0000"
	##kGreen   = "#00ff00"
	##kBlue    = "#0000ff"
	##kYellow  = "#ffff00"
	##kMagenta = "#ff00ff"
	##kCyan    = "#00ffff"
	##kOrange  = "#ffcc00"
	##kViolet  = "#cc00ff"
	##kPink    = "#ff0033"

	#date = subprocess.check_output("date +\"%Y_%m_%d\"", shell=True).replace("\n", "")
	#cmsswBase = getOSVariable("CMSSW_BASE")

	parser = argparse.ArgumentParser(description="Creates plots from flat ntuples, requires config files in JSON format.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument("-i", "--input-directory",
		required=True,
		help="Path to the file containing a list of samples."
	)
	parser.add_argument("--keys",
		help="Prints keys of the root files inside the input directory",
		default = False,
		action="store_true"
	)
	parser.add_argument("--test-run",
		default = False,
		action="store_true",
		help = "Use only the first file for each sample for a quick run"
	)
	parser.add_argument("--y-label",
		default = "Events",
		help = "Label of the y-axis"
	)
	parser.add_argument("--plot-config",
		default = "data/config/plotConfig.json",
		help = "Path to the json file used to create plots: %(default)s"
	)
	parser.add_argument("--sample-config",
		default = "data/config/sampleConfigs.json",
		help = "Path to the json file containing the filenames of the samples: %(default)s"
	)
	parser.add_argument("-s", "--samples",
		nargs="+",
		default = ["zll", "ttv", "vv", "qcd", "ttbarll", "singletop", "wjets", "ttbarl"],
		help="Samples. [Default: %(default)s]"
	)
	parser.add_argument("-x", "--quantities", nargs="+",
		default=["LeptonPt", "LeptonEta"],
		help="Quantities. [Default: %(default)s]"
	)

	args = parser.parse_args()

	if not args.input_directory[-1] == "/":
		args.input_directory += "/"

	with open(args.plot_config) as config_file:
		plotConfig = json.load(config_file)

	with open(args.sample_config) as config_file:
		sampleConfigs = json.load(config_file)

	if (args.keys):
		events = uproot.open(args.input_directory + sampleConfigs[args.samples[0]]["samplename"][0])["nominal"]
		print(events.keys())
		exit();

	# Fill Histograms
	histPerSample = []
	for sample in args.samples:
		histPerQuantity = [bh.Histogram(bh.axis.Regular(plotConfig[quantity]["nBins"], plotConfig[quantity]["x_min"], plotConfig[quantity]["x_max"])) for quantity in args.quantities]
		if args.test_run:
			fileList = [sampleConfigs[sample]["samplename"][0]]
		else:
			fileList = sampleConfigs[sample]["samplename"]
		for fileName in fileList:
			xSection = GetXSection(fileName)
			if xSection == 0:
				continue
			luminosity = GetLuminosity(fileName)
			currentTree = uproot.open(args.input_directory + fileName + ":nominal")
			for quantity, hist in zip(args.quantities, histPerQuantity):
				currentQuantity = currentTree[quantity].array(library="ak")
				for cut, condition in plotConfig[quantity]["cutvariables"]:
					#currentCut = currentTree[cut].array(library="pd")
					currentCut = currentTree[re.sub("_[0-9]", "", cut)].array(library="ak")
					if re.search("_[1-9]", cut):
						indexOfInterest = int(cut[-1]) - 1
						currentCut = currentCut.mask[ak.num(currentCut) > indexOfInterest][:,indexOfInterest]
					# TODO Is there a more elegant way to convert strings into cuts?
					if (condition == "True"):
						currentQuantity.mask[currentCut]
					elif (condition[0:2] == ">="):
						currentQuantity.mask[currentCut >= int(condition[2:])]
					elif (condition[0:2] == "<="):
						currentQuantity.mask[currentCut <= int(condition[2:])]
					elif (condition[0] == ">"):
						currentQuantity.mask[currentCut > int(condition[1:])]
					elif (condition[0] == "<"):
						currentQuantity.mask[currentCut > int(condition[1:])]
					elif (condition[0:2] == "!="):
						currentQuantity.mask[currentCut != int(condition[2:])]
					elif (condition[0:2] == "=="):
						currentQuantity.mask[currentCut == int(condition[2:])]
					else:
						print("Check your plotConfig.json! The cut condition is improperly defined!")
						exit(-1)
				hist.fill(ak.flatten(currentQuantity))
			currentTree.close()
		histPerSample.append(histPerQuantity)

	# Create the plots
	for figureNumber, quantity in enumerate(args.quantities):
		plt.figure(figureNumber)
		for sampleNumber, sample in enumerate(args.samples):
			print(sample)
			hep.histplot(histPerSample[sampleNumber][figureNumber], label = sampleConfigs[sample]["label"], color = sampleConfigs[sample]["color"], histtype = sampleConfigs[sample]["histtype"], stack = sampleConfigs[sample]["isData"])
		hep.cms.label()
		plt.style.use(hep.style.CMS)
		plt.legend(fontsize = 12, ncol = 3)
		plt.xlabel(plotConfig[quantity]["label"])
		plt.ylabel(args.y_label)
		plt.savefig("websync/png/%s.png" % quantity)
		plt.savefig("websync/pdf/%s.pdf" % quantity)
		plt.yscale("log")
		plt.savefig("websync/png/%s_log.png" % quantity)
		plt.savefig("websync/pdf/%s_log.pdf" % quantity)
		#plt.close()

