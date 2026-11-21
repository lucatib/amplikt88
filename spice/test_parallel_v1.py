import unittest
import numpy as np
from parallel_v1 import harmonics, variant


class Measurements(unittest.TestCase):
    def test_nonuniform_samples_with_dc_and_known_distortion(self):
        # Adaptive-solver-like time grid; amplitude must not depend on point density.
        u = np.linspace(0, 1, 100001)
        t = 0.02 * u**1.7
        y = 3 + 2*np.sin(2*np.pi*1000*t) + .02*np.cos(4*np.pi*1000*t)
        result = harmonics(t, y, 1000, 8)
        self.assertAlmostEqual(result['fundamental_peak_V'], 2, places=4)
        self.assertAlmostEqual(result['thd_pct'], 1, places=3)

    def test_requires_complete_window(self):
        with self.assertRaises(ValueError):
            harmonics(np.array([0, .001]), np.array([0, 0]), 20, 8)

    def test_parallel_connections_and_scaled_feedback(self):
        net = ('XV1 V1_A V1_G V1_K spare GND GND ECC83\n'
               'R3 B_V1 V1_A 470k\nR4 V1_K GND 1.5k\n'
               'R22 B_DRV B_V1 150k\nR9 V1_K OT_S_HI 180k\n'
               'C6 V1_K OT_S_HI 12p\nC12 B_V1 GND 22u\n')
        changed = variant(net, 'parallel_scaled')
        self.assertIn('XV1 V1_A V1_G V1_K V1_A V1_G V1_K ECC83', changed)
        self.assertIn('R3 B_V1 V1_A 235k', changed)
        self.assertIn('R4 V1_K GND 750', changed)
        self.assertIn('R9 V1_K OT_S_HI 90k', changed)
        self.assertIn('C6 V1_K OT_S_HI 24p', changed)
        self.assertEqual(variant(net, 'baseline'), net)

    def test_cascode_stacks_spare_on_active_section(self):
        net = ('XV1 V1_A V1_G V1_K spare GND GND ECC83\n'
               'R4 V1_K GND 1.5k\nR9 V1_K OT_S_HI 180k\nC6 V1_K OT_S_HI 12p\n')
        changed = variant(net, 'cascode')
        self.assertIn('XV1 V1_MID V1_G V1_K V1_A CAS_G V1_MID ECC83', changed)
        self.assertIn('R4 V1_K GND 680', changed)
        self.assertIn('R9 V1_K OT_S_HI 82k', changed)
        self.assertIn('C6 V1_K OT_S_HI 27p', changed)
        self.assertIn('CCAS CAS_G GND', changed)


class Variants(unittest.TestCase):
    NET = ('XV1 V1_A V1_G V1_K spare GND GND ECC83\nR5 V1_A LTP_G1 1k\n'
           'C15 LTP_A1 LTP_STEP 330p\nR26 LTP_STEP LTP_A2 10k\n')

    def test_follower_drives_ltp_grid_from_spare_section(self):
        changed = variant(self.NET, 'follower')
        self.assertIn('XV1 V1_A V1_G V1_K B_CF CF_G LTP_G1 ECC83', changed)
        self.assertIn('R5 V1_A CF_G 1k', changed)
        self.assertIn('RCFK LTP_G1 GND 91k', changed)
        self.assertIn('C15 ', changed)

    def test_lag_moves_compensation_from_v2_anodes_to_v1_anode(self):
        for name in ['baseline_lag', 'follower_lag']:
            changed = variant(self.NET, name)
            self.assertNotIn('C15 ', changed)
            self.assertNotIn('R26 ', changed)
            self.assertIn('RSTEP V1_A NSTEP', changed)

    def test_parallel_lag_scales_and_moves_compensation(self):
        net = self.NET + ('R3 B_V1 V1_A 470k\nR4 V1_K GND 1.5k\nR22 B_DRV B_V1 150k\n'
                          'R9 V1_K OT_S_HI 180k\nC6 V1_K OT_S_HI 12p\nC12 B_V1 GND 22u\n')
        changed = variant(net, 'parallel_scaled_lag_damped')
        self.assertIn('XV1 V1_A V1_G V1_K V1_A V1_G V1_K ECC83', changed)
        self.assertIn('R3 B_V1 V1_A 235k', changed)
        self.assertNotIn('C15 ', changed)
        self.assertIn('RSTEP V1_A NSTEP 5.6k', changed)

    def test_ccs_tail_replaces_r8_with_spare_section(self):
        net = self.NET + ('R8 LTP_K GND 39k\nR6 B_DRV LTP_A1 100k\nR7 B_DRV LTP_A2 100k\n'
                          'R3 B_V1 V1_A 470k\nR4 V1_K GND 1.5k\nR9 V1_K OT_S_HI 180k\n'
                          'C6 V1_K OT_S_HI 12p\n')
        low = variant(net, 'ccs_low_lag')
        self.assertIn('XV1 V1_A V1_G V1_K LTP_K CCS_G CCS_K ECC83', low)
        self.assertNotIn('R8 ', low)
        self.assertIn('R6 B_DRV LTP_A1 150k', low)
        self.assertIn('RCCSK CCS_K GND 4.7k', low)
        self.assertNotIn('C15 ', low)
        raised = variant(net, 'ccs_raised')
        self.assertIn('R3 B_V1 V1_A 362k', raised)
        self.assertIn('R9 V1_K OT_S_HI 318k', raised)
        self.assertIn('C15 ', raised)


if __name__ == '__main__':
    unittest.main()
