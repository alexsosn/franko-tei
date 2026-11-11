# Kraken PP-OCRv6 multilingual model: real-image trial

Open model: [PP-OCRv6 medium (Apache 2.0)](https://huggingface.co/small-models-for-glam/kraken-ppocrv6-medium), mirrored byte-identically from [Zenodo 21788410](https://zenodo.org/records/21788410). Kraken engine pinned to 7.1.0 for initial smoke. Pretrained model's published benchmark on other datasets is **not** an accuracy estimate for Franko.

The smoke is run on four real source images from `codex/page-assets`:

- V/100: Church Slavonic orthography and titla, severe existing OCR errors
- III/130: Church Slavonic with Greek/Ukrainian printed apparatus
- I/20: Ukrainian editorial prose with Ancient Greek, German and Latin in lines
- IV/100: editorial Ukrainian, no embedded PDF OCR in volume IV

It uses Kraken neural baseline segmentation `segment -bl` and line recognition `ocr -m`. Raw ALTO XML is archived for every page, including line geometry; `candidates.jsonl` is machine-only, `ocr_unchecked`. Image and model weights SHA-256 are checked. **No scan images or model weights are rehosted in workflow artifacts.**

To reproduce on an image checkout:

```bash
python -m pip install -e .
python -m pip install 'kraken==7.1.0' 'huggingface_hub>=0.34,<2'
hf download small-models-for-glam/kraken-ppocrv6-medium medium.safetensors --local-dir local/models
python -m franko_tei.kraken_trial --images-root images \
  --pages 5:100,3:130,1:20,4:100 \
  --model local/models/medium.safetensors \
  --model-id small-models-for-glam/kraken-ppocrv6-medium \
  --output-dir local/kraken
```

Do not run all 2,337 pages until the four samples have been inspected against source images and a stratified independently reviewed ground truth has been prepared. The Kraken model may be better for Church Slavonic but can expand abbreviations, conflate scripts, and hallucinate text; text must remain diplomatic and image-verifiable. Layout segmentation must be independently evaluated, not collapsed into CER.
