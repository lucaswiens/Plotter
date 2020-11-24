import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import awkward1 as ak
import boost_histogram as bh
import mplhep as hep
import uproot4 as uproot

import argparse
import json
import os
import re
import subprocess

import common

if __name__ == "__main__":
	date = subprocess.check_output("date +\"%Y_%m_%d\"", shell=True).decode("utf-8").replace("\n", "")
	cmsswBase = common.GetOSVariable("CMSSW_BASE")

	parser = argparse.ArgumentParser(description = "Creates plots from flat ntuples, requires config files in JSON format.", formatter_class = argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument("-i", "--input-directory",
		required = True,
		help = "Path to the file containing a list of samples."
	)
	parser.add_argument("-o", "--output-directory",
		default = "plots/" + date,
		help = "Path to the output directory to store the plots."
	)
	parser.add_argument("--keys",
		help = "Prints keys of the root files inside the input directory",
		default = False,
		action = "store_true"
	)
	parser.add_argument("--test-run",
		default = False,
		action = "store_true",
		help = "Use only the first file for each sample for a quick run"
	)
	parser.add_argument("--y-label",
		default = "Events",
		help = "Label of the y-axis"
	)
	parser.add_argument("--plot-config",
		default = cmsswBase + "/src/Plotting/Plotter/data/config/plotConfig.json",
		help = "Path to the json file used to create plots: %(default)s"
	)
	parser.add_argument("--sample-config",
		default = cmsswBase + "/src/Plotting/Plotter/data/config/sampleConfigs.json",
		help = "Path to the json file containing the filenames of the samples: %(default)s"
	)
	parser.add_argument("-s", "--samples",
		nargs = "+",
		#default = ["zll", "ttv", "vv", "qcd", "ttbarll", "singletop", "wjets", "ttbarl"],
		default = ["ttbarl", "wjets", "singletop", "ttbarll", "qcd", "ttv", "vv", "zll", "data"],
		help = "Samples. [Default: %(default)s]"
	)
	parser.add_argument("-x", "--quantities",
		nargs = "+",
		required = True,
		#default = ["LeptonPt", "LeptonEta"],
		help = "Quantities. [Default: %(default)s]"
	)
	parser.add_argument("-dpi", "--dots-per-inch",
		default = 120,
		help = "Set the dpi of the plot: %(default)s"
	)
	parser.add_argument("--width",
		default = 600,
		help = "Set the width of the plot: %(default)s"
	)
	parser.add_argument("--height",
		default = 400,
		help = "Set the height of the plot: %(default)s"
	)
	parser.add_argument("--file-types",
		nargs = "+",
		default = ["png", "pdf"],
		help = "Set the filetypes of the output: %(default)s"
	)
	parser.add_argument("--font-size",
		default = 18,
		help = "Set the filetypes of the output: %(default)s"
	)
	parser.add_argument("--number-of-cols",
		default = 3,
		help = "Set the filetypes of the output: %(default)s"
	)
	parser.add_argument("--unblind",
		default = False,
		action = "store_true",
		help = "Will only plot data if you want to unblind: %(defualt)s"
	)

	args = parser.parse_args()

	if not args.input_directory[-1] == "/":
		args.input_directory += "/"

	if not os.path.exists(args.output_directory):
		os.makedirs(args.output_directory)

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
	nSamples = len(args.samples)
	nQuantities = len(args.quantities)
	if not args.unblind and "data" in args.samples:
		args.samples.remove("data")
	for sampleIndex, sample in enumerate(args.samples):
		isData = True if sampleConfigs[sample]["isData"] == "True" else False

		histPerQuantity = [bh.Histogram(bh.axis.Regular(plotConfig[quantity]["nBins"], plotConfig[quantity]["x_min"], plotConfig[quantity]["x_max"])) for quantity in args.quantities]

		if args.test_run:
			fileList = [sampleConfigs[sample]["samplename"][0]]
		else:
			fileList = sampleConfigs[sample]["samplename"]

		nFiles = len(fileList)
		nEvents = 0
		for fileIndex, fileName in enumerate(fileList):
			xSection = common.GetXSection(fileName)
			if xSection == 0:
				continue
			luminosity = common.GetLuminosity(fileName)

			histPerFile = [bh.Histogram(bh.axis.Regular(plotConfig[quantity]["nBins"], plotConfig[quantity]["x_min"], plotConfig[quantity]["x_max"])) for quantity in args.quantities]
			currentTree = uproot.open(args.input_directory + fileName + ":nominal")
			quantityIndex = 0
			for quantity, hist, finalHist in zip(args.quantities, histPerFile, histPerQuantity):
				common.progressBar(nSamples, nFiles, nQuantities, sampleIndex, fileIndex, quantityIndex, quantity)
				quantityIndex += 1

				currentQuantity = currentTree[re.sub("_[0-9]", "", quantity)].array(library="ak")
				if re.search("_[1-9]", quantity):
					indexOfInterest = int(quantity[-1]) - 1
					currentQuantity = currentQuantity.mask[ak.num(currentQuantity) > indexOfInterest][:,indexOfInterest]

				weightStrings = plotConfig[quantity]["weight"].replace(" ", "").replace("\t", "").split("*")
				currentWeight = currentQuantity / currentQuantity
				for weight in weightStrings:
					if isData:
						continue
					tmpWeight = currentTree[re.sub("_[0-9]", "", weight)].array(library="ak")
					if re.search("_[1-9]", weight):
						indexOfInterest = int(weight[-1]) - 1
						currentWeight = currentWeight * tmpWeight.mask[ak.num(tmpWeight) > indexOfInterest][:,indexOfInterest]
					else:
						currentWeight = currentWeight * tmpWeight


				for cut, condition in plotConfig[quantity]["cutvariables"]:
					cut = cut.replace(" ", "").replace("\t", "")
					currentCut = currentTree[re.sub("_[0-9]", "", cut)].array(library="ak")
					if re.search("_[1-9]", cut):
						indexOfInterest = int(cut[-1]) - 1
						currentCut = currentCut.mask[ak.num(currentCut) > indexOfInterest][:,indexOfInterest]
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
				if isinstance(currentQuantity[0], ak.highlevel.Array):
					if isData:
						hist.fill(ak.flatten(currentQuantity))
					else:
						print(currentWeight)
						hist.fill(ak.flatten(currentQuantity), weight=ak.flatten(currentWeight))
						nEvents += hist.sum()
						hist = hist * xSection * luminosity
				else:
					if isData:
						hist.fill(currentQuantity[~ak.is_none(currentQuantity)])
					else:
						hist.fill(currentQuantity[~ak.is_none(currentQuantity)], weight=currentWeight[~ak.is_none(currentQuantity)])
						nEvents += hist.sum()
						hist = hist * xSection * luminosity
				finalHist += hist
			currentTree.close()
		if args.unblind and "data" in args.samples:
			histPerSample.append([hist / nEvents for hist in histPerQuantity[:-1]] + [histPerQuantity[-1]])
		else:
			histPerSample.append([hist / nEvents for hist in histPerQuantity])

	# Create the plots
	if args.unblind and "data" in args.samples:
		mcHist   = [bh.Histogram(bh.axis.Regular(plotConfig[quantity]["nBins"], plotConfig[quantity]["x_min"], plotConfig[quantity]["x_max"])) for quantity in args.quantities]
		dataHist = [bh.Histogram(bh.axis.Regular(plotConfig[quantity]["nBins"], plotConfig[quantity]["x_min"], plotConfig[quantity]["x_max"])) for quantity in args.quantities]

	for figureNumber, quantity in enumerate(args.quantities):
		#plt.figure(figureNumber)
		if args.unblind and "data" in args.samples:
			fig, axs = plt.subplots(2,1, figsize=(10, 10), sharex = True, gridspec_kw={'height_ratios': [3, 1]})
			axs[0].set_ylabel(args.y_label)
		else:
			fig = plt.figure()
			plt.ylabel(args.y_label)

		plt.style.use(hep.style.CMS)
		hep.cms.label(ax = axs[0])
		plt.xlabel(plotConfig[quantity]["label"], ha = "left")

		for sampleNumber, sample in enumerate(args.samples):
			isData = True if sampleConfigs[sample]["isData"] == "True" else False
			if args.unblind:
				if isData:
					dataHist[figureNumber] += histPerSample[sampleNumber][figureNumber]
				else:
					mcHist[figureNumber] += histPerSample[sampleNumber][figureNumber]

				hep.histplot(histPerSample[sampleNumber][figureNumber], label = sampleConfigs[sample]["label"], color = sampleConfigs[sample]["color"], histtype = sampleConfigs[sample]["histtype"], stack = not isData, ax = axs[0])
			else:
				hep.histplot(histPerSample[sampleNumber][figureNumber], label = sampleConfigs[sample]["label"], color = sampleConfigs[sample]["color"], histtype = sampleConfigs[sample]["histtype"], stack = not isData)

		if args.unblind and "data" in args.samples:
			hep.histplot(dataHist[figureNumber] / mcHist[figureNumber], color = sampleConfigs[sample]["color"], histtype = sampleConfigs[sample]["histtype"], stack = not isData, ax = axs[1])

		if args.unblind and "data" in args.samples:
			axs[0].legend(fontsize = args.font_size, ncol = args.number_of_cols)
		else:
			plt.legend(fontsize = args.font_size, ncol = args.number_of_cols)

		plt.savefig(args.output_directory + "/" + quantity + ".png")
		plt.savefig(args.output_directory + "/" + quantity + ".pdf")

		if args.unblind and "data" in args.samples:
			axs[0].set_yscale("log")
			axs[1].set_yscale("linear")
		else:
			plt.yscale("log")
		#plt.yscale("log")
		plt.savefig(args.output_directory + "/" + quantity + "_log.png")
		plt.savefig(args.output_directory + "/" + quantity + "_log.pdf")

		plt.close()

	common.CreateIndexHtml(templateDir = cmsswBase + "/src/Plotting/Plotter/data/html", outputDir = args.output_directory, fileTypes = args.file_types)

	plottingUrl = common.GetOSVariable("PLOTTING_URL")
	print(plottingUrl + "/" + args.output_directory)

