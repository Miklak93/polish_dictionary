#!/usr/bin/env python3
from source import ArgumentParser, Dictionary, WikitionaryReaderException, make_filters


if __name__ == "__main__":
    try:
        args = ArgumentParser().parse_args()
        dictionary = Dictionary()

        if args.command == "make":
            dictionary.make(
                include_redirects=args.include_redirects,
                progress_every=args.progress_every,
            )

        elif args.command == "search":
            results = dictionary.search(
                make_filters(
                    regex=args.regex,
                    types=args.types,
                    min_letters=args.min_letters,
                    max_letters=args.max_letters,
                    min_syllables=args.min_syllables,
                    max_syllables=args.max_syllables,
                )
            )
            for record in results:
                print(record["word"])
            print(f"Found {len(results)} matching words.")

    except WikitionaryReaderException as e:
        print(f"Error: {e}")
