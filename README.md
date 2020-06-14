# The Experiment:

This experiment was developed to study dynamic decision making. How do people navigate the decision-making process when context and task demands change. It involves learning to sort circles with lines (sine-wave gratings) into 2 categories. Throughout the experiment things change and you'll need to adapt.

The Python version of the experiment also includes a cognitive computational model (PINNACLE 2.0) and an adaptive stimulus selection algorithm that act as an intelligent tutor to try and guide you to the correct answer. The JS version requires quite a bit more infrastructure to get running and so the included files are for code demonstration purposes.

The output of the experiment will be a data file found in ./data/ which you can analyze by calculating the average accuracy (7th column) over blocks of 80 trials. It will also produce a modeling trace in the PINNACLE_files for further modeling use.

# Python code

To run the Python experiment:
1) Download the "Dynamic Cat" folder and within the input/Stims directory unzip Stims.zip. 
2) This code was written for PsychoPy version 1.85.6 which can be downloaded and installed from here: https://github.com/psychopy/psychopy/releases/tag/1.85.6 (other versions might work, but to ensure full compatability, please use that.)
3) When you launch PsychoPy it will likely open into "Builder View". Click "View: Open Coder View". 
4) Open Dynamic_Cat.py and run the file.
