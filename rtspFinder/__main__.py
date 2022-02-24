import time
import asyncio
from sys import stderr
from pathlib import Path

from rtspFinder.modules import utils, workers
from rtspFinder.modules.logs_handler import logs
from rtspFinder.modules.cli.inputs import parser, port


start_datetime = time.strftime("%Y.%m.%d-%H.%M.%S")
REPORT_FOLDER = Path.cwd() / "reports" / start_datetime
PICS_FOLDER = REPORT_FOLDER / "pics"
utils.RESULT_FILE = REPORT_FOLDER / "result.txt"
utils.HTML_FILE = REPORT_FOLDER / "index.html"


def main():
    args = parser.parse_args()

    logs.set_quiet(args.quiet)

    if args.only_onvif and args.no_onvif:
        print("--only-onvif and --no-onvif are not allowed together.", file=stderr)
        quit()

    # set up Folders and files
    if not args.no_report:
        utils.create_folder(PICS_FOLDER)
        utils.create_file(utils.RESULT_FILE)
        utils.generate_html(utils.HTML_FILE)

    asyncio.run(
        workers.main(
            args.ip,
            port(args.rtsp_port),
            port(args.onvif_port),
            args.username,
            args.password,
            utils.load_paths(args.routes),
            args.timeout,
            stop_all_workers_after_first_success=not args.dont_stop,
            only_onvif=args.only_onvif,
            no_onvif=args.no_onvif,
            dont_store=args.no_report
        )
    )


if __name__ == "__main__":
    main()
