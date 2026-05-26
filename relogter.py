from concurrent.futures import thread
import subprocess
import threading
from copy import deepcopy
from pathlib import Path

import matplotlib
matplotlib.use("tkagg") # fast headless renderer
import matplotlib.pyplot as plt

plt.rcParams.update(
    {
        "text.usetex": True,  # Use LaTeX for all text
        "font.family": "serif",  # Use serif fonts (like in LaTeX)
        "text.latex.preamble": r"\usepackage{amsmath, amssymb}",  # Extra packages
        "path.simplify": True,
        "path.simplify_threshold": 1.0
    }
)


class ReLogter:
    def __init__(
        self,
        file_name="output",
        compile=True,
        rm_garbage=True,
        live_update=False,
        show_errors=False,
    ):

        self.file_name = file_name
        self.compile = compile
        self.rm_garbage = rm_garbage
        self.live_update = live_update
        self.show_errors = show_errors

        self.minipage_context = Minipage(self, 0.45)

        self.__output_string = ""
        self.rendering_threads = []

    def initialize_document(
        self, use_default_packages: bool, additional_packages: str = ""
    ):

        packages = self.add_packages(use_default_packages, additional_packages)

        message = (
            r"\documentclass{article}"
            + "\n\n"
            + packages
            + "\n"
            + r"\begin{document}"
            + "\n\n"
        )
        self.__update_buffer(message, file_open_mode="w")

    def add_packages(self, use_default_packages: bool, additional_packages: str = ""):

        packages = ""

        if additional_packages != "":
            packages = packages + additional_packages

        if use_default_packages:
            packages = (
                packages + "\n"
                r"\usepackage[a4paper,margin=2.5cm]{geometry}"
                + "\n"
                + r"\usepackage{caption}"
                + "\n"
                + r"\usepackage{hyperref}"
                + "\n"
                + r"\usepackage{graphicx}"
                + "\n"
                + r"\usepackage{float}"
                + "\n"
                + r"\usepackage{amsmath}"
                + "\n"
                + r"\usepackage{listings}"
                + "\n"
                + r"\usepackage[table]{xcolor}"
            )

        return packages

    def write_title(self, title: str, author: str, date: str | None = None):
        message = (
            rf"\title{{{title}}}"
            + "\n"
            + rf"\author{{{author}}}"
            + rf"\date{{{r'\today' if date is None else date}}}"
            + "\n\n"
            + r"\maketitle"
            + "\n\n"
            + r"\newpage"
            + "\n\n"
        )
        self.__update_buffer(message)


    def write_newpage(self):
        message = "\n\n" + r"\newpage" + "\n\n"
        self.__update_buffer(message)


    def write_message(self, message, noindent=False):
        if noindent:
            message = r"\noindent " + message
        self.__update_buffer(message)

    def write_section(self, section_name, numbered=True):
        message = rf"\section{'' if numbered else '*'}{{{section_name}}}" + "\n\n"
        self.__update_buffer(message)

    def write_subsection(self, subsection_name, numbered=True):
        message = rf"\subsection{'' if numbered else '*'}{{{subsection_name}}}" + "\n\n"
        self.__update_buffer(message)

    def write_subsubsection(self, subsubsection_name, numbered=True):
        message = (
            rf"\subsubsection{'' if numbered else '*'}{{{subsubsection_name}}}" + "\n\n"
        )
        self.__update_buffer(message)

    def write_table(
        self,
        dictionary: dict[str, float | int | str],
        caption: str,
        orientation_horizontal: bool = True,
        fit_width: bool = True,
        elements_alignement="auto",
    ):

        all_keys = dictionary.keys()
        all_values = list(dictionary.values())

        max_len_dictionary_elements = max([len(i) for i in all_values])  # pyright: ignore[reportArgumentType]

        if elements_alignement == "auto":
            if orientation_horizontal:
                alignement = "c|"
                alignement = alignement + "c" * max_len_dictionary_elements
            else:
                alignement = "c|" * len(dictionary)
                alignement = alignement[:-1]  # remove last "|"
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
                all_rows = (
                    all_rows
                    + "\n\t\t\t"
                    + key
                    + " & "
                    + " & ".join([str(i) for i in values])  # pyright: ignore[reportGeneralTypeIssues]
                    + r" \\"
                    + "\n\t\t\t"
                    + r"\hline"
                )
            all_rows = all_rows[:-14]

        else:
            titles = "\n\t\t\t" + " & ".join(all_keys) + r" \\" + "\n\t\t\t" + r"\hline"

            all_rows = ""

            for i in range(max_len_dictionary_elements):
                all_rows = (
                    all_rows
                    + "\n\t\t\t"
                    + " & ".join([str(dictionary[key][i]) for key in all_keys])  # pyright: ignore[reportIndexIssue]
                    + r" \\"
                )

        message = (
            "\n"
            + r"\begin{table}[!ht]"
            + "\n\t"
            + r"\centering"
            + resizing_start
            + "\n\t\t\t"
            + r"\begin{tabular}"
            + f"{{{alignement}}}"
            + "\n\t\t\t"
            + titles
            + all_rows
            + "\n\t\t\t"
            + "\n\t\t\t"
            + r"\end{tabular}%"
            + resizing_stop
            + "\n\t"
            + r"\caption{"
            + f"{caption}"
            + "}"
            + "\n"
            + r"\end{table}"
            + "\n"
        )
        self.__update_buffer(message)

    def write_matrix(self, array2D, transpose=False):
        
        if transpose:
            array2D = list(zip(*array2D))

        message = (
            "\n"
            + r"\["
            + r"\begin{pmatrix}"
            + r" \\ ".join([f"{' & '.join([f'{i}' for i in row])}" for row in array2D])
            + r"\end{pmatrix}"
            + r"\]"
            + "\n\n"
        )
        self.__update_buffer(message)

    def write_itemize(self, *elements):
        
        refined_elements = [element if type(element) == str else element.__repr__() for element in elements]
        refined_elements = [f"{{{element}}}" if type(element) == list else element for element in elements]

        message = (
            "\n"
            + r"\begin{itemize}"
            + "\n"
            + "".join(["\t" fr"\item {element}" "\n" for element in refined_elements])
            + r"\end{itemize}"
        )

        self.__update_buffer(message)

    def write_plot(
        self,
        fig: plt.Figure,  # pyright: ignore[reportPrivateImportUsage]
        centering: bool = True,
        caption: str = "",
        label: str = "",
        size: str | None = None,
        output_name: str = "plot",
        output_extension: str = "jpg",
        dpi: int = 300,
        multithread: bool = False,
        use_cached: bool = False
    ):

        # Ensure directory exists        
        folder = Path(self.file_name).parent

        dir_path = folder / "output_plots"
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


        if use_cached and len(numbers) > 0:
            plot_path_index = max(numbers)
            file_name = f"{output_name}_{plot_path_index}.{output_extension}"
            plt.close(fig)

        else:
            next_number = max(numbers, default=-1) + 1
            file_name = f"{output_name}_{next_number}.{output_extension}"
            plot_path = dir_path / file_name

            if multithread:
                safe_fig = deepcopy(fig)
                plt.close(fig)

                rendering_thread = threading.Thread(target=self._render_plot_thread, args=(safe_fig, plot_path, dpi)).start()
                self.rendering_threads.append(rendering_thread)
            else:
                fig.tight_layout()
                fig.savefig(plot_path, dpi=dpi)
                plt.close(fig)

        if size is None:
            size = r"width=\linewidth"

        message = (
            "\n"
            + r"\begin{figure}[H]"
            + "\n\t"
            + f"{r'\centering' if centering else ''}"
            + "\n\t\t"
            + rf"\includegraphics[{size}]{{{Path("output_plots", file_name).as_posix()}}}"
            + "\n\t\t"
            + rf"\caption{{{caption}}}"
            + "\n\t"
            + rf"\label{{fig:{label}}}"
            + "\n"
            + r"\end{figure}"
            + "\n\n"
        )
        self.__update_buffer(message)

    def _render_plot_thread(self, fig, plot_path, dpi):
        fig.tight_layout()
        fig.savefig(plot_path, dpi=dpi)
        plt.close(fig)

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

        for thread in self.rendering_threads:
            if not thread is None: 
                thread.join()

        mode = "nonstopmode" if self.show_errors else "batchmode"

        cmd = [
            "latexmk",
            "-pdf",
            "-halt-on-error",
            f"-interaction={mode}",
            f"{self.file_name}.tex",
        ]

        result = subprocess.run(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True
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
            check=True,
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
        self.document.write_message(
            rf"\begin{{minipage}}{{{self.width}\textwidth}}" + "\n"
        )
        return self

    def __exit__(self, exc_type, exc, tb):
        self.document.write_message("\n" + r"\end{minipage}" + "\n")
        return False
