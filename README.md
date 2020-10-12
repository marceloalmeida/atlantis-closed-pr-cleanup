# Atlantis closed PR's cleanup

## Motivation

At the moment [Atlantis](https://www.runatlantis.io/) doesn't have the mechanism do delete from disk the closed PR's. This script will cleanup from disk all PR's in `closed` state

## Usage
```sh
(set -o allexport; source .env; set +o allexport; python main.py )
```

## Notes
 * Only implemented support for Github
