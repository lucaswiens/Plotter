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
	parser.add_argument("-i", "--input-file",
		required = True,
		help = "Path to the file containing Histograms."
	)
	parser.add_argument("-o", "--output-directory",
		default = "hostudy/" + date,
		help = "Path to the output directory to store the plots."
	)
	parser.add_argument("--y-label",
		default = "Events",
		help = "Label of the y-axis"
	)
	parser.add_argument("--plot-config",
		default = cmsswBase + "/src/Plotting/Plotter/data/config/histConfig.json",
		help = "Path to the json file used to create plots: %(default)s"
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
		default = 1,
		help = "Set the filetypes of the output: %(default)s"
	)

	args = parser.parse_args()

	if not os.path.exists(args.output_directory):
		os.makedirs(args.output_directory)

	with open(args.plot_config) as config_file:
		histConfig = json.load(config_file)

	histograms = uproot.open(args.input_file)

	# Create the plots
	for figureNumber, key in enumerate(histograms.keys()):
		plt.figure(figureNumber)
		plt.ylabel(hitogramConfig[key]["ylabel"])
		plt.style.use(hep.style.CMS)
		hep.cms.label(ax = axs[0])
		plt.xlabel(histConfig[key]["label"])

		hep.histplot(histograms[key], label = hitogramConfig[key]["xlabel"], color = histConfig[key]["color"], histtype = histConfig[key]["histtype"])
		#hep.histplot(histPerSample[sampleNumber][figureNumber], label = sampleConfigs[sample]["label"], color = sampleConfigs[sample]["color"], histtype = sampleConfigs[sample]["histtype"], stack = not isData)

		#plt.legend(fontsize = args.font_size, ncol = args.number_of_cols)

		plt.savefig(args.output_directory + "/" + key + ".png")
		plt.savefig(args.output_directory + "/" + key + ".pdf")

		plt.savefig(args.output_directory + "/" + key + "_log.png")
		plt.savefig(args.output_directory + "/" + key + "_log.pdf")

		plt.close()

	common.CreateIndexHtml(templateDir = cmsswBase + "/src/Plotting/Plotter/data/html", outputDir = args.output_directory, fileTypes = args.file_types)

	plottingUrl = common.GetOSVariable("PLOTTING_URL")
	print(plottingUrl + "/" + args.output_directory)

