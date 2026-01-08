import subprocess

class ReLogter:
    
    def __init__(self, file_name="output", compile=True, rm_garbage=True, live_update=False, show_errors=False):

        self.file_name = file_name
        self.compile = compile        
        self.rm_garbage = rm_garbage
        self.live_update = live_update
        self.show_errors = show_errors
        
        self.__output_string = ""


    def initialize_document(self):
        message = r"\documentclass{article}" + "\n" + r"\begin{document}" + "\n"
        self.__update_buffer(message, file_open_mode="w")


    def write_message(self, message, noindent=False):
        if noindent:
            message = r"\noindent " + message
        self.__update_buffer(message)


    def write_section(self, section_name):
        message = fr"\section{{{section_name}}}"
        self.__update_buffer(message)


    def close_document(self):
        message = r"\end{document}"
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
        mode = "-interaction=nonstopmode" if self.show_errors else "-interaction=batchmode"

        result = subprocess.run(
            ["pdflatex", "-halt-on-error", mode, f"{self.file_name}.tex"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if self.show_errors:
            print(result.stdout)
            print(result.stderr)

        subprocess.run(
            ["latexmk", "-c", "-silent"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )


if __name__ == "__main__":
    
    logger = ReLogter("log", show_errors=True)
    
    logger.initialize_document()
    logger.write_section("Benvenuto")
    logger.write_message("Ciao a Ale.\n\n")
    logger.write_message("Questo è un Messaggio automatico", noindent=True)
    logger.close_document()

    logger.compile_into_pdf()