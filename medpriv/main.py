import argparse
import medpriv.utils as utils
import medpriv.config as config
import medpriv.data_processing as dp
import medpriv.anonymize as anon


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Process data for k-Anonymity or Epsilon-Differential Privacy.")
    parser.add_argument("-e", "--example-config", action="store_true", help="Print an example configuration file")
    parser.add_argument("-i", "--init-config", action="store_true", help="Initialize a sample configuration file")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        help="Path to the configuration file. Anonymizes using the method specified in the configuration file.",
    )

    return parser.parse_args()


def main():
    """Main function to parse command line options."""
    args = parse_arguments()

    if args.example_config:
        example_config = config.KConfig(
            k=3,
            identifiers=["name"],
            quasiIdentifiers=["age", "gender"],
            inputFile=utils.File("input.csv"),
            outputFile=utils.File("output.csv"),
        )
        print(example_config.to_dict())

    if args.init_config:
        example_config = config.KConfig(
            k=3,
            identifiers=["name"],
            quasiIdentifiers=["age", "gender"],
            inputFile=utils.File("input.csv"),
            outputFile=utils.File("output.csv"),
        )
        loader = config.ConfigLoader(utils.File("config.json"))
        loader.init_config(example_config)

    if args.config:
        config_file = utils.File(args.config)
        loader = config.ConfigLoader(config_file)
        cfg = loader.load_config()

        csv_processor = dp.ProcessCsvData()
        facade = dp.FacadeProcess()
        facade.add_processor(csv_processor)

        if facade.can_process(cfg.inputFile):
            input_data = facade.process(cfg.inputFile)
            if hasattr(cfg, "k"):
                print("Preparing data...")
                data = dp.KAnonymityData(input_data, cfg.quasiIdentifiers, cfg.identifiers)
                anonymized = anon.KAnonymityAnonymizer(cfg.k, data)
                k_before = anonymized.compute_initial_k_anonymity()
                print("Anonymizing data...")
                anonymized.anonymize()
                anonymized_data = utils.concatenate_dataframes(anonymized.partitions)
                anonymized_data.to_csv(cfg.outputFile.name, index=False)
                k_after = anonymized.compute_anonymized_k_anonymity()
                print("Finished!")
                print(f"k before: {k_before}\nk after: {k_after}")
            else:
                data = dp.EpsilonData(input_data, cfg.quasiIdentifiers)
                anonymized = anon.EpsilonAnonymizer(cfg.epsilon, data)
                anonymized.anonymize()
                print(data.histogram)


if __name__ == "__main__":
    main()
