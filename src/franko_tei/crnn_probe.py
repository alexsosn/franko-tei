"""Experimental CRNN comparison on identical, image-anchored Kraken line crops.

This never emits verified text. It does not normalize historical glyphs,
infer manuscript witnesses, or choose a winning model.
"""
import argparse
from hashlib import sha256
import importlib.util
import io
import json
import sys
from pathlib import Path
import re
import tempfile

from .ocr_candidates import _digest, _get_page_image, _read_manifest

SHA256 = re.compile(r"[0-9a-f]{64}\Z")
GIT_REV = re.compile(r"[0-9a-f]{40}\Z")


def _validate_layout(root, volume, layout):
    if not isinstance(layout, dict) or layout.get("status") != "segmentation_unchecked":
        raise ValueError("expected an unverified Kraken layout")
    if layout.get("volume") != str(volume):
        raise ValueError("layout volume mismatch")
    page = layout.get("scan_page")
    if not isinstance(page, int) or page < 1:
        raise ValueError("invalid layout page")
    manifest = _read_manifest(root, volume)
    if page > manifest["page_count"]:
        raise ValueError("layout page beyond manifest")
    if layout["source_pdf_sha256_claimed_by_manifest"] != manifest["source_sha256"]:
        raise ValueError("layout PDF provenance disagrees with manifest")
    entry = manifest["pages"][page - 1]
    if entry.get("scan_page") != page:
        raise ValueError("manifest scan index mismatch")
    image, image_sha = _get_page_image(root, volume, entry)
    if image_sha != layout.get("source_image_sha256"):
        raise ValueError("layout image checksum mismatch")
    if layout.get("source_image_path") != str(image.relative_to(root)):
        raise ValueError("layout image path mismatch")
    if layout.get("image_width") != entry.get("width") or layout.get("image_height") != entry.get("height"):
        raise ValueError("layout image dimensions mismatch")
    lines = layout.get("lines")
    if not isinstance(lines, list) or layout.get("line_count") != len(lines):
        raise ValueError("layout line coverage mismatch")
    layout_sha = layout.get("native_kraken_json_sha256")
    if not isinstance(layout_sha, str) or not SHA256.fullmatch(layout_sha):
        raise ValueError("layout native JSON fingerprint missing")
    ids = [line.get("candidate_line_id") for line in lines if isinstance(line, dict)]
    if len(ids) != len(lines) or len(set(ids)) != len(ids):
        raise ValueError("layout line identities missing or duplicated")
    return image, entry, image_sha, page, lines


def _crop_from_line(image, line, margin_x=5, margin_y=8):
    """Geometry-only rectangle with margins; superscripts still require visual audit."""
    from PIL import Image
    if not isinstance(margin_x, int) or not 0 <= margin_x <= 30:
        raise ValueError("invalid horizontal margin")
    if not isinstance(margin_y, int) or not 0 <= margin_y <= 40:
        raise ValueError("invalid vertical margin")
    rect = line.get("bbox_xywh")
    if not isinstance(rect, list) or len(rect) != 4:
        raise ValueError("line bbox missing")
    if any(not isinstance(n, (int, float)) or isinstance(n, bool) for n in rect):
        raise ValueError("invalid bbox coordinate type")
    from math import isfinite, floor, ceil
    if any(not isfinite(n) for n in rect):
        raise ValueError("bbox coordinates must be finite")
    x, y, width, height = rect
    if x < 0 or y < 0 or width <= 0 or height <= 0:
        raise ValueError("negative or degenerate bbox")
    if x + width > image.width or y + height > image.height:
        raise ValueError("bbox exceeds image")
    bounds = [
        max(0, floor(x) - margin_x), max(0, floor(y) - margin_y),
        min(image.width, ceil(x + width) + margin_x),
        min(image.height, ceil(y + height) + margin_y),
    ]
    crop = image.crop(tuple(bounds)).convert("RGB")
    buffer = io.BytesIO()
    crop.save(buffer, format="PNG")
    digest = sha256(buffer.getvalue()).hexdigest()
    return crop, bounds, digest


def _load_engine(inference_path, checkpoint, symbols):
    """Execute only explicitly supplied, locally vetted upstream inference code."""
    spec = importlib.util.spec_from_file_location("polyscriptor_native_inference", inference_path)
    if not spec or not spec.loader:
        raise RuntimeError("could not load pinned Polyscriptor inference module")
    module = importlib.util.module_from_spec(spec)
    # The pinned upstream inference file imports sibling htr_engine_base.py to
    # register optional model presets. Keep that import local and temporary.
    upstream_dir = str(inference_path.parent.resolve())
    sys.path.insert(0, upstream_dir)
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(upstream_dir)
    return module.PyLaiaInference(checkpoint_path=str(checkpoint), syms_path=str(symbols), device="cpu")


def _check_model_specs(models):
    if not isinstance(models, dict) or not models:
        raise ValueError("at least one model is required")
    result = {}
    for name, item in sorted(models.items()):
        if not re.fullmatch(r"[a-z][a-z0-9-]{1,35}", name):
            raise ValueError("invalid model name")
        if not isinstance(item, dict) or any(k not in item for k in ("checkpoint", "symbols", "repo", "revision")):
            raise ValueError("incomplete model specification")
        if not isinstance(item["revision"], str) or not GIT_REV.fullmatch(item["revision"]):
            raise ValueError("pin each model to its resolved Hugging Face commit SHA")
        for field in ("checkpoint", "symbols"):
            p = Path(item[field])
            if not p.is_file() or p.is_symlink() or p.stat().st_size == 0:
                raise ValueError(f"missing or unsafe {field} for model {name}")
        result[name] = {
            "checkpoint": Path(item["checkpoint"]),
            "symbols": Path(item["symbols"]),
            "repo": item["repo"], "revision": item["revision"],
            "checkpoint_sha256": _digest(Path(item["checkpoint"])),
            "symbols_sha256": _digest(Path(item["symbols"])),
        }
    return result


