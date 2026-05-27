import argparse
import csv
import logging
from pathlib import Path
from typing import Iterable, List, Optional

from downloader import HuabanDownloader


LOGGER = logging.getLogger("huaban_downloader")
KNOWN_ID_HEADERS = ("board_id", "id", "boardid")


def normalize_header(name: str) -> str:
    return name.strip().lower().replace("-", "_").replace(" ", "_")


def load_cookie(cookie_path: Path) -> str:
    if not cookie_path.exists():
        raise FileNotFoundError(f"cookie file not found: {cookie_path}")
    return cookie_path.read_text(encoding="utf-8").strip()


def unique(values: Iterable[str]) -> List[str]:
    seen = set()
    result = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def extract_board_ids(csv_path: Path, id_column: Optional[str] = None) -> List[str]:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = [row for row in csv.reader(f) if any(cell.strip() for cell in row)]

    if not rows:
        raise ValueError(f"csv file is empty: {csv_path}")

    if id_column:
        with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                raise ValueError(f"csv file has no header: {csv_path}")

            normalized_fieldnames = {
                normalize_header(field): field for field in reader.fieldnames if field
            }
            field = normalized_fieldnames.get(normalize_header(id_column))
            if not field:
                raise ValueError(
                    f"column '{id_column}' not found in csv header: {reader.fieldnames}"
                )

            return unique(
                row.get(field, "").strip()
                for row in reader
                if row.get(field, "").strip()
            )

    first_row = rows[0]
    normalized_first_row = {normalize_header(cell) for cell in first_row if cell.strip()}
    has_known_header = bool(normalized_first_row & KNOWN_ID_HEADERS)

    if has_known_header:
        with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                raise ValueError(f"csv file has no header: {csv_path}")

            normalized_fieldnames = {
                normalize_header(field): field for field in reader.fieldnames if field
            }
            field = next(
                (
                    normalized_fieldnames[name]
                    for name in KNOWN_ID_HEADERS
                    if name in normalized_fieldnames
                ),
                None,
            )
            if not field:
                raise ValueError(
                    "csv header detected, but no id column was found. "
                    "Use --id-column to specify the board id column."
                )

            return unique(
                row.get(field, "").strip()
                for row in reader
                if row.get(field, "").strip()
            )

    return unique(row[0].strip() for row in rows if row and row[0].strip())


def download_board(downloader: HuabanDownloader, board_id: str, cookie: str) -> int:
    board = downloader.get_board_info(board_id, cookie)
    pins = downloader.get_board_pins(board_id, cookie)
    save_dir = Path("huohuab") / str(board_id)
    save_dir.mkdir(parents=True, exist_ok=True)

    LOGGER.info(
        "board %s: %s, %s pins, saving to %s",
        board_id,
        board.get("title", ""),
        len(pins),
        save_dir,
    )

    success_count = 0
    for index, pin in enumerate(pins, 1):
        try:
            downloader.download_image(pin, str(save_dir))
            success_count += 1
            LOGGER.info("board %s: downloaded %s/%s", board_id, index, len(pins))
        except Exception as exc:
            LOGGER.error("board %s: failed to download pin %s: %s", board_id, index, exc)

    return success_count


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Download Huaban boards from a CSV file.")
    parser.add_argument("csv_path", help="CSV file containing board ids")
    parser.add_argument(
        "--cookie-path",
        required=True,
        help="Path to a local file that stores the Huaban cookie",
    )
    parser.add_argument(
        "--id-column",
        default=None,
        help="Optional CSV header name for the board id column",
    )
    return parser


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    parser = build_parser()
    args = parser.parse_args()

    csv_path = Path(args.csv_path)
    cookie_path = Path(args.cookie_path)

    if not csv_path.exists():
        raise FileNotFoundError(f"csv file not found: {csv_path}")

    cookie = load_cookie(cookie_path)
    board_ids = extract_board_ids(csv_path, args.id_column)

    if not board_ids:
        LOGGER.warning("no board ids found in %s", csv_path)
        return 1

    downloader = HuabanDownloader()
    failures = 0

    for board_id in board_ids:
        try:
            success_count = download_board(downloader, board_id, cookie)
            LOGGER.info("board %s: finished, downloaded %s images", board_id, success_count)
        except Exception as exc:
            failures += 1
            LOGGER.error("board %s: failed: %s", board_id, exc)

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
