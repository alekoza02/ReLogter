import subprocess
import matplotlib.pyplot as plt
from pathlib import Path

plt.rcParams.update({
    "text.usetex": True,            # Use LaTeX for all text
    "font.family": "serif",         # Use serif fonts (like in LaTeX)
    "text.latex.preamble": r"\usepackage{amsmath, amssymb}"  # Extra packages
})

class ReLogter:
    
    def __init__(self, file_name="output", compile=True, rm_garbage=True, live_update=False, show_errors=False):

        self.file_name = file_name
        self.compile = compile        
        self.rm_garbage = rm_garbage
        self.live_update = live_update
        self.show_errors = show_errors

        self.minipage_context = Minipage(self, 0.45)
        
        self.__output_string = ""


    def initialize_document(self, use_default_packages: bool, additional_packages: str = ""):

        packages = self.add_packages(use_default_packages, additional_packages)

        message = r"\documentclass{article}" + "\n\n" + packages + "\n" + r"\begin{document}" + "\n\n"
        self.__update_buffer(message, file_open_mode="w")


    def add_packages(self, use_default_packages: bool, additional_packages: str = ""):

        packages = ""
        
        if additional_packages != "":
            packages = packages + additional_packages
        
        if use_default_packages:
            packages = packages + "\n" r'\usepackage[a4paper,margin=2.5cm]{geometry}' + "\n" + r'\usepackage{caption}' + "\n" + r'\usepackage{hyperref}' + "\n" + r'\usepackage{graphicx}' + "\n" + r'\usepackage{float}' + "\n" + r'\usepackage{amsmath}' + "\n" + r'\usepackage{listings}' + "\n" + r'\usepackage[table]{xcolor}'

        return packages


    def write_title(self, title: str, author: str, date: str = None):
        message = fr"\title{{{title}}}" + "\n" + fr"\author{{{author}}}" + fr"\date{{{r"\today" if date is None else date}}}" + "\n\n" + r"\maketitle" + "\n\n" + r"\newpage" + "\n\n"
        self.__update_buffer(message)


    def write_message(self, message, noindent=False):
        if noindent:
            message = r"\noindent " + message
        self.__update_buffer(message)


    def write_section(self, section_name, numbered=True):
        message = fr"\section{"" if numbered else "*"}{{{section_name}}}" + "\n\n"
        self.__update_buffer(message)
    
    
    def write_subsection(self, subsection_name, numbered=True):
        message = fr"\subsection{"" if numbered else "*"}{{{subsection_name}}}" + "\n\n"
        self.__update_buffer(message)
    
    
    def write_subsubsection(self, subsubsection_name, numbered=True):
        message = fr"\subsubsection{"" if numbered else "*"}{{{subsubsection_name}}}" + "\n\n"
        self.__update_buffer(message)


    def write_table(self, dictionary: dict[str, float | int | str], caption: str, orientation_horizontal: bool = 1, fit_width: bool = 1, elements_alignement='auto'):
        
        all_keys = dictionary.keys()
        all_values = list(dictionary.values())
        
        max_len_dictionary_elements = max([len(i) for i in all_values])

        if elements_alignement == 'auto':
            if orientation_horizontal:
                alignement = "c|"
                print(alignement)
                alignement = alignement + "c" * max_len_dictionary_elements
                print(alignement)
            else:
                alignement = "c|" * len(dictionary)
                alignement = alignement[:-1] # remove last "|" 
        else:
            alignement = elements_alignement


        if fit_width:
            resizing_start = "\n\t\t" + r"\resizebox{\textwidth}{!}{%"
            resizing_stop = "\n\t\t" + "}"
        else:
            resizing_start = ""
            resizing_stop = ""


        if orientation_horizontal:
            titles = ""

            all_rows = ""
            for key, values in dictionary.items():
                all_rows = all_rows + "\n\t\t\t" + key + " & " + " & ".join([str(i) for i in values]) + r" \\" + "\n\t\t\t" + r"\hline"
            all_rows = all_rows[:-14]

        else:
            titles = "\n\t\t\t" + " & ".join(all_keys) + r" \\" + "\n\t\t\t" + r"\hline"
            
            all_rows = ""

            for i in range(max_len_dictionary_elements):
                all_rows = all_rows + "\n\t\t\t" + " & ".join([str(dictionary[key][i]) for key in all_keys]) + r" \\"


        message = "\n" + r"\begin{table}[!ht]" + "\n\t" + r"\centering" + resizing_start + "\n\t\t\t" + r"\begin{tabular}" + f"{{{alignement}}}" + "\n\t\t\t" + titles + all_rows + "\n\t\t\t" + "\n\t\t\t" + r"\end{tabular}%" + resizing_stop + "\n\t" + r"\caption{" + f"{caption}" + "}" + "\n" + r"\end{table}" + "\n"
        self.__update_buffer(message)


    def write_plot(self, fig: plt.Figure, centering: bool = True, caption: str = "", label: str = "", size: str = None, output_name: str = "plot", output_extension: str = "jpg"):
        
        # Ensure directory exists
        dir_path = Path("./output_plots")
        dir_path.mkdir(parents=True, exist_ok=True)

        # Find existing files with the same base name
        existing_files = list(dir_path.glob(f"{output_name}*{output_extension}"))

        # Determine the next available number
        numbers = []
        for f in existing_files:
            stem = f.stem  # file name without extension
            if stem == output_name:
                numbers.append(0)
            elif stem.startswith(f"{output_name}_"):
                try:
                    num = int(stem.split("_")[-1])
                    numbers.append(num)
                except ValueError:
                    pass

        next_number = max(numbers, default=-1) + 1
        file_name = f"{output_name}_{next_number}.{output_extension}"
        plot_path = dir_path / file_name

        fig.tight_layout()
        fig.savefig(plot_path, dpi=300)

        if size is None:
            size = r"width=\linewidth"

        message = "\n" + r"\begin{figure}[H]" + "\n\t" + f"{r'\centering' if centering else ''}" + "\n\t\t" + fr"\includegraphics[{size}]{{{plot_path}}}" + "\n\t\t" + fr"\caption{{{caption}}}" + "\n\t" + fr"\label{{fig:{label}}}" + "\n" + r"\end{figure}" + "\n\n"
        self.__update_buffer(message)


    def close_document(self):
        message = "\n\n" + r"\end{document}"
        self.__update_buffer(message)
        
        if not self.live_update:
            with open(f"{self.file_name}.tex", "w") as f:
                print(f"{self.__output_string}", file=f)


    def __update_buffer(self, message, file_open_mode="a"):
        if self.live_update:
            with open(f"{self.file_name}.tex", file_open_mode) as f:
                print(f"{message}", file=f, end="")
        else:
            self.__output_string = self.__output_string + message


    def compile_into_pdf(self):
        mode = "nonstopmode" if self.show_errors else "batchmode"

        cmd = [
            "latexmk",
            "-pdf",
            "-halt-on-error",
            f"-interaction={mode}",
            f"{self.file_name}.tex",
        ]

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if self.show_errors:
            print(result.stdout)
            print(result.stderr)

        if result.returncode != 0:
            raise RuntimeError("LaTeX compilation failed")

        subprocess.run(
            ["latexmk", "-c"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )



class Minipage:
    def __init__(self, document: ReLogter, width):
        self.document = document
        self.set_width(width)


    def set_width(self, width):
        self.width = width


    def set_hfill(self):
        self.document.write_message(r"\hfill" + "\n")


    def __enter__(self):
        self.document.write_message(rf"\begin{{minipage}}{{{self.width}\textwidth}}" + "\n")
        return self

    def __exit__(self, exc_type, exc, tb):
        self.document.write_message("\n" + r"\end{minipage}" + "\n")
        return False



#######################################################################################################################################################
#######################################################################################################################################################
#######################################################################################################################################################
##
## EXAMPLE
##
#######################################################################################################################################################
#######################################################################################################################################################
#######################################################################################################################################################



if __name__ == "__main__":
    
    logger = ReLogter("output", show_errors=True)
    
    logger.initialize_document(use_default_packages=True)

    logger.write_title("Randomness comparison Python vs NumPy", "Alekoza02")
    logger.write_section("Introduction", numbered=True)
    logger.write_message("In this report, we will analyze the effeciency and speed up we can obtain by using the NumPy library. We should notice that NumPy is a compiled and vectorized library, meaning it will be much faster for big samples, but what about small samples and the overhead introduced by the function call? Let's find out...")
    logger.write_section("Timings", numbered=True)

    results = {}
    results["N samples"] = [1, 2, 5, 10, 20, 500, 1000, 2000, 5000, 10000, 20000]
    results["Python [us]"] = []
    results["NumPy [us]"] = []
    
    results2 = {}
    results2["Python data"] = []
    results2["NumPy data"] = []
    
    from time import perf_counter_ns
    import numpy as np
    import random

    # dummy warm up
    np.random.random()

    for n_samples in results["N samples"]:
        start_python = perf_counter_ns()
        results_python = []
        for i in range(n_samples):
            results_python.append(random.random())
        stop_python = perf_counter_ns()
        results2["Python data"].append(results_python)

        start_numpy = perf_counter_ns()
        results_numpy = np.random.random(n_samples)
        stop_numpy = perf_counter_ns()
        results2["NumPy data"].append(results_numpy)

        results["Python [us]"].append((stop_python - start_python) / 1000)    
        results["NumPy [us]"].append((stop_numpy - start_numpy) / 1000)    

    logger.write_table(results, "Timings for classic Python (random library) vs NumPy broadcasted function", orientation_horizontal=0, fit_width=0)

    logger.write_section("Plots", numbered=True)
        
    logger.write_message("For this experiment, NumPy has a dummy `warm up' calculation.")

    fig, ax = plt.subplots(2, 1)

    ax[0].plot([str(sample) for sample in results["N samples"][5:]], results["Python [us]"][5:], color='blue', label='Python')
    ax[0].plot([str(sample) for sample in results["N samples"][5:]], results["NumPy [us]"][5:], color='red', label='NumPy')

    ax[0].tick_params(axis='both', which='major', labelsize=14)

    ax[0].set_xlabel("Samples size", fontsize=18)
    ax[0].set_ylabel(r"Timings [$\mu$s]", fontsize=18)

    ax[0].legend(fontsize=14)
    
    ax[1].plot([str(sample) for sample in results["N samples"][:5]], results["Python [us]"][:5], color='blue', label='Python')
    ax[1].plot([str(sample) for sample in results["N samples"][:5]], results["NumPy [us]"][:5], color='red', label='NumPy')

    ax[1].tick_params(axis='both', which='major', labelsize=14)

    ax[1].set_xlabel("Samples size", fontsize=18)
    ax[1].set_ylabel(r"Timings [$\mu$s]", fontsize=18)

    ax[1].legend(fontsize=14)

    logger.write_plot(fig, caption="Visualizing timings of the two algorithms. Smaller values are better. a) Shows how Python loses on big samples. b) Shows how even if NumPy has a non-negligible overhead, it is blazingly fast.", size=r"width=0.8\linewidth", label="a")

    logger.write_section("Randomness distribution")

    logger.minipage_context.set_width(0.35)

    with logger.minipage_context:
        logger.write_message("It may also be interesting to visualize the randomicity of these libraries, who knows: maybe NumPy is faster, but with a poor distribution. This is why we'll try different sample sizes and test which one is actually more randomic at different sizes. Moreover, the way randomness is generated internally can vary significantly between libraries. Some may rely on deterministic algorithms that are fast but exhibit patterns over large sequences, while others might prioritize statistical quality over speed.")
    
    logger.minipage_context.set_hfill()

    logger.minipage_context.set_width(0.6)
    with logger.minipage_context:

        fig, ax = plt.subplots(2, 1)

        ax[0].plot([i + 1 for i in range(20)], results2["Python data"][4], color='blue', label='Python')
        ax[0].plot([i + 1 for i in range(20)], results2["NumPy data"][4], color='red', label='NumPy')

        ax[0].tick_params(axis='both', which='major', labelsize=14)

        ax[0].set_xlabel("Samples", fontsize=18)
        ax[0].set_ylabel(r"Random value", fontsize=18)

        ax[0].legend(fontsize=14)
        
        ax[1].plot([i + 1 for i in range(500)], results2["Python data"][5], color='blue', label='Python')
        ax[1].plot([i + 1 for i in range(500)], results2["NumPy data"][5], color='red', label='NumPy')
        
        ax[1].tick_params(axis='both', which='major', labelsize=14)

        ax[1].set_xlabel("Samples size", fontsize=18)
        ax[1].set_ylabel(r"Timings [$\mu$s]", fontsize=18)

        ax[1].legend(fontsize=14)

        logger.write_plot(fig, caption="Here we can see the distribution at a) 20 samples and b) 500 samples. They look randomic!", size=r"width=0.8\linewidth", label="b")

    logger.close_document()

    logger.compile_into_pdf()