import subprocess

class ReLogter:
    
    def __init__(self, file_name="output", compile=True, rm_garbage=True, live_update=False, show_errors=False):

        self.file_name = file_name
        self.compile = compile        
        self.rm_garbage = rm_garbage
        self.live_update = live_update
        self.show_errors = show_errors
        
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

        print(max_len_dictionary_elements)

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

        print(alignement)
        print(all_rows)

        message = "\n" + r"\begin{table}[!ht]" + "\n\t" + r"\centering" + resizing_start + "\n\t\t\t" + r"\begin{tabular}" + f"{{{alignement}}}" + "\n\t\t\t" + titles + all_rows + "\n\t\t\t" + "\n\t\t\t" + r"\end{tabular}%" + resizing_stop + "\n\t" + r"\caption{" + f"{caption}" + "}" + "\n" + r"\end{table}"
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


if __name__ == "__main__":
    
    logger = ReLogter("output", show_errors=True)
    
    logger.initialize_document(use_default_packages=True)

    logger.write_section("Report", numbered=1)
    logger.write_subsection("Timings", numbered=1)
    logger.write_subsubsection("Overview", numbered=1)
    logger.write_message("Here are reported the execution times of the code.\n")
    
    tabella = {
        r"\textbf{RUN}" : ["1", "2", "3"],
        r"\textbf{Dummy value A} [ms]" : ["30", "45", "17"],
        r"\textbf{Dummy value B} [ms]" : ["2320", "2540", "2023"],
        r"\textbf{Dummy value C} [ms]" : ["4", "7", "6"]
    }
    
    caption_tabella = "This is a Table Report"

    logger.write_table(tabella, caption_tabella, orientation_horizontal=0, fit_width=0)
    
    logger.close_document()

    logger.compile_into_pdf()