# dna-wvalue

**w value of electrons in liquid water** (mean energy spent per ionisation) with
the Geant4-DNA track-structure physics. Built on the Geant4 example
[`extended/medical/dna/wvalue`](https://github.com/Geant4/geant4/tree/v11.3.2/examples/extended/medical/dna/wvalue).

---

## 🔬 What this test does

Mono-energetic electrons start at the centre of a 1 m radius sphere of
`G4_WATER`, in a random direction, and the whole shower is tracked down to the
9 eV tracking cut. For each energy the application writes to `wvalue.txt` the
mean number of ionisations per event and the w value, w = E / mean number of
ionisations, with their standard deviations over the events.

| Macro | Particle | Physics | Energies | Events per energy |
| --- | --- | --- | --- | --- |
| `e-_dna_opt4.mac` | e- | `dna_opt4` | 12 eV – 10 keV | 1000 |

`validation/parser.py` publishes two plots (x: energy in MeV, error: standard
deviation / √N): the w value (eV) and the mean number of ionisations. There is no
reference data: the plots are compared between Geant4 versions. Physics
constructor and tracking cut are those of the example's `wvalue.in`.

## Import notes

- `main.cc`, `include/`, `src/` are `wvalue.cc`, `include/` and `src/` of the
  Geant4 v11.3.2 example (the version of the default base image), unchanged.
- `macro/wvalue.in` and `macro/histo.in` are the example's macros, kept for
  reference; the validation macro is `e-_dna_opt4.mac`, listed in
  `validation/config.json`. `docs/geant4-example-README.txt` is the example's
  README. `plot.C` is replaced by `validation/parser.py`.
- `macro/unit.mac` runs one 1 keV electron on every push.

For the CI, the validation flow and running everything locally, see the
[template README](https://github.com/G4Med-test/template#readme).

References for this example: Med. Phys. 42 (2015) 3870–3876, and the Geant4-DNA
publications Med. Phys. 51 (2024) 5873–5889; Med. Phys. 45 (2018) e722–e739;
Phys. Med. 31 (2015) 861–874; Med. Phys. 37 (2010) 4692–4708; Int. J. Model.
Simul. Sci. Comput. 1 (2010) 157–178.