def probe(images_root, volume, layout_path, model_specs, inference_path,
          output, start_line=2, max_lines=4, margin_x=5, margin_y=8):
    """Same exact crop PNG bytes for all model candidates; report source+weights."""
    images_root, layout_path, output = map(Path, (images_root, layout_path, output))
    if not isinstance(start_line, int) or start_line < 1 or not 1 <= max_lines <= 12:
        raise ValueError("line selection must be bounded (start>=1, max 1–12)")
    if output.exists():
        raise FileExistsError("refusing to overwrite OCR candidates")
    if not inference_path.is_file() or inference_path.is_symlink():
        raise ValueError("missing or unsafe inference source")
    companion_path = inference_path.parent / "htr_engine_base.py"
    if not companion_path.is_file() or companion_path.is_symlink():
        raise ValueError("missing pinned Polyscriptor htr_engine_base.py companion")
    inference_sha = _digest(inference_path)
    companion_sha = _digest(companion_path)
    layout_sha = _digest(layout_path)
    layout = json.loads(layout_path.read_text(encoding="utf-8"))
    image_path, page_entry, image_sha, page, lines = _validate_layout(images_root, volume, layout)
    selected = lines[start_line-1:start_line-1+max_lines]
    if not selected or len(selected) != max_lines:
        raise ValueError("requested lines unavailable")
    models = _check_model_specs(model_specs)

    from PIL import Image
    with Image.open(image_path) as scanned:
        if scanned.size != (layout["image_width"], layout["image_height"]):
            raise ValueError("actual image dimensions mismatch")
        crops = []
        for line in selected:
            crop, bounds, digest = _crop_from_line(scanned, line, margin_x, margin_y)
            crops.append((line, crop, bounds, digest))
    records = []
    for name, spec in models.items():
        engine = _load_engine(inference_path, spec["checkpoint"], spec["symbols"])
        for line, crop, bounds, digest in crops:
            # Third-party recognizers may mutate their PIL input while preprocessing.
            # Pass an independent copy so the next model sees identical source pixels.
            predicted = engine.transcribe(crop.copy())
            if (not isinstance(predicted, (tuple, list)) or len(predicted) != 2
                    or not isinstance(predicted[0], str)):
                raise RuntimeError(f"model {name} returned invalid recognition result")
            text, confidence = predicted
            if not text.strip():
                raise RuntimeError(f"model {name} returned empty line; likely inference failure")
            # Raw confidence is not calibrated across architectures or languages.
            if not isinstance(confidence, (float, int)) or not 0 <= confidence <= 1:
                raise RuntimeError(f"model {name} returned invalid confidence")
            records.append({
                "status": "ocr_unchecked", "engine": "polyscriptor-crnn-ctc",
                "upstream_inference_sha256": inference_sha,
                "upstream_companion_sha256": companion_sha,
                "model_name": name, "model_repo": spec["repo"], "model_revision": spec["revision"],
                "model_checkpoint_sha256": spec["checkpoint_sha256"],
                "model_symbols_sha256": spec["symbols_sha256"],
                "volume": str(volume), "scan_page": page, "printed_page": page_entry.get("printed_page"),
                "source_image_sha256": image_sha,
                "source_pdf_sha256_claimed_by_manifest": layout["source_pdf_sha256_claimed_by_manifest"],
                "kraken_layout_report_sha256": layout_sha,
                "kraken_native_json_sha256": layout["native_kraken_json_sha256"],
                "candidate_line_id": line["candidate_line_id"],
                "bbox_crop_xyxy": bounds, "crop_png_sha256": digest,
                "margin_px": [margin_x, margin_y],
                "transcription": text, "model_internal_confidence": confidence,
                "caution": "Unverified source-line OCR. Crop/line segmentation not manually audited. Confidence not cross-model comparable.",
            })
    if _digest(image_path) != image_sha or _digest(layout_path) != layout_sha:
        raise ValueError("source image/layout changed during inference")
    if _digest(inference_path) != inference_sha or _digest(companion_path) != companion_sha:
        raise ValueError("inference code changed during run")
    for name, spec in models.items():
        if _digest(spec["checkpoint"]) != spec["checkpoint_sha256"] or _digest(spec["symbols"]) != spec["symbols_sha256"]:
            raise ValueError(f"model files changed during run: {name}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".crnn-probe-", dir=output.parent) as tmp:
        stage = Path(tmp) / "ocr.json"
        stage.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        stage.rename(output)
    return records


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", required=True, type=Path)
    parser.add_argument("--volume", required=True, choices=[str(i) for i in range(1, 6)])
    parser.add_argument("--layout", required=True, type=Path)
    parser.add_argument("--model-specs", required=True, type=Path,
                        help="JSON map of model names to pinned local checkpoint/symbol paths + repo/revision")
    parser.add_argument("--inference-script", required=True, type=Path,
                        help="Pinned, locally vetted Polyscriptor inference source")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--start-line", type=int, default=2)
    parser.add_argument("--max-lines", type=int, default=4)
    args = parser.parse_args(argv)
    try:
        records = probe(args.images, args.volume, args.layout,
                        json.loads(args.model_specs.read_text(encoding="utf-8")),
                        args.inference_script, args.output,
                        start_line=args.start_line, max_lines=args.max_lines)
    except (ValueError, RuntimeError, OSError) as exc:
        parser.error(str(exc))
    print(f"Wrote {len(records)} UNVERIFIED CRNN line candidates to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
