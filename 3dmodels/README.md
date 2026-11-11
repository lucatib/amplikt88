# Valve 3D models

KT88.step and ECC83.step are original simplified visualization models with smooth glass shells, approximate internal electrodes, pins, and socket bodies. KT88.wrl and ECC83.wrl are matching KiCad viewer models with transparent glass; geometry uses KiCad's 0.1-inch VRML units. Paired STEP files use millimetres and are available for mechanical exports (enable substitution of similarly named STEP models when exporting from KiCad). Valves.sc contains editable SolidCraft source for both models, at their own origins; export only the relevant bodies for each valve.

References:
- KT88 nominal 52 mm diameter, 117 mm total including pins: https://partsconnexion.com/product_images/downloads/TUBEGL-67225.pdf
- ECC83 maximum 22.2 mm diameter, 49.2 mm body, 55.6 mm including pins: https://frank.pocnet.net/sheets/010/e/ECC83.pdf

Both are visual approximations, not manufacturer-certified mechanical models. Base shape, electrodes and socket bodies are illustrative. Tube seating plane Z=0; socket/pins extend downward, glass upward.

KT88_JJ.wrl and KT88_JJ.stpz are the JJ Electronic KT88 from a SketchUp model on 3D Warehouse ("JJ TESLA KT88 Vacuum tube"), exported as STL in 0.1 mm units and converted here: scaled to mm, base bottom at Z=0, 52.6 mm across and 113.4 mm tall (JJ data sheet: 52 mm and 110 mm max seated, 125 mm with pins; the pins are not in the model). The VRML keeps every triangle, with the base below 16 mm opaque and the glass above it transparent amber; the STEP is a faceted mesh reduced to 25 102 triangles by 0.5 mm vertex clustering, gzipped (KiCad reads .stpz). Check the 3D Warehouse licence before redistributing it.

The model is the valve in its socket. The socket's eight contacts (2.3 mm bores for the 2.36 mm KT88 pins) sit on a 16.0 mm circle at 22.5 deg + n x 45 deg in the model's frame, with the key at 180 deg; the model's base bottom is Z=0. KT88_JJ_socket_tails.wrl/.step add the socket's solder tails, 2 mm across, from 5.5 mm inside the socket to 4 mm under the board top (1.6 mm board plus 2.4 mm), already in the footprint's frame.

Board offsets, in KiCad model coordinates:
- V3/V4 KT88 (KT88_JJ.wrl): offset 0, rotation Z -112.5 deg, so the key falls between pads 1 and 8 and each contact over its pad; the socket bottom on the PCB. KT88_JJ_socket_tails.wrl: offset 0, no rotation.
- V1/V2 ECC83: (-7.62, +5.08, +6.4) mm. Assumed socket seat 6.4 mm above PCB.

Adjust socket height for the actual hardware. Tube pins and PCB socket terminals use different pitch circles.
