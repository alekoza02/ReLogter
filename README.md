# Some info

This project aims to help decorate Logs by merging them into a customazibale report in LaTeX. Add inside your code the desired `ReLogter` function and obtain at then end a report ready to be sent to your manager :D

Future ideas is to add a mailing system of the finished pdf as well as some optimizations to make the ReLogter as lightweight as possible inside the main program and easily commentable without breaking the whole thing.

# Usage

### Initialization
Initialize the ReLogter with this snippet:

```python
logger = ReLogter("output_file_name")
logger.initialize_document(use_default_packages=True)
```

### Available functions
Use the following functions to create your report in LaTeX:

```python
logger.write_title("Title", "Author")
logger.write_section("Section")
logger.write_message("Message")
logger.write_matrix(np.array([[0, 1], [1, 0]]))
logger.write_itemize(*elements)
logger.write_table(results) # results is a Dictionary
logger.write_plot(figure) # figure is a matplotlib.Figure
```

### Contexts
Use the contexts to create more complex impaginations:

- Minipages: 
    ```python
    ReLogter.minipage_context
    ```

### Contexts usage examples

```python
logger.minipage_context.set_width(0.45)
with logger.minipage_context:
    logger.write_message("Message in minipage 1")

logger.minipage_context.set_hfill()

logger.minipage_context.set_width(0.45)
with logger.minipage_context:
    logger.write_message("Message in minipage 2")
```

### Saving and compiling
When you are finished, save everything and if you have LaTeX installed, compile it!

```python
logger.close_document()
logger.compile_into_pdf()
```