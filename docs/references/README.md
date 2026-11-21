# References

| File | Contents | Source |
|---|---|---|
| `morgan-jones-valve-amplifiers-3rd-edition.pdf` | Morgan Jones, *Valve Amplifiers*, 3rd edition, Newnes/Elsevier. Complete downloaded PDF, 633 pages, 5.8 MB. | <https://milas.spb.ru/~kmg/files/literature/Morgan_Jones_Valve_Amplifiers_Third_Edition.pdf> |
| Online reference (no local book file) | Morgan Jones, *Valve Amplifiers*, 4th edition, Newnes/Elsevier, ISBN 9780080966403. Full text has not been accessed or read. | [Online edition and preview](https://www.oreilly.com/library/view/valve-amplifiers-4th/9780080966403/); [publisher](https://shop.elsevier.com/books/valve-amplifiers/jones/978-0-08-096640-3) |
| `mullard-circuits-for-audio-amplifiers.pdf` | Mullard Ltd, *Circuits for Audio Amplifiers* (1963 reprint of the 1960 second edition), complete, 121 pages. Page images re-encoded at 150 dpi (28 MB, from 53 MB). | <https://www.worldradiohistory.com/BOOKSHELF-ARH/Technology/Technology-General/Mullard%20Circuits%20For%20Audio%20Amplifiers.pdf> |
| `mullard-circuits-for-audio-amplifiers-ch1-3-5-6.pdf` | Mullard Ltd, *Circuits for Audio Amplifiers* (1963 reprint of the 1960 second edition), extract: Table 1 of chapter 1 (page 7 of the scan) and pages 19 to 50 (chapter 3 *High-quality Amplification*, chapter 4, chapter 5 *Twenty-watt Amplifier* (5-20), chapter 6 *Ten-watt Amplifier* (5-10)). Reduced to greyscale, 110 dpi. | Full scan, 121 pages: <https://archive.org/details/19400164MullardCircuitsForAudioAmplifiers> |
| `gec-approach-to-af-amplifier-design-1957.pdf` | G.E.C. Valve and Electronics Dept., *An Approach to Audio Frequency Amplifier Design* (1957), complete: the KT88 30 W, 50 W and 100 W fixed-bias ultra-linear amplifiers are in chapters 4 and 5. | <https://archive.org/details/An_Approach_to_Audio_Frequency_Amplifier_Design_G.E._Valve-Electronics_Dept._195> |
| `radiotron-designers-handbook-4th-ch5-7-12-14-21-30-31.pdf` | F. Langford-Smith (ed.), *Radiotron Designer's Handbook*, 4th edition (1952/1953), extract: title pages, chapter list, chapter 5 *Transformers and Iron-cored Inductors*, 7 *Negative Feedback*, 12 *Audio Frequency Voltage Amplifiers* (phase splitters), 13 *Audio Frequency Power Amplifiers*, 14 *Fidelity and Distortion*, 21 *The Network between the Power Valve and the Loudspeaker*, 30 *Rectification*, 31 *Filtering and Hum*. 360 of 1538 pages, images re-encoded at 150 dpi. | Full scan: <https://worldradiohistory.com/BOOKSHELF-ARH/Technology/Technology-Handbooks/Radiotron-Designer's-Handbook-4th-1953.pdf> |
| `valley-wallman-vacuum-tube-amplifiers-1948-ch9-10.pdf` | G. E. Valley and H. Wallman (eds.), *Vacuum Tube Amplifiers*, MIT Radiation Laboratory Series vol. 18 (1948), extract: title pages, contents, chapter 9 *Low-frequency Amplifiers with Stabilized Gain* and chapter 10 *Low-frequency Feedback Amplifiers* (loop gain and phase, stability margins, shaping the loop at both ends of the band). Images re-encoded at 150 dpi. | Full scan: <https://worldradiohistory.com/BOOKSHELF-ARH/Tube-Technology/Vacuum-Tube-Amplifiers-Valley-Wallman-1948-761-pages.pdf> |
| `williamson-amplifier-1952.pdf` | D. T. N. Williamson, *The Williamson Amplifier* (Iliffe, 1952), complete: the *Design for a High-quality Amplifier* articles reprinted from Wireless World (1947 and 1949), including the output transformer specification and why its bandwidth sets the feedback that can be applied. | <https://archive.org/details/The_Williamson_Amplifier_-_Williamson_1952> |

## What they say about the driver

Mullard, chapter 3 (page 24 of the book): two EL34 need about 2 x 25 V rms of drive, two EL84 about 2 x 10 V rms, and an ECC83 cathode-coupled phase splitter direct coupled to the input stage can supply both. Its grids sit at 70 to 80 V on the anode of the input stage; too high an anode voltage leaves too little bias and gives grid-current distortion on peaks.

Operating points read from the DC tables (V, measured with an Avometer 8):

| | 5-20 (2 x EL34) | 5-10 (2 x EL84) |
|---|---|---|
| Input stage | EF86, anode 85 | EF86, anode 61 |
| ECC83 grids / cathodes / anodes | 85 / 87.5 / 325 | 61 / 63.5 / 200 |
| ECC83 anode loads, tail | 180k, 82k | 100k, 68k |
| Output valve grid resistors | 470k (cathode bias) | 820k (cathode bias) |
| Feedback | 30 dB | 26 dB |

G.E.C. never drives the KT88 straight from the phase splitter. Each KT88 design has a push-pull voltage amplifier between them:

| Design | Input and phase splitter | Driver | Output |
|---|---|---|---|
| 30 W ultra-linear (fig. 4-4) | B65/6SN7: input stage direct coupled to a triode phase splitter | B65/6SN7 push-pull | 2 x KT88 (or KT66), cathode bias |
| 50 W ultra-linear (fig. 5-2) | B339/12AX7 floating paraphase | B329/12AU7 push-pull, with balance control | 2 x KT88 |
| 100 W fixed bias ultra-linear (fig. 5-8) | L63/6J5 phase splitter | B65/6SN7 push-pull | 2 x KT88 at 560 V, fixed bias |
