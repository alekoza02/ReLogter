if __name__ == "__main__":
    
    from relogter import ReLogter
    import matplotlib.pyplot as plt

    logger = ReLogter("output", show_errors=True)

    logger.initialize_document(use_default_packages=True)

    logger.write_title("Randomness comparison Python vs NumPy", "Alekoza02")
    logger.write_section("Introduction", numbered=True)
    logger.write_message(
        "In this report, we will analyze the effeciency and speed up we can obtain by using the NumPy library. We should notice that NumPy is a compiled and vectorized library, meaning it will be much faster for big samples, but what about small samples and the overhead introduced by the function call? Let's find out..."
    )
    logger.write_section("Timings", numbered=True)

    results: dict[str, list[int | float | list[int | float]]] = {}
    results["N samples"] = [1, 2, 5, 10, 20, 500, 1000, 2000, 5000, 10000, 20000]
    results["Python [us]"] = []
    results["NumPy [us]"] = []

    results2: dict[str, list[int | float | list[int | float]]] = {}
    results2["Python data"] = []
    results2["NumPy data"] = []

    import random
    from time import perf_counter_ns

    import numpy as np

    # dummy warm up
    np.random.random()

    for n_samples in results["N samples"]:
        start_python = perf_counter_ns()
        results_python = []
        for i in range(n_samples):  # pyright: ignore[reportArgumentType]
            results_python.append(random.random())
        stop_python = perf_counter_ns()
        results2["Python data"].append(results_python)

        start_numpy = perf_counter_ns()
        results_numpy = np.random.random(n_samples)  # pyright: ignore[reportCallIssue, reportArgumentType]
        stop_numpy = perf_counter_ns()
        results2["NumPy data"].append(results_numpy)

        results["Python [us]"].append((stop_python - start_python) / 1000)
        results["NumPy [us]"].append((stop_numpy - start_numpy) / 1000)

    logger.write_table(
        results,  # pyright: ignore[reportArgumentType]
        "Timings for classic Python (random library) vs NumPy broadcasted function",
        orientation_horizontal=False,
        fit_width=False,
    )

    logger.write_section("Plots", numbered=True)

    logger.write_message(
        "For this experiment, NumPy has a dummy `warm up' calculation."
    )

    fig, ax = plt.subplots(2, 1)

    ax[0].plot(
        [str(sample) for sample in results["N samples"][5:]],
        results["Python [us]"][5:],
        color="blue",
        label="Python",
    )
    ax[0].plot(
        [str(sample) for sample in results["N samples"][5:]],
        results["NumPy [us]"][5:],
        color="red",
        label="NumPy",
    )

    ax[0].tick_params(axis="both", which="major", labelsize=14)

    ax[0].set_xlabel("Samples size", fontsize=18)
    ax[0].set_ylabel(r"Timings [$\mu$s]", fontsize=18)

    ax[0].legend(fontsize=14)

    ax[1].plot(
        [str(sample) for sample in results["N samples"][:5]],
        results["Python [us]"][:5],
        color="blue",
        label="Python",
    )
    ax[1].plot(
        [str(sample) for sample in results["N samples"][:5]],
        results["NumPy [us]"][:5],
        color="red",
        label="NumPy",
    )

    ax[1].tick_params(axis="both", which="major", labelsize=14)

    ax[1].set_xlabel("Samples size", fontsize=18)
    ax[1].set_ylabel(r"Timings [$\mu$s]", fontsize=18)

    ax[1].legend(fontsize=14)

    logger.write_plot(
        fig,
        caption="Visualizing timings of the two algorithms. Smaller values are better. a) Shows how Python loses on big samples. b) Shows how even if NumPy has a non-negligible overhead, it is blazingly fast.",
        size=r"width=0.8\linewidth",
        label="a",
    )

    logger.write_section("Randomness distribution")

    logger.minipage_context.set_width(0.35)

    with logger.minipage_context:
        logger.write_message(
            "It may also be interesting to visualize the randomicity of these libraries, who knows: maybe NumPy is faster, but with a poor distribution. This is why we'll try different sample sizes and test which one is actually more randomic at different sizes. Moreover, the way randomness is generated internally can vary significantly between libraries. Some may rely on deterministic algorithms that are fast but exhibit patterns over large sequences, while others might prioritize statistical quality over speed."
        )

    logger.minipage_context.set_hfill()

    logger.minipage_context.set_width(0.6)
    with logger.minipage_context:
        fig, ax = plt.subplots(2, 1)

        ax[0].plot(
            [i + 1 for i in range(20)],
            results2["Python data"][4],
            color="blue",
            label="Python",
        )
        ax[0].plot(
            [i + 1 for i in range(20)],
            results2["NumPy data"][4],
            color="red",
            label="NumPy",
        )

        ax[0].tick_params(axis="both", which="major", labelsize=14)

        ax[0].set_xlabel("Samples", fontsize=18)
        ax[0].set_ylabel(r"Random value", fontsize=18)

        ax[0].legend(fontsize=14)

        ax[1].plot(
            [i + 1 for i in range(500)],
            results2["Python data"][5],
            color="blue",
            label="Python",
        )
        ax[1].plot(
            [i + 1 for i in range(500)],
            results2["NumPy data"][5],
            color="red",
            label="NumPy",
        )

        ax[1].tick_params(axis="both", which="major", labelsize=14)

        ax[1].set_xlabel("Samples size", fontsize=18)
        ax[1].set_ylabel(r"Timings [$\mu$s]", fontsize=18)

        ax[1].legend(fontsize=14)

        logger.write_plot(
            fig,
            caption="Here we can see the distribution at a) 20 samples and b) 500 samples. They look randomic!",
            size=r"width=0.8\linewidth",
            label="b",
        )

    logger.close_document()

    logger.compile_into_pdf()

    logger.send_report_by_email(config_path="credentials.ini")