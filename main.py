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


    def write_section(self, section_name):
        message = fr"\section{{{section_name}}}" + "\n\n"
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

    logger.write_section("Benvenuto")
    logger.write_message("Ciao a Ale.\n\n")
    logger.write_message("Questo è un Messaggio automatico", noindent=True)
    
    logger.close_document()

    logger.compile_into_pdf()