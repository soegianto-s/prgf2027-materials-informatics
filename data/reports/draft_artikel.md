# DRAFT ARTIKEL (IMRaD)
**Target jurnal:** Computational Materials Science (Elsevier, Gold Open Access — sesuai RAB)
**Status:** draft v1.0 — 4 November 2026

---

# An Artificial-Intelligence-Based Materials Informatics Framework for the Discovery of Calcium Phosphate Biomaterials as Candidate Scaffolds for Bone Tissue Engineering

## Abstract

Bone defects caused by trauma, degenerative disease, and congenital abnormalities remain a
major clinical challenge. Calcium phosphate biomaterials are attractive scaffold candidates
owing to their biocompatibility, bioactivity, and osteoconductivity, yet conventional
trial-and-error discovery is time- and cost-intensive. Here we present an end-to-end
Materials Informatics framework that integrates five open material databases
(Materials Project, AFLOW, Crystallography Open Database, PubChem, OQMD) and artificial
intelligence to accelerate the discovery of calcium phosphate biomaterials.
A curated dataset of 2,605 entries spanning 903 unique compositions was assembled and
audited. Physicochemical descriptors (Ca/P ratio, electronegativity, valence electron
concentration, molecular weight, cell volume, density) were engineered, and multicollinearity
was controlled (r > 0.85, VIF). Predictive models trained with composition-grouped
cross-validation achieved R² = 0.84 for formation energy (SVR) and R² = 0.92 for density
(Random Forest); a scaffold-suitability classifier reached F1 = 0.90.
Multi-objective ranking (TOPSIS and VIKOR under three weighting scenarios, plus
Shannon-entropy sensitivity) identified carbonated apatite, fluorapatite, octacalcium
phosphate, tetracalcium phosphate, and hydroxyapatite as the top candidates — in agreement
with clinically established bone-graft materials. Computed densities and formation energies
of reference phases deviate from experimental values by less than 3%, validating the
framework. SHAP analysis reveals oxygen fraction and density as dominant descriptors of
thermodynamic stability. The framework is fully replicable (versioned dataset, checksums,
open tooling) and provides a foundation for an AI-assisted biomaterial discovery platform.

**Keywords:** materials informatics; machine learning; calcium phosphate; bone tissue
engineering; scaffold; multi-criteria decision making

## 1. Introduction

[Paragraf 1: beban klinis defek tulang + peran scaffold — rujuk ref [1–3] proposal]
[Paragraf 2: 3D printing & optimasi berbasis ML — ref [4–7]]
[Paragraf 3: AI dalam sains material & biomaterial — ref [8–17]]
[Paragraf 4: research gap — integrasi seluruh tahapan dalam satu kerangka; penelitian
pendahuluan penulis [18]]
[Paragraf 5: kontribusi makalah ini — (i) kerangka end-to-end yang dapat direplikasi,
(ii) dataset teraudit 2.605 entri/903 komposisi, (iii) model prediktif tervalidasi
GroupKFold, (iv) pemeringkatan multiobjektif dengan analisis sensitivitas, (v) validasi
terhadap data eksperimen.]

## 2. Methods

### 2.1 Data acquisition
Lima basis data terbuka (Tabel 1): Materials Project (API, CC-BY 4.0), AFLOW (AFLUX REST),
COD (CC0), PubChem (PUG REST), OQMD (oqmdapi). Sistem kimia: Ca–P, Ca–P–O, Ca–P–O–H,
Ca–P–O–C (karbonat), Ca–P–O–F (fluor). Metadata versi/tanggal akses/lisensi dicatat
(lihat Supplementary: laporan_akuisisi.md).

### 2.2 Preprocessing & descriptors
QC nilai tak-fisik; deteksi pencilan (IQR×3, z>4, Isolation Forest silang) dengan keputusan
per kasus tercatat — tanpa penghapusan otomatis. Deskriptor: Ca/P, elektronegativitas
rata-rata, VEC, berat molekul, volume sel, densitas (eksperimen/komputasi; densitas teoritis
M·Z/(N_A·V) untuk entri COD). Redundansi dieliminasi (|r| > 0.85; VIF > 10).

### 2.3 Machine learning
Subset komputasional (Materials Project + AFLOW, n = 291). Regresi: Random Forest,
XGBoost, Gradient Boosting, SVR. Klasifikasi kelayakan scaffold: Eform ≤ −2.5 eV/atom,
Ca/P 1.2–2.1, densitas 0.5–4.5 g/cm³. Validasi silang **GroupKFold berbasis kelompok
komposisi** (polimorf dalam satu fold) — mencegah kebocoran data. Metrik: R², RMSE, MAE,
akurasi, F1. Seleksi fitur: RF importance + RFE.

### 2.4 Multi-criteria decision making
Kriteria: C1 stabilitas (Eform), C2 densitas → 2.0 g/cm³, C3 Ca/P → 1.67, C4 modulus
Young → 15 GPa (imputasi median bila tidak tersedia — tercatat), C5 bandgap, C6 skor
kelayakan model. TOPSIS + VIKOR (v = 0.5) dengan tiga skenario bobot (berimbang;
stabilitas-dominan; mekanik-dominan) + pembobotan entropi Shannon (kriteria lengkap saja)
sebagai uji sensitivitas.

