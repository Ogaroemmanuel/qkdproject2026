import json
import tempfile
import sqlite3
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.security.controller import run_simulation
from backend.quantum.state_trace import build_state_trace
from backend.database import db_manager


class SampledExperimentTests(unittest.TestCase):
    def test_exact_channel_math(self):
        for bits in ("00", "01", "10", "11"):
            for eve in (False, True):
                for noise in (0, .03, .3):
                    state = build_state_trace(bits, eve, noise)["decoded"]
                    error = sum(sum(a != b for a, b in zip(bits, format(i, '02b')))*p
                                for i, p in enumerate(state["probabilities"])) / 2
                    self.assertAlmostEqual(error, .25+noise/3 if eve else 2*noise/3)
                    self.assertAlmostEqual(sum(state["probabilities"]), 1)

    def test_clean_complete_and_disjoint(self):
        result = run_simulation(8, False, 512, noise_probability=0, seed=42)
        self.assertEqual(result["status"], "Within limit")
        self.assertTrue(result["payload_released"])
        self.assertEqual(result["completed_batches"], result["planned_batches"])
        self.assertEqual(result["error_bits"], 0)
        for pair in result["pair_results"]:
            self.assertEqual(len(pair["test_indices"]), 256)
            self.assertEqual(sum(pair["retained_counts"].values()), 256)
            self.assertEqual(sum(sum(c.values()) for c in pair["test_counts"].values()), 256)
            self.assertEqual(set(pair["test_inputs"]), set(map(str, pair["test_indices"])))
            self.assertGreater(len(set(pair["test_inputs"].values())), 1)

    def test_eve_stops_later_batches_and_replays(self):
        result = run_simulation(32, True, 1024, seed=42)
        self.assertEqual(result["status"], "Rejected")
        self.assertTrue(result["kill_switch_triggered"])
        self.assertFalse(result["payload_released"])
        self.assertLess(result["completed_batches"], result["planned_batches"])
        self.assertGreater(result["untransmitted_bits"], 0)
        self.assertEqual(result, run_simulation(**result["configuration"], seed=result["seed"]))

    def test_noise_can_reject_without_eve(self):
        result = run_simulation(16, False, 2048, noise_probability=.3, seed=7)
        self.assertEqual(result["status"], "Rejected")
        self.assertTrue(result["kill_switch_triggered"])

    def test_small_sample_withholds_candidates(self):
        result = run_simulation(8, False, 2, noise_probability=0, seed=7)
        self.assertEqual(result["status"], "Inconclusive")
        self.assertFalse(result["payload_released"])
        self.assertFalse(result["kill_switch_triggered"])

    def test_database_round_trip_and_legacy_shape(self):
        result = run_simulation(8, False, 128, noise_probability=0, seed=7)
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(db_manager, "DB_NAME", str(Path(directory)/"test.db")):
                db_manager.init_db()
                db_manager.init_db()
                run_id = db_manager.log_simulation(8,128,False,result["qber_value"],
                    result["threshold"],result["status"],result["kill_switch_triggered"],
                    model_version=result["model_version"],result=result)
                self.assertEqual(db_manager.fetch_run_result(run_id), json.loads(json.dumps(result)))
                self.assertEqual(len(db_manager.fetch_logs()[0]), 10)

    def test_additive_migration_keeps_old_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            filename = str(Path(directory)/"legacy.db")
            connection = sqlite3.connect(filename)
            connection.execute("CREATE TABLE simulation_runs (run_id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT,key_size INTEGER,num_shots INTEGER,eve_active BOOLEAN,qber_value REAL,threshold_used REAL,status TEXT,kill_switch BOOLEAN)")
            connection.execute("INSERT INTO simulation_runs VALUES (1,'old',8,128,0,0,11,'Secure',0)")
            connection.commit()
            connection.close()
            with patch.object(db_manager, "DB_NAME", filename):
                db_manager.init_db()
                old = db_manager.fetch_logs()[0]
                self.assertEqual(old[7], "Secure")
                self.assertEqual(old[-1], "legacy-before-bit-order-fix")
                self.assertIsNone(db_manager.fetch_run_result(1))

    def test_invalid_configuration(self):
        for config in ({"key_size":3}, {"num_shots":0}, {"noise_probability":float('nan')},
                       {"test_fraction":1}, {"seed":-1}, {"eve_active":"false"}):
            with self.assertRaises(ValueError):
                run_simulation(**config)

    def test_save_repairs_missing_detail_table(self):
        with tempfile.TemporaryDirectory() as directory:
            filename = str(Path(directory)/"existing.db")
            with patch.object(db_manager, "DB_NAME", filename):
                db_manager.init_db()
                connection = sqlite3.connect(filename)
                connection.execute("DROP TABLE simulation_details")
                connection.commit()
                connection.close()
                self.assertIsNone(db_manager.fetch_run_result(1))
                run_id = db_manager.log_simulation(8,128,False,0,11,"Within limit",False,
                    model_version="sampled-channel-v3",result={"marker":"retained"})
                self.assertEqual(db_manager.fetch_run_result(run_id), {"marker":"retained"})


if __name__ == "__main__":
    unittest.main()
