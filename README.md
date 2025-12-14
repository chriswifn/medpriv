# Data Privacy

Anonymize data using k-anonymity and epsilon-differential privacy.

## Usage
```bash
usage: medpriv [-h] [-e] [-i] [-c CONFIG]

Process data for k-Anonymity or Epsilon-Differential Privacy.

options:
  -h, --help            show this help message and exit
  -e, --example-config  Print an example configuration file
  -i, --init-config     Initialize a sample configuration file
  -c CONFIG, --config CONFIG
                        Path to the configuration file. Anonymizes using the method
                        specified in the configuration file.
```

## Documentation
Use
```bash
sphinx-build -b html source/ build/
```
in the docs directory.