### 2.5 Interpretability & validation
SHAP (TreeExplainer) + permutation importance; dependence plots. Validasi material rujukan
(HAp, β-TCP, α-TCP, FAp) terhadap nilai eksperimen (densitas, parameter kisi, entalpi
pembentukan standar). Struktur Top-5 disiapkan untuk validasi DFT (input Quantum ESPRESSO).

## 3. Results

### 3.1 Dataset
2.605 entri / 903 komposisi unik (Materials Project 57; AFLOW 234; COD 2.304; PubChem 13;
OQMD berjalan). Kelengkapan: volume sel & spacegroup 99,5%; energi 11,2% (sumber
komputasional); modulus elastik 0,3% (n = 9). [Tabel 1 + Fig. audit]

### 3.2 Descriptor & design space
Korelasi |r|>0.85: EN_avg–EN_diff (0.889), EN_avg–VEC (0.902) → disisihkan; VIF EN_avg 24.
PCA: PC1+PC2 = 61,1%. Klaster K-Means k = 5 (silhouette 0.552; ARI antar-seed 1.000),
konsisten dengan klaster hierarkis Ward (ARI 0.907). HDBSCAN: 17 klaster + 1.266 noise.
Bias sumber terdeteksi (fraksi tetangga sesumber k=5 = 0.94) → mitigasi subset komputasional
+ GroupKFold. [Fig. 2–4]

### 3.3 Predictive models
[Table 2 — semua metrik; highlight:] SVR Eform R² = 0.843 (RMSE 0.435 eV/atom);
RF densitas R² = 0.916 (RMSE 0.132 g/cm³); klasifikasi akurasi 0.975, F1 0.90.
Bandgap tidak dapat diprediksi dari deskriptor komposisi (R² < 0) — keputusan: tanpa
imputasi.

### 3.4 Multi-objective ranking
Top 15 (dedup polimorf): karbonat apatit (Ca10P6CO27), fluorapatit, OCP, TTCP, HAp, ...
Sensitivitas: korelasi Spearman peringkat entropi vs manual = 0.974. [Table 3]

### 3.5 Interpretability & validation
SHAP: fraksi O dan densitas dominan untuk Eform; volume sel + EN_avg untuk densitas;
korelasi SHAP Ca/P–densitas +0.57. Validasi eksperimen: selisih densitas ≤ 2,9%
(HAp +0,6%; FAp −2,7%; karbonat apatit +1,8%; TTCP −2,4%…+1,0%); Eform HAp −3,22 vs
−3,15 eV/atom (entalpi standar); FAp −3,42 vs −3,39. Validasi kisi α/β-TCP (COD):
β-TCP a = 10,449 Å (+0,1%), c = 37,448 Å (+0,2%), ρ = 3,04 (−1,1%); α-TCP (Mathew
1977) a = 12,887 Å (−0,03%), b = 27,28 Å (0,0%), c = 15,219 Å (−0,01%), ρ = 2,86
(+0,1%). Catatan: AFLOW melaporkan TCP sebagai R-3m (ρ +10,9% — overbinding GGA).
[Fig. 5–7]

## 4. Discussion

- Kerangka menghasilkan kandidat yang konsisten dengan pengetahuan klinis (karbonat
  apatit, FAp, OCP, TTCP) → validasi tidak langsung terhadap basis pengetahuan.
- Keterbatasan: ketersediaan modulus elastik komputasional (n = 9) → prioritas validasi
  DFT/MD (input disiapkan); bandgap tidak terprediksi; bias sumber dikelola via subset
  komputasional; ketimpangan kelas klasifikasi (15% layak, recall 0.82).
- Implikasi: framework dapat direplikasi (requirements.txt, run_all, checksum dataset)
  dan siap diperluas ke sistem material lain (roadmap platform AI-assisted discovery AMREC).

## 5. Conclusion

[Ringkasan kontribusi + rekomendasi eksperimental untuk Top-5.]

## Supplementary

- Laporan per tahap: data/reports/*.md; dataset: data/processed/*.csv (checksum di
  data/versions/); skrip: scripts/ (MIT-style, penggunaan akademik).

## References (kerangka awal — lengkapi urutan Vancouver)

1. Farag MM. J Mater Sci. 2023;58:527–558.
2. Prem Ananth K, Jayram ND. Ann 3D Print Med. 2024;13:100141.
3. Vaiani L, et al. J Funct Biomater. 2023;14:146.
4. Omigbodun FT, et al. Biomimetics. 2024;9(10):587.
5. Zhu S, et al. ACS Appl Mater Interfaces. 2025;17(2):2791–2813.
6. Hou B, et al. npj Biol Phys Mech. 2026;3(1).
7. Vasudev H, Mehta A. Glob Clin Eng J. 2026;8(2):35–56.
8. Martelli A, et al. Polymers (Basel). 2025;17(19):2668.
9. Logeshwaran A, et al. ACS Biomater Sci Eng. 2024;10(2):677–696.
10. Gokcekuyu Y, et al. Appl Sci. 2024;14:6590.
11–17. [AI dalam farmasi/biomaterial — ref proposal 11–17]
18. Soelistiono S. Int J Appl Pharm Life Sci. 2026. (penelitian pendahuluan)
+ [tambahan: Jain A, et al. APL Mater. 2013 (MP); Curtarolo S, et al. Comput Mater Sci.
2012 (AFLOW); Kirklin S, et al. npj Comput Mater. 2015 (OQMD); Gražulis S, et al. J Appl
Cryst. 2009 (COD); Dorozhkin SV (kalsium fosfat); Lundberg S, Lee S-I (SHAP)]
