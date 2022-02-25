Uppaal Stratego Strategies Extractor
====================================

The repository contains a software tool to extract strategies generated through [Uppaal stratego][stratego] and convert
them into Probabilitic Timed Automata (PTA). The tool processes both pure [TIGA][tiga]-style strategies and TIGA
strategies optimized through Stratego. in [this article][paper2].

The tool returns the original [Uppaal][uppaal] model (i.e., a PTA network) with all *controllable* edges replaced with *
uncontrollable* ones with guard conditions calculated by the strategy.

**Note:** The tool has been tested on macOS 10.15.7 and Uppaal Stratego 9. Should you succeed in running the tool in a different
environment or run into any issue throughout the process, please reach out to the author.

Authors:

| Name              | E-mail address           |
|:----------------- |:-------------------------|
| Lestingi Livia    | livia.lestingi@polimi.it |

Configuration File Setup
-----------

The tool requires a [configuration file](resources/config/config.ini) whose content must be adjusted to match your
environment.
Make sure that the following properties match your environment:

- **MODEL_PATH** is the path to the original Uppaal Stratego .xml model file

Python Dependencies
-----------

Install the required dependencies:

	pip install -r $REPO_PATH/requirements.txt

Add the repo path to your Python path (fixes ModuleNotFoundError while trying to execute from command line):

	export PYTHONPATH="${PYTHONPATH}:$REPO_PATH"

Main Script's Input Parameters
-----------

Run the main script specifying: 
- the name of the TIGA strategy to convert (e.g., [gosafe](resources/strategies/gosafe.txt))
- the name of the optimized strategy that refines the first one (e.g., [gofastsafe](resources/strategies/gofastsafe.json))
- the name of the original .xml Uppaal file

	python3 $REPO_PATH/it/polimi/strategyviz/main.py $TIGA_STRATEGY $OPT_STRATEGY $MODEL

---

*Copyright &copy; 2022 Livia Lestingi*

[paper1]: https://doi.org/10.4204/EPTCS.319.2

[paper2]: https://doi.org/10.1007/978-3-030-58768-0_17

[paper3]: https://doi.org/10.1109/SMC42975.2020.9283204

[paper4]: https://doi.org/10.1109/ACCESS.2021.3117852

[uppaal]: https://uppaal.org/

[stratego]: https://people.cs.aau.dk/~marius/stratego/

[tiga]: https://uppaal.org/features/#tiga