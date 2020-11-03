import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import uproot4 as uproot
import boost_histogram as bh
import mplhep as hep
import pandas as pd

import json


import argparse

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
		default=["integral", "LeptonPt", "LeptonEta"],
		help="Quantities. [Default: %(default)s]"
	)

	args = parser.parse_args()

	if not args.input_directory[-1] == "/":
		args.input_directory += "/"

	if (args.keys):
		events = uproot.open(args.input_directory + sampleConfigs[args.samples[0]]["samplename"])["nominal"]
		print(events.keys())
		exit();

	with open(args.plot_config) as config_file:
		plotConfig = json.load(config_file)

	with open(args.sample_config) as config_file:
		sampleConfigs = json.load(config_file)

	for quantity in args.quantities:
		currentConfig = plotConfig[quantity]
		for sample in args.samples:
			hist = bh.Histogram(bh.axis.Regular(currentConfig["nBins"], currentConfig["x_min"], currentConfig["x_max"]))
			for fileName in sampleConfigs[sample]["samplename"]:
				currentFile = uproot.open(args.input_directory + fileName)
				currentTree = currentFile["nominal"]
				currentQuantity = currentTree[quantity].array(library="pd")
				hist.fill(currentQuantity)
				currentTree.close()
				currentFile.close()
			#eventTrees = [uproot.open(args.input_directory + sampleConfig)["nominal"] for sampleConfig in sampleConfigs[sample]["samplename"]]
			#currentQuantityArray = [tree[quantity].array(library="pd") for tree in eventTrees]
			#currentQuantity = pd.concat(currentQuantityArray)
			#hist.fill(currentQuantity)
			hep.histplot(hist, label = sampleConfigs[sample]["label"], color = sampleConfigs[sample]["color"], histtype = sampleConfigs[sample]["histtype"], stack = sampleConfigs[sample]["isData"])
		hep.cms.label()
		plt.style.use(hep.style.CMS)
		plt.legend()
		plt.xlabel(currentConfig["label"])
		plt.ylabel(args.y_label)
		plt.savefig("websync/png/%s.png" % quantity)
		plt.savefig("websync/pdf/%s.pdf" % quantity)
		plt.close()

