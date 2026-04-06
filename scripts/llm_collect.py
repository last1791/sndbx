"""
LLM Daily Collector
Umístění: sndbx/scripts/llm_collect.py
Výstup:   sndbx/data/llm_data.jsonl
"""

import json
import time
import datetime
import os
import requests
from pathlib import Path

# scripts/ je o úroveň níž než kořen repozitáře → parents[1]
OUTPUT = Path(__file__).resolve().parents[1] / "data" / "llm_data.jsonl"

MODELS = [
    {"hf_id": "deepseek-ai/DeepSeek-V3",               "name": "DeepSeek V3",        "developer": "DeepSeek",   "parameters_b": 671, "architecture": "MoE (Mixture of Experts)", "license": "open-source"},
    {"hf_id": "deepseek-ai/DeepSeek-R1",               "name": "DeepSeek R1",        "developer": "DeepSeek",   "parameters_b": 671, "architecture": "MoE – reasoning",          "license": "open-source"},
    {"hf_id": "meta-llama/Llama-4-Maverick-17B-128E",  "name": "Llama 4 Maverick",   "developer": "Meta",       "parameters_b": 400, "architecture": "MoE",                      "license": "open-weight"},
    {"hf_id": "Qwen/Qwen3-235B-A22B",                  "name": "Qwen3 235B A22B",    "developer": "Alibaba",    "parameters_b": 235, "architecture": "MoE",                      "license": "open-weight"},
    {"hf_id": "mistralai/Mixtral-8x22B-Instruct-v0.1", "name": "Mixtral 8x22B",      "developer": "Mistral AI", "parameters_b": 141, "architecture": "MoE",                      "license": "open-weight"},
    {"hf_id": "mistralai/Mistral-Large-Instruct-2411",  "name": "Mistral Large 2411", "developer": "Mistral AI", "parameters_b": 123, "architecture": "Dense Transformer",        "license": "proprietary"},
    {"hf_id": "meta-llama/Llama-4-Scout-17B-16E",      "name": "Llama 4 Scout",      "developer": "Meta",       "parameters_b": 109, "architecture": "MoE",                      "license": "open-weight"},
    {"hf_id": "meta-llama/Llama-3.3-70B-Instruct",     "name": "Llama 3.3 70B",      "developer": "Meta",       "parameters_b":  70, "architecture": "Dense Transformer",        "license": "open-weight"},
    {"hf_id": "Qwen/Qwen3-32B",                        "name": "Qwen3 32B",          "developer": "Alibaba",    "parameters_b":  32, "architecture": "Dense Transformer",        "license": "open-weight"},
    {"hf_id": "google/gemma-3-27b-it",                 "name": "Gemma 3 27B",        "developer": "Google",     "parameters_b":  27, "architecture": "Dense Transformer",        "license": "open-weight"},
]

HF_API   = "https://huggingface.co/api/models"
HF_TOKEN = os.environ.get("HF_TOKEN", "")


def fetch_hf(hf_id: str) -> dict:
    headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}
    try:
        r = requests.get(f"{HF_API}/{hf_id}", headers=headers, timeout=15)
        r.raise_for_status()
        d = r.json()
        return {
            "downloads_alltime": d.get("downloads"),
            "likes":             d.get("likes"),
            "last_modified":     d.get("lastModified"),
            "pipeline_tag":      d.get("pipeline_tag"),
            "fetch_ok":          True,
            "fetch_error":       None,
        }
    except Exception as e:
        return {
            "downloads_alltime": None, "likes": None,
            "last_modified": None, "pipeline_tag": None,
            "fetch_ok": False, "fetch_error": str(e),
        }


def group_share(records):
    vals  = {r["hf_id"]: (r["_hf"]["downloads_alltime"] or 0) for r in records}
    total = sum(vals.values())
    if total == 0:
        return {k: None for k in vals}
    return {k: round(v / total * 100, 4) for k, v in vals.items()}


def main():
    now  = datetime.datetime.utcnow()
    ts   = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    date = now.strftime("%Y-%m-%d")

    print(f"[→] {ts}  |  výstup: {OUTPUT}")
    print(f"    {'Model':<28} {'Status':>8}  {'Stažení':>12}  {'Likes':>7}")
    print("    " + "─" * 60)

    records = []
    for m in MODELS:
        hf = fetch_hf(m["hf_id"])
        time.sleep(0.4)
        status = "✓" if hf["fetch_ok"] else "✗"
        dl = hf["downloads_alltime"] if hf["downloads_alltime"] is not None else "–"
        lk = hf["likes"]             if hf["likes"]             is not None else "–"
        print(f"    {m['name']:<28} {status:>8}  {str(dl):>12}  {str(lk):>7}")
        records.append({**m, "_hf": hf})

    shares = group_share(records)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "a", encoding="utf-8") as f:
        for r in records:
            row = {
                "collected_at":   ts,
                "date":           date,
                "schema_version": "1.1",
                "hf_id":          r["hf_id"],
                "name":           r["name"],
                "developer":      r["developer"],
                "parameters_b":   r["parameters_b"],
                "architecture":   r["architecture"],
                "license":        r["license"],
                "popularity": {
                    "downloads_alltime": r["_hf"]["downloads_alltime"],
                    "likes":             r["_hf"]["likes"],
                    "last_modified":     r["_hf"]["last_modified"],
                    "pipeline_tag":      r["_hf"]["pipeline_tag"],
                    "group_share_pct":   shares.get(r["hf_id"]),
                    "fetch_ok":          r["_hf"]["fetch_ok"],
                    "fetch_error":       r["_hf"]["fetch_error"],
                },
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"\n[✓] Uloženo {len(records)} záznamů → {OUTPUT}")
    print(f"\n  {'#':<3} {'Model':<28} {'Param B':>8}  {'Podíl %':>8}  Architektura")
    print("  " + "─" * 65)
    for i, r in enumerate(sorted(records, key=lambda x: x["parameters_b"], reverse=True), 1):
        s = shares.get(r["hf_id"])
        s_str = f"{s:.2f}" if s is not None else "N/A"
        print(f"  {i:<3} {r['name']:<28} {r['parameters_b']:>8}  {s_str:>7}%  {r['architecture']}")


if __name__ == "__main__":
    main()
