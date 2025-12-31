import subprocess
import time

class ReLogter:
    
    def __init__(self, file_name="output", compile=True, rm_garbage=True, live_update=False):

        self.file_name = file_name
        self.compile = compile        
        self.rm_garbage = rm_garbage
        self.live_update = live_update
        
        self.__output_string = ""


    def initialize_document(self):
        if self.live_update:
            with open(f"{self.file_name}.tex", "w") as f:
                print(r"\documentclass{article}", "\n", r"\begin{document}", file=f)
        else:
            self.__output_string = self.__output_string + r"\documentclass{article}" + "\n" + r"\begin{document}" + "\n"


    def write_message(self, message):
        if self.live_update:
            with open(f"{self.file_name}.tex", "a") as f:
                print(fr"{message}", file=f)
        else:
            self.__output_string = self.__output_string + message + "\n"


    def close_document(self):
        if self.live_update:
            with open(f"{self.file_name}.tex", "a") as f:
                print(r"\end{document}", file=f)
        else:
            self.__output_string = self.__output_string + r"\end{document}"
            with open(f"{self.file_name}.tex", "w") as f:
                print(f"{self.__output_string}", file=f)


    def compile_into_pdf(self):
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", f"{self.file_name}.tex"],
            check=True
        )


    def remove_aux_file(self, additional_wait_time=5):
        time.sleep(additional_wait_time)
        subprocess.run(
            "rm -f *.log *.aux *.fdb_latexmk *.fls *.log *.gz",
            shell=True,
            check=True
        )


if __name__ == "__main__":
    
    logger1 = ReLogter("output_live", live_update=True)
    logger2 = ReLogter("output_no_live", live_update=False)

    logger1.initialize_document()
    logger1.write_message("Ciao a tutti.")
    logger1.write_message("Messaggio automatico")
    logger1.close_document()

    logger1.compile_into_pdf()
    logger1.remove_aux_file()


    logger2.initialize_document()
    time.sleep(5)
    logger2.write_message("Ciao a tutti.")
    time.sleep(5)
    logger2.write_message("Messaggio automatico")
    time.sleep(5)
    logger2.close_document()

    logger2.compile_into_pdf()
    logger2.remove_aux_file()