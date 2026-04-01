from lama_cleaner.parse_args import parse_args
from lama_cleaner.runtime_settings import configure_cache_settings


def entry_point():
    args = parse_args()
    args.cache_settings = configure_cache_settings(args.cache_dir)
    from lama_cleaner.server import main

    main(args)
