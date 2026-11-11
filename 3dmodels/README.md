# Valve 3D models

KT88.step and ECC83.step are original simplified visualization models with smooth glass shells, approximate internal electrodes, pins, and socket bodies. KT88.wrl and ECC83.wrl are matching KiCad viewer models with transparent glass; geometry uses KiCad's 0.1-inch VRML units. Paired STEP files use millimetres and are available for mechanical exports (enable substitution of similarly named STEP models when exporting from KiCad). Valves.sc contains editable SolidCraft source for both models, at their own origins; export only the relevant bodies for each valve.

References:
- KT88 nominal 52 mm diameter, 117 mm total including pins: https://partsconnexion.com/product_images/downloads/TUBEGL-67225.pdf
- ECC83 maximum 22.2 mm diameter, 49.2 mm body, 55.6 mm including pins: https://frank.pocnet.net/sheets/010/e/ECC83.pdf

Both are visual approximations, not manufacturer-certified mechanical models. Base shape, electrodes and socket bodies are illustrative. Tube seating plane Z=0; socket/pins extend downward, glass upward.

Board offsets, in KiCad model coordinates:
- V3/V4 KT88: (-7.62, +7.62, +10) mm. Assumed socket seat 10 mm above PCB.
- V1/V2 ECC83: (-7.62, +5.08, +6.4) mm. Assumed socket seat 6.4 mm above PCB.

Adjust socket height for the actual hardware. Tube pins and PCB socket terminals use different pitch circles.
