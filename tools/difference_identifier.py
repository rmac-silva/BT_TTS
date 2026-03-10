from __future__ import annotations

from pathlib import Path


def _split_columns(line: str) -> list[str] | None:
	if "|" not in line:
		return None
	parts = [part.strip() for part in line.split("|")]
	if len(parts) < 3:
		return None
	return parts


def _extract_id(line: str) -> str | None:
	parts = _split_columns(line)
	if parts is None:
		return None
	raw_id = parts[0].strip()
	while raw_id.startswith("!#"):
		raw_id = raw_id[2:].lstrip()
	return raw_id if raw_id else None


def _find_next_index(lines: list[str], start: int, wanted_id: str) -> int | None:
	for idx in range(start, len(lines)):
		current_id = _extract_id(lines[idx])
		if current_id == wanted_id:
			return idx
	return None


def _extract_second_column(line: str) -> str | None:
	parts = _split_columns(line)
	if parts is None:
		return None
	if len(parts) < 2:
		return None
	return parts[1].strip()


def compare_ids(source_path: Path, target_path: Path, lookahead: int = 10) -> None:
	source_lines = source_path.read_text(encoding="utf-8").splitlines()
	target_lines = target_path.read_text(encoding="utf-8").splitlines()

	max_lines = max(len(source_lines), len(target_lines))
	for idx in range(max_lines):
		source_line = source_lines[idx] if idx < len(source_lines) else ""
		target_line = target_lines[idx] if idx < len(target_lines) else ""
		source_id = _extract_id(source_line)
		target_id = _extract_id(target_line)

		if source_id == target_id:
			continue

		print("Mismatch detected:")
		print(f"  Line {idx + 1} source ID: {source_id}")
		print(f"  Line {idx + 1} target ID: {target_id}")

		if source_id and target_id:
			source_next = _find_next_index(target_lines, idx + 1, source_id)
			target_next = _find_next_index(source_lines, idx + 1, target_id)

			source_delta = (
				source_next - idx if source_next is not None else None
			)
			target_delta = (
				target_next - idx if target_next is not None else None
			)

			if source_delta is not None and source_delta <= lookahead:
				print(
					"  Hint: source ID appears later in target; target may have an extra line."
				)
			elif target_delta is not None and target_delta <= lookahead:
				print(
					"  Hint: target ID appears later in source; source may have an extra line."
				)
			else:
				print("  Hint: IDs diverge and do not realign soon.")
		else:
			print("  Hint: one side is missing an ID on this line.")

		break


def compare_second_column(source_path: Path, target_path: Path) -> None:
	source_lines = source_path.read_text(encoding="utf-8").splitlines()
	target_lines = target_path.read_text(encoding="utf-8").splitlines()

	max_lines = max(len(source_lines), len(target_lines))
	for idx in range(max_lines):
		source_line = source_lines[idx] if idx < len(source_lines) else ""
		target_line = target_lines[idx] if idx < len(target_lines) else ""
		source_id = _extract_id(source_line)
		target_id = _extract_id(target_line)

		if source_id != target_id:
			print("ID mismatch before text comparison:")
			print(f"  Line {idx + 1} source ID: {source_id}")
			print(f"  Line {idx + 1} target ID: {target_id}")
			response = input("Press Enter to continue, or type 'q' to quit: ").strip()
			if response.lower() == "q":
				return
			continue

		source_text = _extract_second_column(source_line)
		target_text = _extract_second_column(target_line)
		if source_text == target_text:
			continue

		print("Second column mismatch:")
		print(f"  Line {idx + 1} ID: {source_id}")
		print(f"  Source: {source_text}")
		print(f"  Target: {target_text}")
		response = input("Press Enter to continue, or type 'q' to quit: ").strip()
		if response.lower() == "q":
			return


if __name__ == "__main__":
	base_dir = Path(__file__).resolve().parent
	source = base_dir / "transcripts" / "mission_control_bladewolf.csv"
	target = base_dir / "transcripts" / "mission_control_transcript_en.csv"

	compare_second_column(source, target)
