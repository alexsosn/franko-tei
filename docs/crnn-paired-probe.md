# Two specialized CRNN models on fixed Franko line images

Issue #20; experimental. This applies two independently trained, open PyTorch
CRNN-CTC models to the **exact same** two Kraken-derived physical line crops
on III/130 and V/100. No model is selected as a winner, no auto-correction,
no language identification, and no text is marked verified.

Sources and code are version-addressed:

- Franko scan images: user-supplied codex/page-assets at
  e871f32537e81f81896f6ce9a6658aba667db9c5.
- Polyscriptor inference source:
  achimrabus/polyscriptor at 7994ccadc537c59b0b90eb25b66dfa5d54976d6d.
- Model repositories: achimrabus/crnn-ctc-prosta-mova and
  achimrabus/crnn-ctc-church-slavonic. The GitHub Actions workflow resolves
  their frozen Hugging Face repository SHAs from successful scan run 43036416973 (40 hex chars), downloads
  best_model.pt and symbols.txt from **those revisions**, and records SHA256
  of both artifacts in the output. Outputs include SHA256 for upstream
  inference script, native line JSON, candidate layout report, page image
  and exact PNG crop bytes. The local code executes a trusted, locally
  supplied upstream inference script; never run arbitrary unreviewed code
  or third-party checkpoints with sensitive files/credentials exposed.

The baseline crop uses the Kraken line polygon's bounding rectangle with
horizontal 5px and vertical 8px margin (configurable in Python), preserving
the original pixels. It is **not a verified optimal crop**; superscripts
and marginal signs can be clipped. A true scholarly pipeline needs independent
line segmentation/reading-order verification and possibly baseline-based
warped extraction; this experiment does not claim that yet.

To run (after installing Pillow, PyTorch, torchvision and a pinned
Polyscriptor inference file):

    franko-crnn-probe --images images --volume 3 \
      --layout geometry/vol3/vol3-page-00130-kraken-layout.json \
      --model-specs local/model-specs.json \
      --inference-script upstream/inference_pylaia_native.py \
      --start-line 2 --max-lines 2 --output local/crnn-vol3.json

Model spec JSON maps a name to local checkpoint and symbol paths, upstream
repository and resolved 40-digit Git revision. Reports are arrays of per-model
OCR candidates; they never embed/distribute the cropped image or weights.

**Cautions:** model-internal CTC confidence is not calibrated across models,
and neither model was trained on Franko's 1896–1910 typefaces. Published
validation CER does NOT establish accuracy here. The true next gate is
a held-out, independently checked transcription of line images and
critical-glyph error analysis on ѣ/ѳ/ѵ/ѡ, titla and superscripts. Mixed
Ukrainian/German/Greek/Latin lines additionally require appropriate
script-specific models; Church Slavonic models alone cannot handle them.

The pinned `inference_pylaia_native.py` imports the adjacent upstream `htr_engine_base.py` at module import to populate model presets. The workflow fetches **both** files from the same fixed Polyscriptor Git commit. The runner temporarily adds their directory to the Python module path while loading the upstream code, then removes it. Both SHA256 values are recorded in the model outputs. This requirement was found by an actual GitHub Actions run; do not treat a single-file import as sufficient.
