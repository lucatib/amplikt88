# Valve 3D models

KT88.step and ECC83.step are original simplified visualization models with smooth glass shells, approximate internal electrodes, pins, and socket bodies. KT88.wrl and ECC83.wrl are matching KiCad viewer models with transparent glass; geometry uses KiCad's 0.1-inch VRML units. Paired STEP files use millimetres and are available for mechanical exports (enable substitution of similarly named STEP models when exporting from KiCad). Valves.sc contains editable SolidCraft source for both models, at their own origins; export only the relevant bodies for each valve.

References:
- KT88 nominal 52 mm diameter, 117 mm total including pins: https://partsconnexion.com/product_images/downloads/TUBEGL-67225.pdf
- ECC83 maximum 22.2 mm diameter, 49.2 mm body, 55.6 mm including pins: https://frank.pocnet.net/sheets/010/e/ECC83.pdf

Both are visual approximations, not manufacturer-certified mechanical models. Base shape, electrodes and socket bodies are illustrative. Tube seating plane Z=0; socket/pins extend downward, glass upward.

KT88_JJ.wrl and KT88_JJ.stpz are the JJ Electronic KT88 from a SketchUp model on 3D Warehouse ("JJ TESLA KT88 Vacuum tube"), exported as STL in 0.1 mm units and converted here: scaled to mm, base bottom at Z=0, 52.6 mm across and 113.4 mm tall (JJ data sheet: 52 mm and 110 mm max seated, 125 mm with pins; the pins are not in the model). The VRML keeps every triangle, with the base below 16 mm opaque and the glass above it transparent amber; the STEP is a faceted mesh reduced to 25 102 triangles by 0.5 mm vertex clustering, gzipped (KiCad reads .stpz). Check the 3D Warehouse licence before redistributing it.

The model is the valve plugged into its socket. The valve's pins go into the socket's eight contacts (2.3 mm bores on a 16 mm circle); the socket's own solder tabs are what goes through the PCB: eight curved blades 0.5 mm thick, 0.9 mm wide at the tip and 2.9 mm where they leave the body, on a 25.3 mm circle at 22.5 deg + n x 45 deg in the model's frame, straight from the model's Z=0 to 4.6 mm, then bent in towards the socket body. The socket key is at 180 deg.

ECC83_RFT.wrl / ECC83_RFT.stpz are an ECC83 (RFT) from a STEP render file on GrabCAD ("ECC83 RFT double triode"), with the table and backdrop of the render scene removed: glass 21.5 mm across, glass bottom at Z=-9.6 mm, 1.0 mm pins on the 11.9 mm noval circle. The VRML is the mesh reduced by 0.1 mm vertex clustering (130 716 triangles), with transparent glass, the getter flash on top, grey electrodes and bright pins; the STEP is reduced further (0.4 mm, 31 637 triangles) and gzipped. Noval_PCB_socket.step is a noval PCB socket from GrabCAD ("Vacuum tube PCB socket"), used as it is: body 18 mm across from Z=1.98 to 11.9 mm, nine flat tabs 1.55 x 0.2 mm on a 17.4 mm circle at 18 + n x 36 deg with the gap at 270 deg, the same frame as the tube. Check both GrabCAD licences before redistributing them.

Board offsets, in KiCad model coordinates:
- V3/V4 KT88 (KT88_JJ.wrl): offset (0, 0, -4.6) mm, rotation Z -112.5 deg: the key falls between pads 1 and 8, each tab in its hole, the straight part of the tabs across the 1.6 mm board and 3 mm out underneath.
- V1/V2 ECC83 (Valve_Noval_ECC83): Noval_PCB_socket.step at (0, 0, -1.976) mm, so its body sits on the board and the tabs come 3 mm out underneath; ECC83_RFT.wrl at (0, 0, +19.524) mm, the glass on the socket top, the pins in its contacts. No rotation: pad 1 is next to the gap, like tab and pin 1 in the models.

Adjust socket height for the actual hardware. Tube pins and PCB socket terminals use different pitch circles.
