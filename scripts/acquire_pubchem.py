"""Akuisisi PubChem PUG REST untuk senyawa kalsium fosfat kunci."""
import time

import pandas as pd
import requests

from common import RAW, get, save_json

BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound"

NAMES = [
    ("Hydroxyapatite", "HAp"),
    ("Calcium phosphate", "TCP"),
    ("beta-Tricalcium phosphate", "b-TCP"),
    ("alpha-Tricalcium phosphate", "a-TCP"),
    ("Calcium hydrogen phosphate dihydrate", "DCPD"),
    ("Calcium hydrogen phosphate", "DCPA-monetit"),
    ("Octacalcium phosphate", "OCP"),
    ("Tetracalcium phosphate", "TTCP"),
    ("Monocalcium phosphate", "MCPM"),
    ("Fluorapatite", "FAp"),
    ("Carbonate apatite", "CAp"),
    ("Calcium pyrophosphate", "CPP"),
    ("Whitlockite", "WH"),
]

PROPS = (
    "MolecularFormula,MolecularWeight,ExactMass,IUPACName,CanonicalSMILES,IsomericSMILES,"
    "XLogP,HBondDonorCount,HBondAcceptorCount,Complexity,Charge"
)


def main():
    rows, raws = [], {}
    for name, tag in NAMES:
        url = f"{BASE}/name/{requests.utils.quote(name)}/property/{PROPS}/JSON"
        r = get(url, tries=3, pause=4, timeout=60)
        if r is None:
            print(f"  {tag}: gagal")
            continue
        try:
            d = r.json()
        except Exception:
            print(f"  {tag}: bukan JSON")
            continue
        props = d.get("PropertyTable", {}).get("Properties", [])
        if not props:
            print(f"  {tag}: kosong")
            continue
        p = props[0]
        p["_query"] = f"name:{name}"
        p["_tag"] = tag
        rows.append(p)
        raws[tag] = d
        print(f"  {tag}: CID {p.get('CID')} {p.get('MolecularFormula')}")
        time.sleep(0.4)

    # perluasan: enumerasi senyawa bertagar "calcium phosphate"
    try:
        r = get(f"{BASE}/name/calcium%20phosphate/cids/JSON?name_type=word&max=100", tries=3, pause=4, timeout=60)
        if r is not None:
            cids = r.json().get("IdentifierList", {}).get("CID", [])
            print(f"  pencarian 'calcium phosphate': {len(cids)} CID")
            for i in range(0, len(cids), 50):
                chunk = cids[i : i + 50]
                rr = get(f"{BASE}/cid/{','.join(map(str, chunk))}/property/{PROPS}/JSON", tries=3, pause=4, timeout=90)
                if rr is None:
                    continue
                props = rr.json().get("PropertyTable", {}).get("Properties", [])
                for p in props:
                    p["_query"] = "search:calcium phosphate"
                    p["_tag"] = ""
                rows.extend(props)
                time.sleep(0.4)
            raws["search_calcium_phosphate"] = {"cid": cids}
    except Exception as e:
        print("  perluasan pencarian gagal:", e)

    save_json(RAW / "pubchem" / "pubchem_cap_raw.json", raws)
    if rows:
        df = pd.DataFrame(rows).drop_duplicates(subset="CID")
        df.to_csv(RAW / "pubchem" / "pubchem_cap.csv", index=False)
    save_json(
        RAW / "pubchem" / "_metadata.json",
        {
            "sumber": "PubChem PUG REST",
            "tanggal_akses": time.strftime("%Y-%m-%d %H:%M:%S"),
            "lisensi": "public domain (data NCBI)",
            "jumlah": len(rows),
        },
    )
    print("PubChem selesai. baris:", len(rows))


if __name__ == "__main__":
    main()
