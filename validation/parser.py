#!/usr/bin/env python

# dna-wvalue portal parser: metadata() reads the macro, parse() the wvalue.txt
# table that Run::EndOfRun appends after every /run/beamOn (one energy per run):
# energy (eV), mean number of ionisations per event and its standard deviation,
# w value = energy / mean number of ionisations (eV) and its standard deviation
# (eV). The run writes no row if no ionisation occurred.
#
# Electrons only, as in the Geant4 example. There is no reference here: the
# plots are compared between Geant4 versions.
import math
import os

from geantval import energy_mev, getJSON, one_command

TEST = "dna-wvalue"
PHYSLISTS = {"dna", "dna_opt1", "dna_opt2", "dna_opt3", "dna_opt4", "dna_opt5", "dna_opt6",
             "dna_opt7"}

# wvalue.txt columns after the energy: (observable, y axis, mean column, standard deviation column).
QUANTITIES = (("w value", "w, eV", 3, 4),
              ("number of ionisations", "mean number of ionisations per event", 1, 2))


def energy_scan(commands):
    """Energy (MeV) and number of events of every /run/beamOn, in macro order."""
    energies, events = [], []
    energy = None
    for command, value in commands:
        if command == "/gun/energy":
            energy = energy_mev(value)
        elif command == "/run/beamOn":
            n = int(value)
            if energy is None or n < 2:
                raise ValueError("Each /run/beamOn needs an explicit /gun/energy before it "
                                 "and at least 2 events")
            energies.append(energy)
            events.append(n)
    if not energies:
        raise ValueError("No /run/beamOn in the macro")
    return energies, events


def metadata(commands):
    physlist = one_command(commands, "/w/phys/addPhysics")
    if physlist not in PHYSLISTS:
        # The application silently keeps its default for an unknown name.
        raise ValueError("Unknown physics constructor %r (expected one of %s)"
                         % (physlist, ", ".join(sorted(PHYSLISTS))))
    if one_command(commands, "/w/det/setMat") != "G4_WATER":
        raise ValueError("This validation expects /w/det/setMat G4_WATER")
    particle = one_command(commands, "/gun/particle")
    if particle != "e-":
        raise ValueError("This validation is for electrons only, not %r" % particle)
    energies, events = energy_scan(commands)
    return {"TEST": TEST, "PHYSLIST": physlist, "PARTICLE": particle,
            "TRACKING_CUT": one_command(commands, "/w/det/setTrackingCut"),
            "ENERGIES": energies, "NEVENTS": events}


def read_table(path, expected_energies):
    """Rows of wvalue.txt, checked against the energies of the macro."""
    rows = []
    with open(path) as table:
        for line in table:
            if line.strip():
                rows.append([float(v) for v in line.split()])
    if len(rows) != len(expected_energies):
        raise ValueError("wvalue.txt has %d rows, expected %d (one per /run/beamOn; a run "
                         "without any ionisation writes none)" % (len(rows), len(expected_energies)))
    for row, energy in zip(rows, expected_energies):
        if len(row) != 5:
            raise ValueError("Expected 5 columns in wvalue.txt, got %r" % row)
        if not math.isclose(row[0] * 1e-6, energy, rel_tol=1e-5):
            raise ValueError("wvalue.txt energy %g eV does not match the macro (%g MeV)"
                             % (row[0], energy))
    return rows


def parse(job):
    rows = read_table(os.path.join(job["path"], "wvalue.txt"), job["ENERGIES"])
    energies = job["ENERGIES"]
    parameters = [{"names": "tracking cut", "values": job["TRACKING_CUT"]}]

    for name, y_axis, mean, rms in QUANTITIES:
        errors = [row[rms] / math.sqrt(n) for row, n in zip(rows, job["NEVENTS"])]
        yield getJSON(job, "chart",
                      mctool_name="GEANT4",
                      mctool_model=job["PHYSLIST"],
                      observableName=name,
                      targetName="water",
                      beamParticle=job["PARTICLE"],
                      beamEnergies=energies,
                      secondaryParticle="None",
                      parameters=parameters,
                      title="%s of e- in liquid water" % name.capitalize(),
                      xAxisName="E, MeV",
                      yAxisName=y_axis,
                      xValues=energies,
                      yValues=[row[mean] for row in rows],
                      yStatErrorsPlus=errors,
                      yStatErrorsMinus=errors)
